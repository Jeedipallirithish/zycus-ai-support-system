from retrieval import retrieve_kb
from llm import generate_answer


def rag_answer(query, top_k=3):

    # 1. Retrieve relevant KB chunks
    results = retrieve_kb(query, top_k=top_k)

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    # 2. Combine retrieved chunks into one context
    context = "\n\n".join(documents)

    # 3. Generate answer using retrieved context
    answer = generate_answer(
        question=query,
        context=context
    )

    return answer, metadatas


if __name__ == "__main__":

    query = "Why are AnalyticsHub reports truncated at 1000 rows?"

    answer, sources = rag_answer(query)

    print("=" * 80)
    print("FINAL ANSWER")
    print("=" * 80)
    print(answer)

    print("\n" + "=" * 80)
    print("SOURCES")
    print("=" * 80)

    for source in sources:
        print(source)