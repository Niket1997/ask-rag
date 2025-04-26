# Retrieval script that retrieves the data from the Qdrant vector database
# and uses the data to answer the user's question
# steps:
# 1. get the input query from user
# 2. get the vector embeddings assocoated with that query
# 3. generate a system prompt using the retrieved vector embeddings
# 4. query the LLM to answer user's question

from langchain_qdrant import QdrantVectorStore

from app.core.constants import embeddings, llm, qdrant_client


# Retrieve the answer from LLM based on the query
# and the documents retrieved from Qdrant
def retrieve_answer(query: str) -> str:
    # get the vector embeddings assocoated with that query
    vector_store = QdrantVectorStore(
        collection_name="test-stock-investing-101",
        embedding=embeddings,
        client=qdrant_client,
    )

    found_docs = vector_store.similarity_search(query, k=5)

    system_prompt = f"""
    You are a helpful AI assistant that can asnwer user's questions based on the documents provided.
    If there aren't any related documents, then you can provide the answer based on your knowledge.
    Think carefully before answering the user's question.
    Documents: {'\n'.join([doc.page_content for doc in found_docs])}
    """

    messages = [("system", system_prompt), ("user", query)]

    response = llm.invoke(messages)
    return response.content
