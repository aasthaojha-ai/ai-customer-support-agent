import os
import sys
import json
from typing import List, Dict, Any

# Append current directory to path to ensure robust relative imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from schemas import ConversationSummary

# Safely import OpenAI to allow running entirely offline/without the package
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Initialize OpenAI client with the validated key if available and not in mock mode
api_key = config.validate_config()
client = None
if OPENAI_AVAILABLE and not config.MOCK_MODE:
    try:
        client = OpenAI(api_key=api_key)
    except Exception:
        config.MOCK_MODE = True
else:
    config.MOCK_MODE = True

# Recommended default model that is highly capable and supports native Pydantic structured outputs
DEFAULT_MODEL = "gpt-4o-mini"

def generate_conversation_summary(
    conversation_history: List[Dict[str, str]], 
    lead_data: Dict[str, Any]
) -> ConversationSummary:
    """
    Generates a structured final summary of the conversation using the ConversationSummary schema.
    Normally called when a conversation is escalated or concluded.
    """
    transcript = ""
    for msg in conversation_history:
        role = "Customer" if msg["role"] == "user" else "AI Support Agent"
        transcript += f"{role}: {msg['content']}\n"
        
    summary_prompt = f"""You are an operations audit assistant for "Bloom Aesthetics Clinic".
Analyze the following conversation transcript between a Customer and our AI Support Agent, and summarize it strictly conforming to the requested JSON schema.

### TRANSCRIPT:
{transcript}

### COMPILED GATHERED LEAD DATA:
{json.dumps(lead_data, indent=2)}

### SUMMARY INSTRUCTIONS:
1. **customer_intent**: Briefly describe the customer's main reason for messaging the clinic (e.g. Booking a Botox appointment, general price check, medical inquiry).
2. **details_collected**: Output the final validated lead information gathered.
3. **sop_gaps**: List all specific customer questions or requests that were NOT answered in the SOP (e.g. side effects, specific clinic location details, practitioner details). If none, output an empty list.
4. **next_actions**: Prescribe actionable next steps for a human staff member (e.g. "Call John on 07xxx to schedule a Botox consultation", "Send clinic location address", "Answer medical question regarding pain during procedure").
"""
    try:
        completion = client.beta.chat.completions.parse(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": summary_prompt}],
            response_format=ConversationSummary,
            temperature=0.0
        )
        return completion.choices[0].message.parsed
    except Exception as e:
        return ConversationSummary(
            customer_intent="Interaction with customer support.",
            details_collected=lead_data,
            sop_gaps=["Error compiling SOP gaps"],
            next_actions=[f"Error generating summary: {str(e)}. Review raw history manually."]
        )


def generate_summary_mock(session_state: Dict[str, Any]) -> ConversationSummary:
    """
    Generates a structured final summary locally for demo offline run.
    Parses conversation history to extract SOP gaps, intent, and next actions.
    """
    conversation_history = session_state.get("conversation_history", [])
    lead_data = session_state.get("lead_data", {})
    
    # Defaults
    customer_intent = "Inquiry regarding clinic services and appointment booking."
    sop_gaps = []
    
    # Analyze conversation history locally
    for msg in conversation_history:
        if msg["role"] == "user":
            content = msg["content"].lower()
            if "pregnancy" in content or "safe" in content:
                customer_intent = "Medical safety query about Botox treatment suitability."
                sop_gaps.append("Is Botox safe during pregnancy? (Medical suitability query)")
            elif "pain" in content or "hurt" in content:
                customer_intent = "Query regarding Botox procedure discomfort and safety."
                sop_gaps.append("Does the procedure hurt? (Discomfort query)")
            elif "location" in content or "where" in content:
                sop_gaps.append("Clinic physical location details / Parking options")
            elif "brand" in content:
                sop_gaps.append("Which Botox brands are used by the clinic")
            elif "complain" in content or "angry" in content:
                customer_intent = "Customer complaint handoff."
                
    # Compile recommended next actions
    next_actions = []
    if session_state.get("is_escalated"):
        reason = session_state.get("escalation_reason", "")
        if "Medical" in reason:
            next_actions.append("Have a qualified medical practitioner contact the patient regarding safety/pain queries.")
        elif "complaint" in reason or "human" in reason:
            next_actions.append("Have a clinic manager contact the customer immediately to resolve their complaint.")
        elif "SOP" in reason or "2 questions" in reason:
            next_actions.append("Provide details on clinic location, practitioner credentials, and Botox brands to the client.")
        else:
            next_actions.append("Contact the customer to address their outstanding queries.")
    else:
        name = lead_data.get("name", "Customer")
        treatment = lead_data.get("treatment_of_interest", "desired treatment")
        contact = lead_data.get("phone_or_email", "provided contact info")
        next_actions.append(f"Call {name} on {contact} to schedule their {treatment} session.")
        next_actions.append("Send clinic welcome pack and address details via SMS/Email.")

    return ConversationSummary(
        customer_intent=customer_intent,
        details_collected=lead_data,
        sop_gaps=sop_gaps or ["None (all queries answered within clinic SOP)"],
        next_actions=next_actions
    )


def generate_summary(session_state: Dict[str, Any]) -> ConversationSummary:
    """
    Stage 4: Post-Interaction Conversation Summary.
    Accepts the entire session state dictionary, makes one last LLM call or mock call 
    to generate a clean structured summary, and automatically saves the results 
    locally to 'summary.json' at the project root directory.
    """
    conversation_history = session_state.get("conversation_history", [])
    lead_data = session_state.get("lead_data", {})
    
    # 1. Call the LLM or Mock to get the structured summary
    if config.MOCK_MODE:
        summary = generate_summary_mock(session_state)
    else:
        summary = generate_conversation_summary(conversation_history, lead_data)
    
    # 2. Compile dictionary to save locally
    summary_data = {
        "customer_intent": summary.customer_intent,
        "details_collected": summary.details_collected,
        "sop_gaps": summary.sop_gaps,
        "next_actions": summary.next_actions
    }
    
    # 3. Save locally to 'summary.json' at the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    summary_json_path = os.path.join(project_root, "summary.json")
    
    try:
        with open(summary_json_path, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        # Silently fail or log error so it does not crash the CLI termination
        pass
        
    return summary
