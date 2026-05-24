# Case 1: In-SOP Question (Botox prices)

* **Goal**: Validate FAQ answering and successful SOP grounding. The agent must provide accurate, non-hallucinated pricing based strictly on the SOP.

```markdown
AI Support Agent: Hello! Welcome to Bloom Aesthetics Clinic. How can I help you today? (We offer Botox, Fillers, and free consultations!)

Customer: Hi, I'm thinking of getting Botox. How much does it cost?

[System Info]: Active Stage = FAQ | Unanswered Questions = 0/2
[API Call]: Structured Output returned: { "stage": "faq", "escalate": false, "is_unanswered_question": false }

AI Support Agent: Hello! We would love to help you with that. Our Botox treatments start from £200. We also offer free consultations if you would like to discuss this with our specialists! Would you like to schedule an appointment?

Customer: Okay, thank you. What are your opening hours?

[System Info]: Active Stage = FAQ | Unanswered Questions = 0/2
[API Call]: Structured Output returned: { "stage": "faq", "escalate": false, "is_unanswered_question": false }

AI Support Agent: You're very welcome! We are open Monday to Saturday, from 9:00 AM to 7:00 PM. We are closed on Sundays. Please let me know if you would like to book a session!
```
