import json
import streamlit as st

from rag import rag_answer
from ticket_triage import get_ticket_by_id, triage_ticket
from account_health import generate_account_health


# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="Zycus AI Support System",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# Title
# ============================================================

st.title("🤖 Zycus AI Support System")

st.write(
    "AI-powered customer support system for Knowledge Base "
    "question answering, ticket triage, and account health analysis."
)


# ============================================================
# Sidebar Navigation
# ============================================================

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select a feature:",
    [
        "Knowledge Base Q&A",
        "Ticket Triage",
        "Account Health"
    ]
)


# ============================================================
# PAGE 1 — KNOWLEDGE BASE Q&A
# ============================================================

if page == "Knowledge Base Q&A":

    st.header("🔎 Knowledge Base Q&A")

    st.write(
        "Ask questions about products, troubleshooting, "
        "billing, onboarding, authentication, and integrations."
    )

    question = st.text_input(
        "Ask your question:",
        placeholder=(
            "Why are AnalyticsHub reports truncated "
            "at 1000 rows?"
        )
    )

    if st.button(
        "Ask Question",
        type="primary"
    ):

        if not question.strip():

            st.warning(
                "Please enter a question."
            )

        else:

            with st.spinner(
                "Searching knowledge base and generating answer..."
            ):

                try:

                    answer, sources = rag_answer(
                        question,
                        top_k=3
                    )

                    # ----------------------------------------
                    # Answer
                    # ----------------------------------------

                    st.subheader("Answer")

                    st.write(answer)

                    # ----------------------------------------
                    # Sources
                    # ----------------------------------------

                    st.subheader("Sources")

                    for source in sources:

                        st.write(
                            f"**{source.get('title', 'Unknown')}**"
                        )

                        st.caption(
                            f"Source: "
                            f"{source.get('source', 'Unknown')} | "
                            f"Section: "
                            f"{source.get('section', 'Unknown')}"
                        )

                except Exception as e:

                    st.error(
                        f"Error generating answer: {e}"
                    )


# ============================================================
# PAGE 2 — TICKET TRIAGE
# ============================================================

elif page == "Ticket Triage":

    st.header("🎫 Intelligent Ticket Triage")

    st.write(
        "Select a real support ticket from tickets.json "
        "and generate an AI triage result."
    )

    # --------------------------------------------------------
    # Load ticket IDs
    # --------------------------------------------------------

    try:

        from ticket_triage import load_tickets

        tickets = load_tickets()

        ticket_ids = [
            ticket.get("ticket_id")
            for ticket in tickets
            if ticket.get("ticket_id")
        ]

    except Exception as e:

        st.error(
            f"Could not load tickets: {e}"
        )

        ticket_ids = []

    # --------------------------------------------------------
    # Ticket selector
    # --------------------------------------------------------

    if ticket_ids:

        selected_ticket_id = st.selectbox(
            "Select Ticket:",
            ticket_ids
        )

        if st.button(
            "Run Ticket Triage",
            type="primary"
        ):

            with st.spinner(
                "Analyzing ticket and retrieving Knowledge Base information..."
            ):

                try:

                    ticket = get_ticket_by_id(
                        selected_ticket_id
                    )

                    result = triage_ticket(
                        ticket,
                        top_k=3
                    )

                    # ========================================
                    # Input Ticket
                    # ========================================

                    st.subheader("📋 Input Ticket")

                    st.json(ticket)

                    # ========================================
                    # Triage Result
                    # ========================================

                    st.subheader(
                        "🎯 Triage Result"
                    )

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        st.metric(
                            "Product Area",
                            result.get(
                                "product_area",
                                "Unknown"
                            )
                        )

                    with col2:

                        st.metric(
                            "Issue Category",
                            result.get(
                                "issue_category",
                                "Unknown"
                            )
                        )

                    with col3:

                        st.metric(
                            "Urgency",
                            result.get(
                                "urgency",
                                "Unknown"
                            )
                        )

                    # ========================================
                    # Detailed Information
                    # ========================================

                    st.subheader(
                        "Reasoning"
                    )

                    st.write(
                        result.get(
                            "reasoning",
                            "No reasoning available."
                        )
                    )

                    st.subheader(
                        "Known Issue"
                    )

                    if result.get("known_issue"):

                        st.success(
                            "Yes — matching Knowledge Base issue found."
                        )

                    else:

                        st.info(
                            "No clear matching known issue."
                        )

                    st.subheader(
                        "Knowledge Base Source"
                    )

                    st.write(
                        result.get(
                            "knowledge_base_source",
                            "None"
                        )
                    )

                    st.subheader(
                        "Responder Team"
                    )

                    st.write(
                        result.get(
                            "responder_team",
                            "Unknown"
                        )
                    )

                    st.subheader(
                        "💬 First Response"
                    )

                    st.text_area(
                        "Customer response:",
                        result.get(
                            "first_response",
                            ""
                        ),
                        height=220
                    )

                    # ========================================
                    # Retrieved Sources
                    # ========================================

                    st.subheader(
                        "📚 Retrieved Knowledge Base Sources"
                    )

                    for source in result.get(
                        "retrieved_sources",
                        []
                    ):

                        st.write(
                            f"**{source.get('title', 'Unknown')}**"
                        )

                        st.caption(
                            f"Source: "
                            f"{source.get('source', 'Unknown')} | "
                            f"Section: "
                            f"{source.get('section', 'Unknown')}"
                        )

                except Exception as e:

                    st.error(
                        f"Ticket triage failed: {e}"
                    )


# ============================================================
# PAGE 3 — ACCOUNT HEALTH
# ============================================================

elif page == "Account Health":

    st.header("🏢 TAM Account Health")

    st.write(
        "Generate an Account Health Brief using account "
        "information and the last 90 days of ticket history."
    )

    # --------------------------------------------------------
    # Load shared account IDs
    # --------------------------------------------------------

    try:

        accounts, tickets = (
            __import__(
                "account_health"
            ).load_data()
        )

        account_ids = sorted(
            list(
                set(
                    account.get("account_id")
                    for account in accounts
                    if account.get("account_id")
                )
                &
                set(
                    ticket.get("account_id")
                    for ticket in tickets
                    if ticket.get("account_id")
                )
            )
        )

    except Exception as e:

        st.error(
            f"Could not load accounts: {e}"
        )

        account_ids = []

    # --------------------------------------------------------
    # Account selector
    # --------------------------------------------------------

    if account_ids:

        selected_account_id = st.selectbox(
            "Select Account:",
            account_ids
        )

        if st.button(
            "Generate Account Health",
            type="primary"
        ):

            with st.spinner(
                "Analyzing account health and ticket history..."
            ):

                try:

                    result = generate_account_health(
                        selected_account_id
                    )

                    # ========================================
                    # Account ID
                    # ========================================

                    st.subheader(
                        "Account"
                    )

                    st.write(
                        selected_account_id
                    )

                    # ========================================
                    # Executive Summary
                    # ========================================

                    st.subheader(
                        "📊 Executive Summary"
                    )

                    st.info(
                        result.get(
                            "executive_summary",
                            "No summary available."
                        )
                    )

                    # ========================================
                    # Ticket Count
                    # ========================================

                    col1, col2 = st.columns(2)

                    with col1:

                        st.metric(
                            "Tickets — Last 90 Days",
                            result.get(
                                "ticket_count_last_90_days",
                                0
                            )
                        )

                    with col2:

                        st.metric(
                            "Dataset Reference Date",
                            result.get(
                                "dataset_reference_date",
                                "Unknown"
                            )[:10]
                        )

                    # ========================================
                    # Risks
                    # ========================================

                    st.subheader(
                        "⚠️ Open Risks & Flagged Issues"
                    )

                    risks = result.get(
                        "open_risks_and_flagged_issues",
                        []
                    )

                    if not risks:

                        st.success(
                            "No major risks identified."
                        )

                    else:

                        for index, risk in enumerate(
                            risks,
                            start=1
                        ):

                            severity = risk.get(
                                "severity",
                                "Unknown"
                            )

                            with st.expander(
                                f"{index}. "
                                f"{risk.get('risk', 'Unknown Risk')} "
                                f"— {severity}"
                            ):

                                st.write(
                                    "**Evidence:**"
                                )

                                st.write(
                                    risk.get(
                                        "evidence",
                                        ""
                                    )
                                )

                                quote = risk.get(
                                    "ticket_quote",
                                    ""
                                )

                                if quote:

                                    st.write(
                                        "**Ticket Quote:**"
                                    )

                                    st.write(
                                        f'> "{quote}"'
                                    )

                    # ========================================
                    # TAM Talking Points
                    # ========================================

                    st.subheader(
                        "🗣️ Recommended TAM Talking Points"
                    )

                    talking_points = result.get(
                        "recommended_tam_talking_points",
                        []
                    )

                    for point in talking_points:

                        st.markdown(
                            f"- {point}"
                        )

                except Exception as e:

                    st.error(
                        f"Account health analysis failed: {e}"
                    )

    else:

        st.warning(
            "No accounts shared between accounts.json "
            "and tickets.json were found."
        )


# ============================================================
# Footer
# ============================================================

st.sidebar.markdown("---")

st.sidebar.caption(
    "Zycus AI Support System"
)

st.sidebar.caption(
    "RAG • Ticket Triage • Account Health"
)