import os
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings

load_dotenv()

def get_retriever(role: str = "researcher"):
    """
    Creates and returns a LangChain retriever connected to Pinecone.
    
    RBAC Enforcement:
    - If role is 'researcher', a filter is applied to exclude 'admin' content.
    - If role is 'admin', no role-based filter is applied.
    """
    index_name = os.environ.get("PINECONE_INDEX_NAME")
    api_key = os.environ.get("PINECONE_API_KEY")
    
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
        base_url=os.environ.get("OPENAI_BASE_URL")
    )
    
    vectorstore = PineconeVectorStore.from_existing_index(
        index_name=index_name,
        embedding=embeddings,
        pinecone_api_key=api_key
    )
    
    search_kwargs = {"k": 5}
    
    # Inject RBAC metadata filter
    if role == "researcher":
        # Exclude any document where role is 'admin'
        search_kwargs["filter"] = {"role": {"$ne": "admin"}}
        print(f"[Retriever] Initialized with 'researcher' RBAC filter (excluding admin content)")
    else:
        print(f"[Retriever] Initialized with 'admin' access (no role filter)")
        
    return vectorstore.as_retriever(search_kwargs=search_kwargs)
