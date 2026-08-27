import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI


# --------------------------------------------------
# 1. Load .env from project root
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")


# --------------------------------------------------
# 2. Get Gemini API key
# --------------------------------------------------

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file")


# --------------------------------------------------
# 3. Create Gemini LLM
# --------------------------------------------------

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=api_key,
    temperature=0
)


# --------------------------------------------------
# 4. Generate answer
# --------------------------------------------------

def generate_answer(question, context):

    prompt = f"""
You are a customer support AI assistant.

Answer the user's question using ONLY the information
provided in the knowledge-base context.

Rules:
- Do not invent information.
- Do not use outside knowledge.
- If the answer is not available in the context,
  say that the information was not found in the knowledge base.
- Give a clear and concise support answer.

Knowledge Base Context:
{context}

User Question:
{question}

Answer:
"""

    response = llm.invoke(prompt)

    if isinstance(response.content, list):
        return "".join(
            block["text"]
            for block in response.content
            if block.get("type") == "text"
        )

    return response.content

# --------------------------------------------------
# 5. Test LLM
# --------------------------------------------------

if __name__ == "__main__":

    test_context = """
    ### Report exports truncated at 1000 rows

    This is a plan limit, not a bug.

    Starter plan: 1,000 rows per export.

    Upgrade to Professional or above for higher limits.

    Workaround (Starter): split the export into
    multiple date ranges.
    """

    test_question = "Why are AnalyticsHub reports truncated at 1000 rows?"

    answer = generate_answer(
        test_question,
        test_context
    )

    print("=" * 80)
    print("ANSWER")
    print("=" * 80)
    print(answer)