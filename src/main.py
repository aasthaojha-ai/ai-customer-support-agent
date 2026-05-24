import os
import sys
from typing import Dict, Any, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text

# Append current directory to path to ensure robust relative imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import agent
import summary
import config
from schemas import AssistantResponse, ConversationSummary

# Initialize Rich Console for premium styling
console = Console()

def print_welcome_banner():
    """Prints a beautiful and styled welcome banner for the Bloom Aesthetics Clinic."""
    console.print()
    banner_text = Text()
    banner_text.append("*** BLOOM AESTHETICS CLINIC ***\n", style="bold deep_pink1")
    banner_text.append("AI Customer Support & Lead Qualification System\n", style="italic white")
    banner_text.append("-" * 55, style="deep_pink1")
    
    console.print(Panel(
        banner_text,
        border_style="deep_pink1",
        title="[bold white]Interactive Support CLI[/bold white]",
        title_align="center",
        padding=(1, 2)
    ))
    
    # Print basic SOP overview
    table = Table(title="[bold deep_pink1]SOP Information Grounding Quick Reference[/bold deep_pink1]", title_style="bold", border_style="dim magenta")
    table.add_column("Business Details", style="cyan")
    table.add_column("Value", style="white")
    table.add_row("Clinic Name", config.CLINIC_NAME)
    table.add_row("Hours", config.BUSINESS_HOURS)
    table.add_row("Botox Pricing", config.SERVICES["Botox"])
    table.add_row("Fillers Pricing", config.SERVICES["Fillers"])
    table.add_row("Consultation", config.SERVICES["Consultations"])
    table.add_row("Booking Policy", "WhatsApp or Website | 24hr cancellation policy")
    console.print(table)
    console.print("[dim white]Type 'exit' or 'quit' at any time to end the session.[/dim white]\n")


def print_status_sidebar(state: Dict[str, Any]):
    """Displays the active session state in a beautiful stylized sidebar panel."""
    # Build details string
    lead_data = state["lead_data"]
    lead_details = []
    for k, v in lead_data.items():
        # Humanize key names
        k_clean = k.replace("_", " ").title()
        lead_details.append(f"  - [bold deep_pink1]{k_clean}[/bold deep_pink1]: {v}")
        
    lead_str = "\n".join(lead_details) if lead_details else "  - [dim white]None collected yet[/dim white]"
    
    # Style stage colors
    stage_colors = {
        "faq": "bold cyan",
        "lead_qualification": "bold magenta",
        "escalated": "bold red",
        "concluded": "bold green"
    }
    stage_name = state["current_stage"]
    stage_colored = f"[{stage_colors.get(stage_name, 'white')}]{stage_name.replace('_', ' ').upper()}[/{stage_colors.get(stage_name, 'white')}]"
    
    # Check unanswered count
    unans_count = state.get("unanswered_question_count", 0)
    unans_color = "red" if unans_count > 1 else "yellow" if unans_count > 0 else "green"
    
    status_text = Text()
    status_text.append("Active Stage: ", style="bold white")
    status_text.append(f"{stage_name.replace('_', ' ').upper()}\n", style=stage_colors.get(stage_name, "white"))
    status_text.append("Unanswered Questions: ", style="bold white")
    status_text.append(f"{unans_count} / 2\n", style=unans_color)
    status_text.append("Lead Data Collected:\n", style="bold white")
    
    status_panel = Panel(
        status_text + Text.from_markup(lead_str),
        title="[bold deep_pink1]Session State[/bold deep_pink1]",
        border_style="deep_pink1",
        width=45
    )
    console.print(status_panel)


def display_final_summary(state: Dict[str, Any]):
    """Generates, prints, and locally saves the final conversation summary."""
    console.print("\n" + "=" * 60, style="dim white")
    with console.status("[bold magenta]Generating final conversation audit summary & saving locally...[/bold magenta]"):
        convo_summary: ConversationSummary = summary.generate_summary(state)
        
    summary_title = Text("*** CONVERSATION SUMMARY & ACTION AUDIT ***", style="bold deep_pink1")
    
    details_rows = []
    for k, v in convo_summary.details_collected.items():
        details_rows.append(f"- [bold deep_pink1]{k.replace('_', ' ').title()}[/bold deep_pink1]: {v}")
    details_str = "\n".join(details_rows) if details_rows else "- None collected"

    gaps_str = "\n".join([f"- {gap}" for gap in convo_summary.sop_gaps]) if convo_summary.sop_gaps else "- No SOP gaps identified (All questions covered by SOP)"
    actions_str = "\n".join([f"- {action}" for action in convo_summary.next_actions]) if convo_summary.next_actions else "- No follow-up actions required"

    summary_table = Table(
        title="[bold deep_pink1]Stage 4: Post-Interaction Summary Report[/bold deep_pink1]",
        border_style="deep_pink1",
        show_lines=True,
        width=80
    )
    summary_table.add_column("Audit Metric", style="bold cyan", width=25)
    summary_table.add_column("Details / Findings", style="white")
    
    summary_table.add_row("Customer Core Intent", convo_summary.customer_intent)
    summary_table.add_row("Details Collected", details_str)
    summary_table.add_row("SOP Information Gaps", gaps_str)
    summary_table.add_row("Recommended Next Actions", actions_str)
    
    console.print(Panel(
        summary_table,
        title="[bold white]Operational Handoff Package[/bold white]",
        border_style="deep_pink1",
        padding=(1, 1)
    ))
    console.print("\n[bold green][v] Summary compiled and saved locally to 'summary.json'. Goodbye![/bold green]\n")


def run_cli_loop():
    """Runs the main interactive loop for the customer support application."""
    # Manage session state dictionary
    state = {
        "conversation_history": [],
        "current_stage": "faq",
        "unanswered_question_count": 0,
        "lead_data": {},
        "is_escalated": False
    }
    
    print_welcome_banner()
    
    # Greeting from AI
    initial_greeting = (
        "Hello! Welcome to Bloom Aesthetics Clinic. "
        "How can I help you today? (We offer Botox, Fillers, and free consultations!)"
    )
    state["conversation_history"].append({"role": "assistant", "content": initial_greeting})
    
    console.print(f"[bold deep_pink1]AI Support Agent:[/bold deep_pink1] {initial_greeting}\n")
    
    # Command-line loop
    while True:
        try:
            # Print current state status sidebar
            print_status_sidebar(state)
            
            # Prompt user for input
            user_input = console.input("[bold cyan]Customer:[/bold cyan] ").strip()
            
            # Allow clean manual exit
            if user_input.lower() in ["exit", "quit", "q"]:
                console.print("\n[bold yellow]Session ended manually by user.[/bold yellow]")
                break
                
            if not user_input:
                continue
                
            # Call AI agent handler
            with console.status("[bold deep_pink1]Bloom AI is typing...[/bold deep_pink1]"):
                response: AssistantResponse = agent.handle_interaction(
                    user_message=user_input,
                    state=state
                )
            
            # If the response was flagged as unanswered, print notification details
            if response.is_unanswered_question:
                console.print(
                    f"\n[bold orange3]! [Notice] The customer asked a question outside the clinic SOP "
                    f"({state['unanswered_question_count']}/2 unanswered questions).[/bold orange3]\n"
                )
            
            # Print AI response
            console.print()
            console.print(Panel(
                response.reply,
                title="[bold deep_pink1]AI Support Agent[/bold deep_pink1]",
                border_style="deep_pink1",
                padding=(1, 2)
            ))
            console.print()
            
            # Cleanly exit if escalated or naturally concluded
            if state.get("is_escalated"):
                console.print(Panel(
                    f"[bold red]*** Escalation Hand-off Initiated ***[/bold red]\n"
                    f"[bold white]Reason:[/bold white] {state.get('escalation_reason', 'Immediate escalation trigger detected.')}",
                    border_style="red",
                    title="[bold red]System Alert[/bold red]"
                ))
                # Proceed to Stage 4 Conversation Summary
                display_final_summary(state)
                break
                
            if state["current_stage"] == "concluded" or state.get("is_concluded"):
                console.print(Panel(
                    "[bold green]*** Conversation Concluded Successfully ***[/bold green]\n"
                    "All lead information gathered and customer's questions resolved.",
                    border_style="green",
                    title="[bold green]Success[/bold green]"
                ))
                # Proceed to Stage 4 Conversation Summary
                display_final_summary(state)
                break
                
        except KeyboardInterrupt:
            console.print("\n[bold yellow]\nSession interrupted via keyboard. Exiting...[/bold yellow]")
            break
        except Exception as e:
            console.print(f"\n[bold red]An unexpected error occurred in the CLI execution loop: {str(e)}[/bold red]")
            break

if __name__ == "__main__":
    run_cli_loop()
