# Bloom Aesthetics Clinic - AI Support CLI Workflow

Welcome to the **Bloom Aesthetics Clinic AI Customer Support CLI**. This project is a Python CLI-based AI customer support workflow built for the Closira internship assignment.

The application implements a 4-stage pipeline (FAQ Answering, Lead Qualification, Escalation Handling, and Conversation Summarization) using **OpenAI Structured Outputs (JSON Mode with Pydantic)**. The workflow uses structured JSON outputs and validation to improve response consistency.

---


## Project Directory Structure

The project is organized into the following file structure:

```text
closira-ai-agent/

├── .env                  # Local environment file containing the OPENAI_API_KEY
├── .gitignore            # Specifies files and folders to ignore in Git
├── README.md             # Project overview and setup instructions
├── prompt_design.md      # System prompt design and workflow reasoning
├── requirements.txt      # Python dependencies

├── src/                  # Main source code directory
│   ├── __init__.py
│   ├── main.py           # Runs the CLI conversation loop
│   ├── config.py         # Stores SOP data and app configuration
│   ├── schemas.py        # Pydantic schemas for structured outputs
│   ├── agent.py          # Handles AI workflow and API interaction
│   └── summary.py        # Generates the final conversation summary

└── test_transcripts/     # Sample test conversations for evaluation
    ├── 1_in_sop_question.md
    ├── 2_out_of_scope.md
    ├── 3_escalation_trigger.md
    ├── 4_lead_qualification.md
    └── 5_conversation_summary.md

---

## Quick Start Guide

### 1. Prerequisites

Ensure you have **Python 3.9+** installed on your system.

---

### 2. Installation

Clone or navigate to the project directory and install the required dependencies using pip:

```bash
pip install -r requirements.txt

This project uses the following main libraries:

- `openai` → For OpenAI API interaction
- `pydantic` → For structured JSON validation
- `python-dotenv` → For loading environment variables
- `rich` → For improving CLI output formatting

### 3. Configure the Environment

Create or open the `.env` file in the project root folder and add your OpenAI API key:

```env
OPENAI_API_KEY=your_api_key_here

### 4. Running the CLI

Run the application from the project root directory using:

```bash
python src/main.py

---

## Design Trade-offs & Limitations

### 1. In-Memory Session State

The application currently stores conversation history, lead details, and workflow state in memory using Python dictionaries. This works well for a simple CLI-based workflow, but a production multi-user system would require persistent storage such as Redis or PostgreSQL.

---

### 2. Conversational Lead Qualification

Lead qualification is handled through a conversational flow instead of fixed form inputs. This makes the interaction feel more natural, although it may take slightly longer to collect all required details compared to a traditional form.

---

### 3. Structured JSON Outputs

The workflow uses OpenAI structured outputs with Pydantic validation to maintain consistent response formatting. While this improves reliability, it also adds slight complexity and depends on models that support structured outputs.
