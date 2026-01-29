import os
import logging
import time
from datetime import datetime
from collections import deque
from dotenv import load_dotenv

# Load .env file
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, "../../.env")
if os.path.exists(env_path):
    load_dotenv(env_path, override=True)

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from tavily import TavilyClient
import json
import re

# Initialize Clients
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

logger = logging.getLogger(__name__)

# Rate limiting configuration
MAX_REQUESTS_PER_MINUTE = 20
RATE_LIMIT_WINDOW = 60  # seconds
api_call_timestamps = deque()  # Track API call times

def check_rate_limit() -> tuple[bool, int]:
    """
    Check if we're approaching the rate limit.
    Returns: (can_proceed, remaining_calls)
    """
    current_time = time.time()
    
    # Remove timestamps older than 1 minute
    while api_call_timestamps and current_time - api_call_timestamps[0] > RATE_LIMIT_WINDOW:
        api_call_timestamps.popleft()
    
    remaining = MAX_REQUESTS_PER_MINUTE - len(api_call_timestamps)
    can_proceed = remaining > 0
    
    return can_proceed, remaining

def record_api_call():
    """Record an API call timestamp."""
    api_call_timestamps.append(time.time())

if not GROQ_API_KEY:
    logger.warning("GROQ_API_KEY not set. LLM generation will fail.")
else:
    logger.info("GROQ_API_KEY loaded successfully")

tavily_client = TavilyClient(api_key=TAVILY_API_KEY) if TAVILY_API_KEY else None

def perform_web_search(query: str, max_results: int = 3) -> str:
    """Search the web using Tavily."""
    if not tavily_client:
        return "Search unavailable (No API Key)."
    
    try:
        results = tavily_client.search(query=query, max_results=max_results, search_depth="advanced")
        context = []
        for res in results.get("results", []):
            context.append(f"Source: {res['title']} ({res['url']})\nContent: {res['content']}")
        return "\n\n".join(context) if context else "No results found."
    except Exception as e:
        logger.error(f"Tavily search failed: {e}")
        return f"Search failed: {str(e)}"

# Initialize LLM WITHOUT tools binding - gpt-oss has issues with native function calling
# We'll use JSON-based tool calling in the prompt instead
if GROQ_API_KEY:
    llm = ChatGroq(
        temperature=0,
        model_name="openai/gpt-oss-120b",
        api_key=GROQ_API_KEY
    )
else:
    llm = None

def load_prompt(filename: str) -> str:
    """Load a prompt from the backend/agent/prompts directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(current_dir, "../../agent/prompts", filename)
    try:
        with open(prompt_path, "r") as f:
            return f.read().strip()
    except Exception as e:
        logger.error(f"Failed to load prompt {filename}: {e}")
        return ""

def record_token_usage(source: str, tokens: int):
    """Record token usage to database for analytics."""
    from sqlmodel import Session
    from app.database import engine
    from app.models import TokenUsage
    
    current_hour = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    
    try:
        with Session(engine) as session:
            usage = TokenUsage(
                hour=current_hour,
                source=source,
                tokens=tokens
            )
            session.add(usage)
            session.commit()
    except Exception as e:
        logger.error(f"Failed to record token usage: {e}")

async def generate_response_stream(query: str, context_chunks: list = None, history: list = None):
    """
    Async Generator that yields agent steps and final response.
    Uses JSON-based tool calling (not native function calling) for compatibility with gpt-oss.
    """
    context_text = ""
    sources = []
    
    # 1. Prepare Context from RAG
    if context_chunks:
        context_text = "\n\n".join([c.content for c in context_chunks])
        try:
            sources = [c.document.title if c.document else "Internal Doc" for c in context_chunks]
        except:
            sources = ["Internal Documents"]
        record_token_usage("retriever", len(context_text) // 4)

    # 2. Build system prompt
    system_content = f"""You are VaultMind AI, a helpful assistant.

PRIORITY ORDER:
1. **Knowledge Base FIRST**: ALWAYS check the context below FIRST. For general/vague questions (like "find users", "show data"), the answer is likely in the Knowledge Base.
2. **Web Search**: Only use search if you need CURRENT/external info not in the Knowledge Base.

TOOLS:
- To search the web: {{"action": "search", "query": "your query"}}
- To answer: Just write your response as plain text.

SIMPLE TO-DO (optional, for complex tasks only):
If the task has multiple steps, you can track progress:
{{"thought": "...", "todo": ["[x] Step done", "[ ] Step pending"], "action": "..."}}
Mark completed items with [x]. Keep it brief!

RULES:
- Be CONCISE. Max 2-3 paragraphs.
- Check Knowledge Base context BEFORE searching the web.
- Don't over-plan simple questions. Just answer directly.
- You can format your final answer using **Markdown** (headers, bold, lists, code blocks) or plain text.

Context from Knowledge Base:
{context_text if context_text else "No documents found."}

Respond in the user's language."""

    messages = [SystemMessage(content=system_content)]
    
    # Add conversation history
    if history:
        for msg in history:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role in ["ai", "assistant"]:
                if msg.content:
                    messages.append(AIMessage(content=msg.content))
    
    # Add the current query
    messages.append(HumanMessage(content=query))
    
    # 3. Agent loop
    max_iterations = 8 # Increased for planning steps
    reasoning_steps = []
    final_response = ""
    collected_info = []
    step_counter = 0
    
    def add_step(content: str, action: str = "status", todo_list: list = None):
        nonlocal step_counter
        step_counter += 1
        step_data = {
            "step": step_counter,
            "action": action,
            "content": content,
            "timestamp": str(datetime.utcnow())
        }
        if todo_list:
            step_data["todo_list"] = todo_list
        reasoning_steps.append(step_data)
    
    # Initial status
    add_step("Initializing Agent & Planning...", "analyze")
    yield {"type": "status", "content": "Planning..."}
    
    if context_chunks:
        add_step(f"Loaded {len(context_chunks)} docs from Knowledge Base", "retriever")

    for iteration in range(max_iterations):
        if not llm:
            add_step("LLM not configured", "error")
            yield {"type": "error", "content": "LLM not configured"}
            return
        
        # Check rate limit
        can_proceed, remaining = check_rate_limit()
        if not can_proceed:
            add_step("Rate limit reached", "rate_limit")
            yield {"type": "status", "content": "Rate limit reached..."}
            final_response = "⚠️ Rate limit reached. Please try again later."
            break
        
        try:
            record_api_call()
            # Call the model
            response = await llm.ainvoke(messages)
            
            # Record usage
            usage = getattr(response, 'response_metadata', {}).get('usage', {})
            if usage.get('total_tokens', 0) > 0:
                record_token_usage("groq", usage['total_tokens'])
            
            content = response.content.strip() if response.content else ""
            
            if not content:
                # Retry once
                messages.append(AIMessage(content=""))
                messages.append(HumanMessage(content="Please provide a valid JSON response with your plan or answer."))
                continue

            # Try to parse JSON
            # Regex to find JSON block if mixed with text
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            parsed_json = None
            
            if json_match:
                try:
                    parsed_json = json.loads(json_match.group(0))
                except:
                    pass
            
            # Parsing logic
            if parsed_json:
                action = parsed_json.get("action", "")
                thought = parsed_json.get("thought", "")
                todo_list = parsed_json.get("todo") or parsed_json.get("todo_list") or []
                
                # Show thought if present
                if thought:
                    add_step(thought, "thought", todo_list)
                    yield {"type": "status", "content": f"💭 {thought[:80]}"}
                
                # Show plan only if present (simplified)
                if todo_list:
                    plan_items = [item for item in todo_list if isinstance(item, str)]
                    if plan_items:
                        plan_str = " | ".join(plan_items[:5])  # Max 5 items, inline
                        add_step(plan_str, "plan", todo_list)
                        yield {"type": "status", "content": f"📋 {plan_str}"}

                if action == "search":
                    query_term = parsed_json.get("query", query)
                    add_step(f"Searching: {query_term}", "search")
                    yield {"type": "status", "content": f"Searching: {query_term}"}
                    
                    search_res = perform_web_search(query_term)
                    
                    collected_info.append(f"Search '{query_term}': {search_res[:200]}...")
                    
                    # Add result to history
                    messages.append(AIMessage(content=content)) # Add the JSON reasoning
                    messages.append(HumanMessage(content=f"Search Results:\n{search_res}"))
                    
                    add_step("Processed search results", "search_complete")
                    continue
                
                elif action == "answer":
                    # Done
                    final_response = parsed_json.get("content", "")
                    if final_response:
                        add_step("Generated final response", "answer")
                        break # Done loop
                    # If empty content, fall through to text check or loop
                
                elif action == "plan":
                    # Just an update
                    messages.append(AIMessage(content=content))
                    continue
            
            # If valid JSON wasn't "answer" or "search", or if NO JSON found (text response)
            if not parsed_json:
                final_response = content
                add_step("Generated final response", "answer")
                break
            
            # If we acted (search/plan), loop continues. 
            
        except Exception as e:
            logger.error(f"Error in agent loop: {e}")
            add_step(f"Error: {str(e)}", "error")
            break

    if not final_response:
         # Check if we have a partial answer in the last JSON
        if collected_info:
             final_response = "I gathered this info:\n" + "\n".join(collected_info)
        else:
             final_response = "I couldn't generate a complete response."

    yield {
        "type": "answer",
        "response": final_response,
        "sources": list(set(sources)),
        "reasoning_data": {"steps": reasoning_steps}
    }
