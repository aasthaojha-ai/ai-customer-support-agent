import os
import sys
import json
from typing import List, Dict, Any
from openai import OpenAI

# Append current directory to path to ensure robust relative imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from schemas import ConversationSummary

# Initialize OpenAI client with the validated key
api_key = config.validate_config()
client = OpenAI(api_key=api_key)

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


def generate_summary(session_state: Dict[str, Any]) -> ConversationSummary:
    """
    Stage 4: Post-Interaction Conversation Summary.
    Accepts the entire session state dictionary, makes one last LLM call to generate 
    a clean structured summary, and automatically saves the results locally to 'summary.json'
    at the project root directory.
    """
    conversation_history = session_state.get("conversation_history", [])
    lead_data = session_state.get("lead_data", {})
    
    # 1. Call the LLM to get the structured summary
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
