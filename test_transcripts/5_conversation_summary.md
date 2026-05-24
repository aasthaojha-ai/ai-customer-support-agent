# Case 5: The final Conversation Summary printout

* **Goal**: Validate Stage 4 summary synthesis (intent, collected details, SOP gaps, next actions) and local `summary.json` file generation upon exit.

### CLI Screen Output

```
============================================================
*** CONVERSATION SUMMARY & ACTION AUDIT ***

Stage 4: Post-Interaction Summary Report
+-------------------------+--------------------------------------------------+
| Audit Metric            | Details / Findings                               |
+-------------------------+--------------------------------------------------+
| Customer Core Intent    | Requesting a Botox booking and asking out-of-SOP |
|                         | location details.                                |
|-------------------------+--------------------------------------------------|
| Details Collected       | • Name: Sarah Jenkins                            |
|                         | • Treatment Of Interest: Botox                   |
|                         | • Phone Or Email: sarah@jenkins.com              |
|-------------------------+--------------------------------------------------|
| SOP Information Gaps    | • Customer asked: "Where is your clinic located?"|
|                         |   which is not in our grounding guidelines.      |
|-------------------------+--------------------------------------------------|
| Recommended Next Actions| • Reach out to Sarah on WhatsApp/email to        |
|                         |   schedule a Botox slot.                         |
|                         | • Provide Sarah with the physical address of     |
|                         |   the clinic.                                    |
+-------------------------+--------------------------------------------------+

[v] Summary compiled and saved locally to 'summary.json'. Goodbye!
```

### Local Saved `summary.json` File Content

```json
{
  "customer_intent": "Requesting a Botox booking and asking out-of-SOP location details.",
  "details_collected": {
    "name": "Sarah Jenkins",
    "treatment_of_interest": "Botox",
    "phone_or_email": "sarah@jenkins.com"
  },
  "sop_gaps": [
    "Customer asked: 'Where is your clinic located?' which is not in our grounding guidelines."
  ],
  "next_actions": [
    "Reach out to Sarah on WhatsApp/email to schedule a Botox slot.",
    "Provide Sarah with the physical address of the clinic."
  ]
}
```
