import json
import re
from pathlib import Path

from retrieval import retrieve_kb
from llm import generate_answer


# ============================================================
# Extract JSON from LLM response
# ============================================================

def extract_json(text):

    text = text.strip()

    # Remove markdown code fences
    text = re.sub(r"```json", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```", "", text)

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        raise ValueError("No valid JSON found in LLM response.")

    return json.loads(match.group())


# ============================================================
# Ticket Triage
# ============================================================

def triage_ticket(ticket, top_k=3):

    subject = ticket.get("subject", "")
    body = ticket.get("body", "")

    if not subject and not body:
        raise ValueError("Ticket must contain subject or body.")

    # --------------------------------------------------------
    # 1. Create searchable ticket text
    # --------------------------------------------------------

    ticket_text = f"""
Subject: {subject}

Body:
{body}
"""

    # --------------------------------------------------------
    # 2. Retrieve relevant Knowledge Base information
    # --------------------------------------------------------

    results = retrieve_kb(
        ticket_text,
        top_k=top_k
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    # --------------------------------------------------------
    # 3. Build KB context
    # --------------------------------------------------------

    context_parts = []

    for i, document in enumerate(documents):

        metadata = metadatas[i]

        context_parts.append(
            f"""
Knowledge Base Result {i + 1}

Content:
{document}

Metadata:
{metadata}
"""
        )

    context = "\n\n".join(context_parts)

    # --------------------------------------------------------
    # 4. Create triage prompt
    # --------------------------------------------------------

    prompt = f"""
You are an AI Technical Support Ticket Triage Agent.

Analyze the following incoming support ticket.

Use the provided Knowledge Base context to identify
whether the ticket matches a known issue.

Do NOT invent information that is not supported by
the ticket or the Knowledge Base.

========================
TICKET
========================

{ticket_text}

========================
KNOWLEDGE BASE
========================

{context}

========================
TASK
========================

Classify the ticket into:

1. product_area
2. issue_category
3. urgency
4. reasoning
5. known_issue
6. knowledge_base_source
7. responder_team
8. first_response

Urgency must be exactly one of:

P1
P2
P3
P4

Use the following general interpretation:

P1 = Critical / major business impact / widespread or
     severe service disruption

P2 = High impact / significant functionality affected
     or many users affected

P3 = Moderate impact / limited users or workaround exists

P4 = Low impact / general question, request, or minor issue

The urgency decision must include a short explanation.

For known_issue:

true = the ticket clearly matches information in the
       provided Knowledge Base.

false = there is no clear matching known issue.

For knowledge_base_source:

Return the relevant KB source filename when there
is a known issue.

If there is no known issue, return:

"None"

For responder_team:

Recommend the most appropriate internal support team
based on the issue.

For first_response:

Write a professional first-response message that a
support agent could send to the customer.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "product_area": "string",
    "issue_category": "string",
    "urgency": "P1",
    "reasoning": "string",
    "known_issue": true,
    "knowledge_base_source": "string",
    "responder_team": "string",
    "first_response": "string"
}}
"""

    # --------------------------------------------------------
    # 5. Generate structured answer
    # --------------------------------------------------------

    response = generate_answer(
        question=ticket_text,
        context=prompt
    )

    # --------------------------------------------------------
    # 6. Convert JSON response to Python dictionary
    # --------------------------------------------------------

    triage_result = extract_json(response)

    # --------------------------------------------------------
    # 7. Add ticket information
    # --------------------------------------------------------

    triage_result["ticket_id"] = ticket.get(
        "ticket_id",
        "Unknown"
    )

    triage_result["account_id"] = ticket.get(
        "account_id",
        "Unknown"
    )

    # --------------------------------------------------------
    # 8. Add retrieved KB sources
    # --------------------------------------------------------

    triage_result["retrieved_sources"] = metadatas

    return triage_result


# ============================================================
# Load tickets.json
# ============================================================

def load_tickets():

    project_root = Path(__file__).resolve().parent.parent

    ticket_file = project_root / "data" / "tickets.json"

    if not ticket_file.exists():
        raise FileNotFoundError(
            f"Ticket dataset not found: {ticket_file}"
        )

    with open(ticket_file, "r", encoding="utf-8") as file:
        tickets = json.load(file)

    return tickets


# ============================================================
# Find a ticket by Ticket ID
# ============================================================

def get_ticket_by_id(ticket_id):

    tickets = load_tickets()

    for ticket in tickets:

        if ticket.get("ticket_id") == ticket_id:
            return ticket

    raise ValueError(
        f"Ticket {ticket_id} not found."
    )


# ============================================================
# Test with a real ticket from tickets.json
# ============================================================

if __name__ == "__main__":

    # Change this to any ticket ID from tickets.json
    ticket_id = "TKT-10358"

    ticket = get_ticket_by_id(ticket_id)

    print("=" * 80)
    print("INPUT TICKET")
    print("=" * 80)

    print(
        json.dumps(
            ticket,
            indent=4
        )
    )

    result = triage_ticket(ticket)

    print("\n" + "=" * 80)
    print("TICKET TRIAGE RESULT")
    print("=" * 80)

    print(
        json.dumps(
            result,
            indent=4
        )
    )