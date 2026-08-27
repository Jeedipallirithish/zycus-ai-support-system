import chromadb
from sentence_transformers import SentenceTransformer


# Load the same embedding model used to create the KB embeddings
embedding_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


# Connect to the locally stored Chroma database
kb_vector_db = chromadb.PersistentClient(
    path=r"C:\Users\Rithish\Desktop\Zycus_Project_ass\kb_vector_database"
)


# Open the existing collection
kb_collection = kb_vector_db.get_collection(
    name="customer_support_knowledge_base"
)


def retrieve_kb(query, top_k=3):

    # Convert the user's question into a vector
    query_embedding = embedding_model.encode(query).tolist()

    # Search the vector database
    results = kb_collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results


if __name__ == "__main__":

    query = "Why are AnalyticsHub reports truncated at 1000 rows?"

    results = retrieve_kb(query, top_k=3)

    for i, document in enumerate(results["documents"][0]):

        print("=" * 80)
        print(f"RESULT {i + 1}")
        print(document)

        print("\nMETADATA:")
        print(results["metadatas"][0][i])