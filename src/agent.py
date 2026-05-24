import os
import sys
import json
from typing import List, Dict, Any
from openai import OpenAI

# Append current directory to path to ensure robust relative imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from schemas import AssistantResponse, ConversationSummary

# Initialize OpenAI client with the validated key
api_key = config.validate_config()
client = OpenAI(api_key=api_key)

# Recommended default model that is highly capable and supports native Pydantic structured outputs
DEFAULT_MODEL = "gpt-4o-mini"

def build_system_prompt(current_stage: str, lead_data: Dict[str, Any]) -> str:
    """
    Compiles the comprehensive system prompt for the customer support agent,
    injecting current stage details and any already-collected lead information.
    """
    lead_str = json.dumps(lead_data, indent=2) if lead_data else "None collected yet"
    
    return f"""You are a warm, professional, and compliant AI Customer Support Agent for "Bloom Aesthetics Clinic".
Your task is to assist the user through our 4-stage customer support pipeline: FAQ Answering, Lead Qualification, Escalation Handling, and Session Conclusion.

{config.SOP_GROUNDING_TEXT}

{config.STRICT_INSTRUCTIONS}

### CURRENT OPERATIONAL CONTEXT:
- **Active Stage**: {current_stage}
- **Lead Data Gathered So Far**: {lead_str}

### STAGE-SPECIFIC ACTIONS:
1. **faq**:
   - If the active stage is 'faq', answer patient questions about our business hours, services, pricing, booking, and cancellation rules.
   - Use ONLY the facts listed in the SOP. Do NOT make up details.
   - If a question cannot be answered from the SOP (e.g. clinic location, parking, practitioner background, duration of botox), set 'is_unanswered_question' to True in your response, politely decline, and remain in the 'faq' stage.
   - When the user's questions are satisfied or if they express intent to book/schedule an appointment, update the 'stage' field to 'lead_qualification' in your response.

2. **lead_qualification**:
   - If the active stage is 'lead_qualification', warmly ask 2-3 structured questions to qualify the lead. Do NOT ask them all at once. Ask them one by one.
   - Details to gather:
     * Full Name (e.g. "To get started, may I have your full name?")
     * Treatment of Interest (Botox, Fillers, or Consultation)
     * Preferred Contact Method (phone number, WhatsApp, or email)
   - As the user answers, extract and include these in the 'extracted_lead_data' field in your response.
   - Once all 3 fields are successfully collected, set the stage to 'concluded' in your response.

3. **escalated**:
   - If you detect an immediate escalation trigger (complaint, medical question, pricing negotiation, angry customer, or explicit human representative request), set 'escalate' to True, specify the precise 'escalation_reason', and set the stage to 'escalated'.

### FORMATTING REQUIREMENT:
You must return your output strictly matching the requested JSON schema. Do not output anything other than valid JSON conforming to the schema.
"""

def handle_interaction(user_message: str, state: Dict[str, Any]) -> AssistantResponse:
    """
    Accepts the current user message and the entire session state dictionary.
    
    Processes the request by:
      1. Formatting the system prompt and conversation history.
      2. Sending a completion request using OpenAI's Structured Outputs (Pydantic parsing).
      3. Applying programmatic safety checks (unanswered question threshold, LLM escalation flags).
      4. Updating the session state dictionary in-place.
      
    Returns the final AssistantResponse.
    """
    # Safety sync: Ensure user_message is recorded in history if it is not the last item
    history = state.setdefault("conversation_history", [])
    if not history or history[-1].get("content") != user_message or history[-1].get("role") != "user":
        history.append({"role": "user", "content": user_message})

    # Prepare system prompt
    current_stage = state.get("current_stage", "faq")
    lead_data = state.setdefault("lead_data", {})
    
    system_prompt = build_system_prompt(current_stage, lead_data)
    messages = [{"role": "system", "content": system_prompt}] + history

    try:
        completion = client.beta.chat.completions.parse(
            model=DEFAULT_MODEL,
            messages=messages,
            response_format=AssistantResponse,
            temperature=0.2
        )
        
        response_message = completion.choices[0].message
        
        if response_message.refusal:
            response = AssistantResponse(
                reply=f"I'm sorry, I am unable to complete this request: {response_message.refusal}",
                stage=current_stage,
                escalate=True,
                escalation_reason="Model Refusal",
                extracted_lead_data=lead_data,
                is_unanswered_question=False
            )
        else:
            response = response_message.parsed
            
    except Exception as e:
        response = AssistantResponse(
            reply="I apologize, I'm experiencing a brief system connection error. Please let me connect you with a representative.",
            stage=current_stage,
            escalate=True,
            escalation_reason=f"API connection exception: {str(e)}",
            extracted_lead_data=lead_data,
            is_unanswered_question=False
        )

    # --- Programmatic Safety Logic (In-place State updates & overrides) ---
    
    # Update lead details if any details were extracted
    if response.extracted_lead_data:
        state["lead_data"].update(response.extracted_lead_data)

    # Track unanswered question count
    if response.is_unanswered_question:
        state["unanswered_question_count"] = state.get("unanswered_question_count", 0) + 1
        
        # SOP Trigger: Escalate if customer asks > 2 questions not answered in the SOP
        if state["unanswered_question_count"] > 2:
            response.escalate = True
            response.escalation_reason = (
                "Immediate human transfer: Customer asked more than 2 questions "
                "not covered by the Standard Operating Procedure (SOP)."
            )
            response.reply = (
                "I apologize for the inconvenience, but since I don't have direct answers "
                "for some of your questions, I am immediately connecting you with a "
                "human representative of Bloom Aesthetics Clinic who can assist you further. "
                "Please hold on a brief moment!"
            )

    # Check for escalation flag from either the LLM response or our unanswered question threshold override
    if response.escalate:
        state["is_escalated"] = True
        state["current_stage"] = "escalated"
        response.stage = "escalated"
        state["escalation_reason"] = response.escalation_reason or "Immediate escalation trigger detected."
        
        # Append system handoff notification in terminal for clean visual boundary
        if "[System Handoff]" not in response.reply:
            response.reply += "\n\n[bold red][System Handoff]: Transitioning you to a clinic representative...[/bold red]"
    else:
        # Update stage and state transitions normally
        state["current_stage"] = response.stage
        if state["current_stage"] == "concluded":
            state["is_concluded"] = True

    # Record AI's response to conversation history
    history.append({"role": "assistant", "content": response.reply})
    
    return response
