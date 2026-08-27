import json
from pathlib import Path
from datetime import datetime, timedelta

from llm import generate_answer


# ============================================================
# Load JSON file
# ============================================================

def load_json(file_path):

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


# ============================================================
# Load accounts and tickets
# ============================================================

def load_data():

    project_root = Path(__file__).resolve().parent.parent

    accounts_file = project_root / "data" / "accounts.json"
    tickets_file = project_root / "data" / "tickets.json"

    if not accounts_file.exists():
        raise FileNotFoundError(
            f"accounts.json not found: {accounts_file}"
        )

    if not tickets_file.exists():
        raise FileNotFoundError(
            f"tickets.json not found: {tickets_file}"
        )

    accounts = load_json(accounts_file)
    tickets = load_json(tickets_file)

    return accounts, tickets


# ============================================================
# Find account
# ============================================================

def get_account_by_id(account_id, accounts):

    for account in accounts:

        if account.get("account_id") == account_id:
            return account

    raise ValueError(
        f"Account {account_id} not found."
    )


# ============================================================
# Get latest ticket date from dataset
# ============================================================

def get_dataset_reference_date(tickets):

    dates = []

    for ticket in tickets:

        created_at = ticket.get("created_at")

        if not created_at:
            continue

        try:

            ticket_date = datetime.fromisoformat(
                created_at.replace("Z", "+00:00")
            )

            dates.append(ticket_date)

        except ValueError:
            continue

    if not dates:

        raise ValueError(
            "No valid ticket dates found."
        )

    return max(dates)


# ============================================================
# Get account tickets from last 90 days
# ============================================================

def get_account_tickets(
    account_id,
    tickets,
    days=90
):

    # Use latest ticket date in dataset
    # as the reference date.

    reference_date = get_dataset_reference_date(
        tickets
    )

    cutoff_date = (
        reference_date
        - timedelta(days=days)
    )

    account_tickets = []

    for ticket in tickets:

        # Match account ID
        if ticket.get("account_id") != account_id:
            continue

        created_at = ticket.get("created_at")

        if not created_at:
            continue

        try:

            ticket_date = datetime.fromisoformat(
                created_at.replace("Z", "+00:00")
            )

        except ValueError:

            continue

        # Last 90 days
        if cutoff_date <= ticket_date <= reference_date:

            account_tickets.append(ticket)

    # Newest ticket first
    account_tickets.sort(
        key=lambda x: x.get("created_at", ""),
        reverse=True
    )

    return account_tickets, reference_date


# ============================================================
# Build ticket context
# ============================================================

def build_ticket_context(tickets):

    if not tickets:

        return "No tickets found in the last 90 days."

    context_parts = []

    for ticket in tickets:

        context_parts.append(
            f"""
--------------------------------------------------
Ticket ID: {ticket.get("ticket_id")}

Created At:
{ticket.get("created_at")}

Product:
{ticket.get("product")}

Product Area:
{ticket.get("product_area")}

Category:
{ticket.get("category")}

Urgency:
{ticket.get("urgency")}

Status:
{ticket.get("status")}

Satisfaction Score:
{ticket.get("satisfaction_score")}

Subject:
{ticket.get("subject")}

Ticket Body:
{ticket.get("body")}
--------------------------------------------------
"""
        )

    return "\n".join(context_parts)


# ============================================================
# Generate Account Health
# ============================================================

def generate_account_health(account_id):

    # --------------------------------------------------------
    # Load datasets
    # --------------------------------------------------------

    accounts, tickets = load_data()

    # --------------------------------------------------------
    # Find account
    # --------------------------------------------------------

    account = get_account_by_id(
        account_id,
        accounts
    )

    # --------------------------------------------------------
    # Get last 90 days tickets
    # --------------------------------------------------------

    recent_tickets, reference_date = get_account_tickets(
        account_id,
        tickets,
        days=90
    )

    # ========================================================
    # DEBUG INFORMATION
    # ========================================================

    print("\n" + "=" * 80)
    print("LAST 90 DAYS TICKETS")
    print("=" * 80)

    print(
        f"Reference date: {reference_date}"
    )

    print(
        f"90-day cutoff: "
        f"{reference_date - timedelta(days=90)}"
    )

    print(
        f"Number of tickets: "
        f"{len(recent_tickets)}"
    )

    for ticket in recent_tickets:

        print(
            ticket.get("ticket_id"),
            "|",
            ticket.get("created_at"),
            "|",
            ticket.get("subject")
        )

    # ========================================================
    # Account information
    # ========================================================

    primary_contact = account.get(
        "primary_contact",
        {}
    )

    account_context = f"""
Account ID:
{account.get("account_id")}

Company:
{account.get("company")}

TAM:
{account.get("tam")}

Plan Tier:
{account.get("plan_tier")}

ARR:
{account.get("arr_usd")}

Licensed Seats:
{account.get("seats_licensed")}

Active Seats:
{account.get("seats_active")}

Products:
{account.get("products")}

Health Status:
{account.get("health_status")}

Usage Trend:
{account.get("usage_trend")}

Open Tickets:
{account.get("open_tickets")}

P1 Tickets Last 30 Days:
{account.get("p1_tickets_last_30d")}

Customer Since:
{account.get("customer_since")}

Renewal Date:
{account.get("renewal_date")}

Last QBR Date:
{account.get("last_qbr_date")}

Escalation Notes:
{account.get("escalation_notes")}

NPS Score:
{account.get("nps_score")}

Last Login Days Ago:
{account.get("last_login_days_ago")}

Active Integrations:
{account.get("integrations_active")}

Region:
{account.get("region")}

Industry:
{account.get("industry")}

Primary Contact:
{primary_contact.get("name")}

Primary Contact Title:
{primary_contact.get("title")}
"""

    # ========================================================
    # Ticket history
    # ========================================================

    ticket_context = build_ticket_context(
        recent_tickets
    )

    # ========================================================
    # LLM PROMPT
    # ========================================================

    prompt = f"""
You are an AI assistant helping a Technical Account Manager.

Create an Account Health Brief using ONLY the supplied
account information and ticket history.

Do NOT invent facts.

============================================================
DATASET REFERENCE DATE
============================================================

{reference_date.isoformat()}

The ticket history contains tickets from the last
90 days relative to this dataset reference date.

============================================================
ACCOUNT INFORMATION
============================================================

{account_context}

============================================================
LAST 90 DAYS TICKET HISTORY
============================================================

{ticket_context}

============================================================
REQUIRED OUTPUT
============================================================

Return ONLY valid JSON.

Use exactly this structure:

{{
    "account_id": "{account_id}",

    "executive_summary": "3-5 sentences",

    "open_risks_and_flagged_issues": [
        {{
            "risk": "string",
            "severity": "High/Medium/Low",
            "evidence": "string",
            "ticket_quote": "exact quote from ticket body"
        }}
    ],

    "recommended_tam_talking_points": [
        "string",
        "string",
        "string"
    ]
}}

============================================================
EXECUTIVE SUMMARY
============================================================

Write 3-5 sentences.

Consider:

- Health status
- Usage trend
- Open tickets
- Recent ticket history
- NPS
- Renewal date
- Escalation notes
- Customer activity

============================================================
RISK RULES
============================================================

Identify meaningful risks such as:

- Repeated support problems
- High urgency incidents
- Unresolved issues
- Performance problems
- Integration problems
- Negative customer satisfaction
- Declining usage
- Churn signals
- Escalation signals

IMPORTANT:

If a risk is based on a ticket, include an EXACT quote
from the ticket body.

The quote must be copied directly from the provided
ticket body.

DO NOT invent quotes.

DO NOT paraphrase quotes.

If a risk is based only on account-level information,
ticket_quote may be an empty string.

============================================================
TAM TALKING POINTS
============================================================

Provide 3-5 actionable talking points.

Focus on:

- Open support problems
- Customer concerns
- Usage changes
- Product adoption
- Renewal concerns
- Customer satisfaction
- Follow-up actions

============================================================
GROUNDING
============================================================

Use ONLY the supplied information.

Do not invent:

- complaints
- ticket information
- dates
- quotes
- products
- business problems

Return ONLY valid JSON.
"""

    # ========================================================
    # Gemini
    # ========================================================

    response = generate_answer(
        question=f"Generate account health brief for {account_id}",
        context=prompt
    )

    # ========================================================
    # Remove Markdown code fences
    # ========================================================

    response = response.strip()

    if response.startswith("```"):

        response = response.replace(
            "```json",
            ""
        )

        response = response.replace(
            "```",
            ""
        )

        response = response.strip()

    # ========================================================
    # Parse JSON
    # ========================================================

    try:

        result = json.loads(response)

    except json.JSONDecodeError as e:

        print("\nInvalid JSON returned by LLM:")
        print(response)

        raise ValueError(
            f"Could not parse LLM response: {e}"
        )

    # ========================================================
    # Add metadata
    # ========================================================

    result["ticket_count_last_90_days"] = len(
        recent_tickets
    )

    result["dataset_reference_date"] = (
        reference_date.isoformat()
    )

    return result


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    # Account that exists in BOTH datasets
    account_id = "ACC-1785"

    print("=" * 80)
    print("ACCOUNT HEALTH ANALYSIS")
    print("=" * 80)

    result = generate_account_health(
        account_id
    )

    print("\n" + "=" * 80)
    print("FINAL ACCOUNT HEALTH RESULT")
    print("=" * 80)

    print(
        json.dumps(
            result,
            indent=4,
            ensure_ascii=False
        )
    )