from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class AssistantResponse(BaseModel):
    """
    Schema for regular interactive responses from the AI Customer Support Agent.
    Guarantees structured extraction and workflow tracking.
    """
    reply: str = Field(
        description="The warm, empathetic, and professional response string to show to the customer."
    )
    stage: str = Field(
        description="The active conversation stage. Must be one of: 'faq', 'lead_qualification', 'escalated', 'concluded'."
    )
    escalate: bool = Field(
        description="Set to true if immediate escalation is triggered (due to complaint, medical question, pricing negotiation, human request, or high frustration)."
    )
    escalation_reason: Optional[str] = Field(
        default=None,
        description="The precise reason for escalation if escalate is true. Otherwise set to null."
    )
    extracted_lead_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Key-value pairs of any gathered lead information. Can include: name, treatment_of_interest, phone_or_email, preferred_booking_time. Maintain and update existing data across turns."
    )
    is_unanswered_question: bool = Field(
        description="Set to true if the customer's input contained a query or request that could not be answered using the provided SOP. Otherwise set to false."
    )


class ConversationSummary(BaseModel):
    """
    Schema for Stage 4: Final Conversation Summary.
    Organizes intent, gathered lead data, detected SOP gaps, and recommended next actions.
    """
    customer_intent: str = Field(
        description="A concise summary of the customer's core intent or reason for contacting the clinic."
    )
    details_collected: Dict[str, Any] = Field(
        description="The final compiled dictionary of lead details (e.g. name, contact, treatment of interest) that were successfully gathered."
    )
    sop_gaps: List[str] = Field(
        description="A list of specific questions, queries, or topics the customer asked that were not answered by the SOP."
    )
    next_actions: List[str] = Field(
        description="Recommended next steps for the clinic's staff (e.g. 'Call John back on WhatsApp to book Botox', 'Escalate to medical practitioner to answer recovery time query')."
    )
