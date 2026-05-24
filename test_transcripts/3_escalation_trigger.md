# Case 3: Escalation Trigger (Customer anger/complaint)

* **Goal**: Validate immediate escalation detection. An angry customer or medical query must bypass normal flows and hand-off instantly.

```markdown
AI Support Agent: Hello! Welcome to Bloom Aesthetics Clinic. How can I help you today? (We offer Botox, Fillers, and free consultations!)

Customer: I am extremely unhappy. I had a Botox session yesterday and my left eyelid is drooping! I want to speak to someone right now!

[System Info]: Active Stage = FAQ | Unanswered Questions = 0/2
[API Call]: Structured Output returned: { "stage": "escalated", "escalate": true, "escalation_reason": "Customer complaint & potential medical side-effect post-treatment." }

AI Support Agent: I am incredibly sorry to hear that you are experiencing this, and I understand your concern completely. I am immediately connecting you with a human clinic manager and a practitioner to address this situation as our top priority. Please stay on the line.

[System Handoff]: Transitioning you to a clinic representative...

*** System Alert: Escalation Hand-off Initiated ***
Reason: Customer complaint & potential medical side-effect post-treatment.
```
