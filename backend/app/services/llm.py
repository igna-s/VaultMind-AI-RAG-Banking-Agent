import os
import logging
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from tavily import TavilyClient

# Initialize Clients
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

logger = logging.getLogger(__name__)

if not GROQ_API_KEY:
    logger.warning("GROQ_API_KEY not set. LLM generation will fail.")

llm = ChatGroq(
    temperature=0,
    model_name="llama3-70b-8192",
    api_key=GROQ_API_KEY
)

tavily_client = TavilyClient(api_key=TAVILY_API_KEY) if TAVILY_API_KEY else None

def perform_web_search(query: str, max_results: int = 3) -> str:
    """Search the web using Tavily."""
    if not tavily_client:
        return "Search unavailable (No API Key)."
    
    try:
        results = tavily_client.search(query=query, max_results=max_results, search_depth="advanced")
        # Format results
        context = []
        for res in results.get("results", []):
            context.append(f"Source: {res['title']} ({res['url']})\nContent: {res['content']}")
        return "\n\n".join(context)
    except Exception as e:
        logger.error(f"Tavily search failed: {e}")
        return "Search failed."

def generate_response(query: str, context_chunks: list = None, history: list = None) -> dict:
    """
    Generate a response using Groq.
    - If context provided -> RAG Answer.
    - If no context -> Web Search -> Answer.
    """
    context_text = ""
    sources = []
    
    # 1. Prepare Context
    if context_chunks:
        context_text = "\n\n".join([c.content for c in context_chunks])
        # Unpack SQLModel objects if needed, assuming they possess 'document' relation
        try:
            sources = [c.document.filename for c in context_chunks]
        except:
            sources = ["Internal Documents"]
            
        system_prompt = (
            "You are a helpful banking assistant. Use the following retrieved context to answer the user's question. "
            "If the answer is not in the context, say so, but do not make up facts."
            "\n\nContext:\n" + context_text
        )
    else:
        # 2. Fallback to Web Search
        if TAVILY_API_KEY:
            print("No local context found. Searching web...")
            search_context = perform_web_search(query)
            context_text = search_context
            sources = ["Web Search (Tavily)"]
            
            system_prompt = (
                "You are a helpful banking assistant. The user is asking a question that wasn't found in their private documents. "
                "Use the following web search results to answer if relevant."
                "\n\nWeb Search Results:\n" + search_context
            )
        else:
             # Basic conversational fallback
             sources = ["LLM Knowledge"]
             system_prompt = "You are a helpful banking assistant. You do not have access to specific documents right now."

    # 3. Construct Messages
    messages = [SystemMessage(content=system_prompt)]
    
    # Optional: Add history (simplified for MVP)
    if history:
        # Assuming history is list of Message sqlmodels
        for msg in history[-5:]: # Last 5
            if msg.role == 'user':
                messages.append(HumanMessage(content=msg.content))
            else:
                messages.append(AIMessage(content=msg.content))
    
    messages.append(HumanMessage(content=query))
    
    # 4. Generate
    try:
        response = llm.invoke(messages)
        content = response.content
    except Exception as e:
        logger.error(f"Groq generation failed: {e}")
        content = "I'm sorry, I'm having trouble connecting to my brain (Groq) right now."
    
    return {
        "response": content,
        "sources": sources,
        "used_web_search": not bool(context_chunks)
    }
