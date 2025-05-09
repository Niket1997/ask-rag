# Retrieval script that retrieves the data from the Qdrant vector database
# and uses the data to answer the user's question
# steps:
# 1. get the input query from user
# 2. get the vector embeddings assocoated with that query
# 3. generate a system prompt using the retrieved vector embeddings
# 4. query the LLM to answer user's question

from app.core.constants import (
    collection_exists,
    embeddings,
    get_vector_store,
    info_logger,
    llm,
    qdrant_client,
    redis_client,
)
from langchain_qdrant import QdrantVectorStore

# Similarity threshold for considering a document relevant
SIMILARITY_THRESHOLD = 0.60


# Retrieve the answer from LLM based on the query
# and the documents retrieved from Qdrant
# TODO: we can use memoization here (mem0) to cache the results using the user's email as the key
def retrieve_answer(query: str, user_email: str) -> str:
    system_prompt = """
    You are a helpful AI assistant that can answer user's questions based on the documents provided.
    If there aren't any related documents, or if the user's query is not related to the documents, then you can provide the answer based on your knowledge.        Think carefully before answering the user's question.

    For example:
    User: What is the capital of France? You answer this because the user's query is not related to the documents.
    You: The capital of France is Paris.

    User: How to invest in stocks? You answer this because the user's query is related to the documents.
    You: You can invest in stocks by opening a demat account with a stockbroker. 
    """
    # get the vector embeddings assocoated with that query
    try:
        if collection_exists(user_email):
            vector_store = get_vector_store(user_email)

            # Get documents with their similarity scores
            docs = vector_store.similarity_search_with_score(
                query, k=5
            )

            for doc, score in docs:
                if score >= SIMILARITY_THRESHOLD:
                    system_prompt += f"""
                    Document: {doc.page_content}
                    """

        messages = [("system", system_prompt), ("user", query)]

        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        return f"An error occurred: {e}"
