# Case 2: Out-of-Scope Question (Handling a Gap and Escalating)

* **Goal**: Validate hallucination prevention and out-of-SOP guardrails. If the customer asks more than 2 out-of-scope questions, the program must trigger an immediate human escalation.

```markdown
AI Support Agent: Hello! Welcome to Bloom Aesthetics Clinic. How can I help you today? (We offer Botox, Fillers, and free consultations!)

Customer: Hi, where is your clinic located?

[System Info]: Active Stage = FAQ | Unanswered Questions = 0/2
[API Call]: Structured Output returned: { "stage": "faq", "is_unanswered_question": true }
[Notice]: The customer asked a question outside the clinic SOP (1/2 unanswered questions).

AI Support Agent: I would be happy to help, but I don't have our physical address details listed in my system. I can suggest speaking to a clinic representative to get our exact directions! What else can I assist you with today?

Customer: Oh ok. Who is the main doctor operating there?

[System Info]: Active Stage = FAQ | Unanswered Questions = 1/2
[API Call]: Structured Output returned: { "stage": "faq", "is_unanswered_question": true }
[Notice]: The customer asked a question outside the clinic SOP (2/2 unanswered questions).

AI Support Agent: I apologize, but I do not have information about our specific practitioners or doctors in my standard operating procedures. I recommend checking our website or consulting a staff representative. Is there anything else about our services, hours, or booking policies I can answer?

Customer: Is there a parking lot near the clinic?

[System Info]: Active Stage = FAQ | Unanswered Questions = 2/2
[API Call]: Structured Output returned: { "stage": "faq", "is_unanswered_question": true }
[Notice]: The customer asked a question outside the clinic SOP (3/2 unanswered questions).

[Programmatic Overrides Triggered]: unanswered_question_count > 2. Escalate set to True.

AI Support Agent: I apologize for the inconvenience, but since I don't have direct answers for some of your questions, I am immediately connecting you with a human representative of Bloom Aesthetics Clinic who can assist you further. Please hold on a brief moment!

*** System Alert: Escalation Hand-off Initiated ***
Reason: Immediate human transfer: Customer asked more than 2 questions not covered by the Standard Operating Procedure (SOP).
```
