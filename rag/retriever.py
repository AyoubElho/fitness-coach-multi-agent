from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.tools import tool

from config import VECTORSTORE_DIR, EMBEDDING_MODEL, RETRIEVER_K

_vectorstore = None

def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        _vectorstore = Chroma(
            persist_directory=str(VECTORSTORE_DIR),
            embedding_function=embeddings,
        )
    return _vectorstore

@tool(
    description="Search the fitness knowledge base for exercise, training, nutrition, recovery, and physical activity guidance."
)
def search_fitness_knowledge(query: str) -> str:
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search(query, k=RETRIEVER_K)

    if not results:
        return "No relevant information found in the knowledge base."

    formatted = "\n\n---\n\n".join(
        f"[Source: {doc.metadata.get('source', 'unknown')}]\n{doc.page_content}"
        for doc in results
    )
    return formatted
