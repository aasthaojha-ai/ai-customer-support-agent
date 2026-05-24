import os
import sys
from dotenv import load_dotenv

# Robustly load the .env file from the parent directory (project root)
# relative to this src/config.py file location.
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path=dotenv_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def validate_config() -> str:
    """
    Validates that the required environment variables are set.
    Exits gracefully if OPENAI_API_KEY is missing or the placeholder value.
    """
    key = os.getenv("OPENAI_API_KEY")
    if not key or key.strip() == "" or key.strip() == "your_openai_api_key_here":
        print("[bold red]Configuration Error:[/bold red]")
        print("OPENAI_API_KEY is not set in the environment or .env file.")
        print("\nPlease do one of the following:")
        print("  1. Update the '.env' file in this directory with your actual OpenAI API Key.")
        print("  2. Set it in your environment: 'set OPENAI_API_KEY=your_key' (Windows) or 'export OPENAI_API_KEY=your_key' (bash).")
        print("-" * 60)
        sys.exit(1)
    return key

# =====================================================================
# Standard Operating Procedure (SOP) Grounding Data for the AI Agent
# =====================================================================

CLINIC_NAME = "Bloom Aesthetics Clinic"

BUSINESS_HOURS = "Monday to Saturday, 9:00 AM - 7:00 PM (Closed Sundays)"

SERVICES = {
    "Botox": "Prices start from £200",
    "Fillers": "Prices start from £250",
    "Consultations": "Free of charge"
}

BOOKING_POLICY = (
    "Bookings can be made via WhatsApp or our official website. "
    "A strict 24-hour cancellation policy applies to all scheduled appointments."
)

# List of immediate escalation topics/criteria
ESCALATION_TRIGGERS = [
    "Customer complaints",
    "Medical questions (e.g. pain, safety, side effects, suitability, recovery time, pregnancy instructions)",
    "Pricing negotiations or discount requests",
    "Explicit human agent/representative requests",
    "Customer expressions of anger, frustration, or severe impatience",
    "Customer asking more than 2 questions not answered in the SOP"
]

# Standard text block to be injected into system prompts
SOP_GROUNDING_TEXT = f"""
### STANDARD OPERATING PROCEDURE (SOP) - {CLINIC_NAME.upper()}
1. Business Name: {CLINIC_NAME}
2. Operating Hours: {BUSINESS_HOURS}
3. Offered Services and Prices:
   - Botox: {SERVICES['Botox']}
   - Fillers: {SERVICES['Fillers']}
   - Consultations: {SERVICES['Consultations']}
4. Booking & Cancellation Policy:
   - {BOOKING_POLICY}
"""

STRICT_INSTRUCTIONS = """
### CRITICAL COMPLIANCE RULES:
- You must ONLY answer questions that are DIRECTLY answered by the SOP above.
- Absolutely DO NOT invent details or extrapolate. If the user asks something outside the SOP (e.g. where the clinic is located, what brand of Botox is used, who the practitioners are, how long treatment takes), you must mark 'is_unanswered_question' as true, politely state that you cannot answer that specific question, and suggest they speak with a staff representative.
- Monitor for immediate escalation conditions: complaints, medical queries, price negotiations, or requests to speak to a human.
- Lead Qualification: Gather Full Name, Treatment of Interest, and Preferred Contact details (phone/whatsapp/email) conversationally.
"""
