# Case 4: Complete Lead Qualification process

* **Goal**: Validate the transition from FAQ to conversational Lead Qualification, saving responses into structured slots in-place, and concluding successfully.

```markdown
AI Support Agent: Hello! Welcome to Bloom Aesthetics Clinic. How can I help you today? (We offer Botox, Fillers, and free consultations!)

Customer: Hi, I'd like to book a Fillers appointment please.

[System Info]: Active Stage = FAQ | Unanswered Questions = 0/2
[API Call]: Structured Output returned: { "stage": "lead_qualification", "escalate": false }

AI Support Agent: We would be absolutely delighted to help you book a Fillers appointment! To get started with your reservation, may I please have your full name?

Customer: Sure, my name is Sarah Jenkins.

[System Info]: Active Stage = LEAD_QUALIFICATION | Lead Data = { "treatment_of_interest": "Fillers" }
[API Call]: Structured Output returned: { "stage": "lead_qualification", "extracted_lead_data": { "name": "Sarah Jenkins" } }

AI Support Agent: Thank you so much, Sarah! I have noted down that you are interested in our Fillers treatments. Next, could you please provide a preferred phone number, WhatsApp, or email address where we can reach you to finalize your booking?

Customer: My phone number is 07812345678.

[System Info]: Active Stage = LEAD_QUALIFICATION | Lead Data = { "name": "Sarah Jenkins", "treatment_of_interest": "Fillers" }
[API Call]: Structured Output returned: { "stage": "concluded", "extracted_lead_data": { "phone_or_email": "07812345678" } }

AI Support Agent: Perfect, Sarah! I have gathered all your details and saved your contact number (07812345678) for the Fillers appointment. One of our team members will contact you on WhatsApp shortly to confirm your preferred time slot. Have a wonderful day!

*** Success: Conversation Concluded Successfully ***
All lead information gathered and customer's questions resolved.
```
