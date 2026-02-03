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

# Initialize LLM WITHOUT tools binding - using JSON-based tool calling in the prompt
# Changed from gpt-oss-120b (forces tool_choice) to llama-3.3 which works with JSON prompts
if GROQ_API_KEY:
    llm = ChatGroq(
        temperature=0.1,  # Slight temperature for more natural responses
        model_name="llama-3.3-70b-versatile",
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

def record_token_usage(source: str, tokens: int, user_id: int = None):
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
                tokens=tokens,
                user_id=user_id
            )
            session.add(usage)
            session.commit()
    except Exception as e:
        logger.error(f"Failed to record token usage: {e}")

async def generate_response_stream(query: str, context_chunks: list = None, history: list = None, user_id: int = None):
    """
    Async Generator that yields agent steps and final response.
    Uses JSON-based tool calling (not native function calling) for compatibility with gpt-oss.
    """
    logger.info(f"[LLM] Starting generate_response_stream with query: {query[:50]}...")
    
    context_text = ""
    sources = []
    
    # 1. Prepare Context from RAG
    if context_chunks:
        logger.info(f"[LLM] Processing {len(context_chunks)} context chunks")
        try:
            context_text = "\n\n".join([c.content for c in context_chunks])
            sources = [c.document.title if c.document else "Internal Doc" for c in context_chunks]
            logger.info(f"[LLM] Context prepared: {len(context_text)} chars")
        except Exception as e:
            logger.error(f"[LLM] Error preparing context: {e}")
            sources = ["Internal Documents"]
        record_token_usage("retriever", len(context_text) // 4, user_id=user_id)
    else:
        logger.info("[LLM] No context chunks provided")

    # 2. Build system prompt
    current_date = datetime.utcnow().strftime("%Y-%m-%d")
    system_content = f"""You are VaultMind AI, a deep reasoning agent with access to tools.

## TODAY'S DATE: {current_date}

## YOUR KNOWLEDGE BASE (from user's documents)
{context_text if context_text else "⚠️ No relevant documents found in Knowledge Base."}

---

## 🚨 CRITICAL RULES (MUST FOLLOW)

### Rule 1: NEVER USE YOUR TRAINING DATA FOR CURRENT INFO
Your training data is OUTDATED. You MUST search the web for:
- **Current presidents/leaders** (they change!)
- **Prices** (Bitcoin, stocks, crypto, commodities)
- **Today's news, events, weather**
- **Anything with "actual", "hoy", "now", "current"**

### Rule 2: MULTI-QUESTION = MULTI-STEP
If the user asks 2+ questions, you MUST:
1. Create a TODO plan first
2. Execute ONE search per topic that needs current info
3. Only answer after ALL searches are done

### Rule 3: KNOWLEDGE BASE FIRST
For questions about the user's documents/policies, check the Knowledge Base above FIRST.
Only search web if the info is NOT in the Knowledge Base.

---

## AVAILABLE ACTIONS (use JSON format)

### 1. Plan (for multi-questions)
{{"thought": "User asked X questions, I need to solve each", "todo": ["[ ] Task 1", "[ ] Task 2"], "action": "plan"}}

### 2. Web Search (for current info)
{{"thought": "Need current price/president/news", "action": "search", "query": "bitcoin price USD today"}}

### 3. Final Answer (plain markdown, NO JSON)
Just write your answer in clean markdown. Use headers, lists, bold for structure.

---

## EXAMPLE: Multi-Question with DB + Web (SPANISH)

**User**: "¿Qué documentos tengo en la base, quién es el presidente de Argentina, y cuánto vale Bitcoin?"

**Step 1** (Plan):
{{"thought": "3 preguntas: 1) Docs en DB (revisar Knowledge Base), 2) Presidente Argentina (buscar web - cambia), 3) Precio BTC (buscar web - cambia)", "todo": ["[ ] Revisar Knowledge Base para docs", "[ ] Buscar presidente Argentina", "[ ] Buscar precio Bitcoin"], "action": "plan"}}

**Step 2** (Search president):
{{"thought": "Buscando presidente actual de Argentina", "action": "search", "query": "presidente de Argentina 2026"}}

**Step 3** (Search BTC):
{{"thought": "Ahora busco precio Bitcoin", "action": "search", "query": "Bitcoin price USD January 2026"}}

**Step 4** (Final answer in markdown):
## Respuesta

### 1. Documentos en tu Base de Conocimiento
Según la base de datos, tienes los siguientes documentos: [lista de la KB]

### 2. Presidente de Argentina
Según mi búsqueda, el presidente actual es [nombre] (fuente: [url])

### 3. Precio de Bitcoin
El precio actual de Bitcoin es $XX,XXX USD (fuente: [url])



---

## EXAMPLE 2: English (Multi-Question)

**User**: "Who is the president of France and what is the capital of Australia?"

**Step 1** (Plan):
{{"thought": "2 questions: 1) President of France (search needed), 2) Capital of Australia (static knowledge but better to confirm)", "todo": ["[ ] Search president of France", "[ ] Search capital of Australia"], "action": "plan"}}

**Step 2** (Search):
{{"thought": "Searching for current French president", "action": "search", "query": "current president of France 2026"}}

**Step 3** (Final Answer):
## Response

### 1. President of France
The current president of France is [Name] (Source: [url]).

### 2. Capital of Australia
The capital of Australia is Canberra.


---

## 🌐 LANGUAGE RULE (CRITICAL!)
**MATCH THE USER'S LANGUAGE EXACTLY:**
- If user writes in English → Answer in English
- If user writes in Spanish → Answer in Spanish  
- If user writes in French → Answer in French
- etc.

Never default to Spanish. Always mirror the exact language the user uses in their message.

---

## ❌ WRONG BEHAVIORS (never do this)
- Answering "el presidente es X" without searching (your data is OLD!)
- Giving a BTC price from memory (prices change every second!)
- Answering multi-questions in 1 step without planning
- Showing JSON in the final answer
- Answering in Spanish when user wrote in English (ALWAYS MATCH USER'S LANGUAGE!)

---

## OUTPUT FORMAT
- **RESPOND IN THE SAME LANGUAGE THE USER USED** (English → English, Spanish → Spanish)
- Final answer = clean Markdown (headers, lists, bold)
- Include sources when you searched the web
- Never show raw JSON to the user

You have up to 20 steps. Use as many as needed. DO NOT RUSH."""

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
    max_iterations = 20  # Deep agent mode - allows for multi-step reasoning
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
            logger.info(f"[LLM] Iteration {iteration+1}: Calling Groq API...")
            response = await llm.ainvoke(messages)
            logger.info(f"[LLM] Iteration {iteration+1}: Got response from Groq")
            
            # Record usage
            usage = getattr(response, 'response_metadata', {}).get('usage', {})
            if usage.get('total_tokens', 0) > 0:
                record_token_usage("groq", usage['total_tokens'], user_id=user_id)
            
            content = response.content.strip() if response.content else ""
            logger.info(f"[LLM] Response content length: {len(content)}")
            
            if not content:
                # Retry once
                messages.append(AIMessage(content=""))
                messages.append(HumanMessage(content="Please provide a valid JSON response with your plan or answer."))
                continue

            # Try to parse JSON - find ALL JSON blocks
            # Regex to find ALL JSON objects in content
            json_matches = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content)
            parsed_json = None
            
            # Try each JSON object, prioritizing 'search' actions
            search_json = None
            plan_json = None
            any_json = None
            
            for match in json_matches:
                try:
                    candidate = json.loads(match)
                    if isinstance(candidate, dict):
                        action = candidate.get("action", "")
                        if action == "search" and not search_json:
                            search_json = candidate
                        elif action == "plan" and not plan_json:
                            plan_json = candidate
                        elif not any_json:
                            any_json = candidate
                except:
                    continue
            
            # Prioritize: search > plan > any other
            parsed_json = search_json or plan_json or any_json
            
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
                    yield {"type": "status", "content": f"🔍 Searching: {query_term}"}
                    
                    search_res = perform_web_search(query_term)
                    
                    collected_info.append(f"Search '{query_term}': {search_res[:500]}...")
                    
                    # Add result to history
                    messages.append(AIMessage(content=content)) # Add the JSON reasoning
                    messages.append(HumanMessage(content=f"Search Results:\n{search_res}\n\nNow continue with your plan. If you have more searches to do, do them. Otherwise provide the final answer."))
                    
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
                    # Plan update - add to messages and MUST continue
                    messages.append(AIMessage(content=content))
                    # Force continuation - ask for next step
                    messages.append(HumanMessage(content="Good plan. Now execute it step by step. Start with the first search action."))
                    continue
                
                else:
                    # Unknown action (like "knowledge_base_check") - treat as intermediate step
                    # Add to messages and continue
                    messages.append(AIMessage(content=content))
                    messages.append(HumanMessage(content="Continue with your plan. Execute the next search or provide the final answer if done."))
                    add_step(f"Intermediate step: {action}", "intermediate")
                    continue
            
            # If NO JSON found (text response) = final answer
            if not parsed_json:
                final_response = content
                add_step("Generated final response", "answer")
                break 
            
        except Exception as e:
            error_str = str(e)
            logger.error(f"[LLM] Exception in agent loop: {error_str}")
            
            # Handle Groq's tool_choice error - retry without expecting tool call
            if "tool_use_failed" in error_str or "Tool choice is none" in error_str:
                logger.warning(f"Tool choice error, retrying with direct answer prompt: {e}")
                add_step("Retrying with direct response...", "retry")
                try:
                    # Add instruction to answer directly
                    messages.append(HumanMessage(content="Please answer directly as plain text, do not use any tools or JSON formatting. Just provide your answer."))
                    record_api_call()
                    response = await llm.ainvoke(messages)
                    content = response.content.strip() if response.content else ""
                    if content:
                        final_response = content
                        add_step("Generated direct response", "answer")
                        break
                except Exception as retry_e:
                    logger.error(f"Retry also failed: {retry_e}")
            
            logger.error(f"Error in agent loop: {e}")
            add_step(f"Error: {str(e)[:100]}", "error")
            break

    if not final_response:
         # Check if we have a partial answer in the last JSON
        if collected_info:
             final_response = "I gathered this info:\n" + "\n".join(collected_info)
        else:
             final_response = "I couldn't generate a complete response."
    
    # Clean markdown output - remove any remaining JSON blocks
    final_response = re.sub(r'```json.*?```', '', final_response, flags=re.DOTALL)
    # Also remove inline JSON patterns that might slip through
    final_response = re.sub(r'\{"action"[^}]+\}', '', final_response)
    final_response = final_response.strip()

    yield {
        "type": "answer",
        "response": final_response,
        "sources": list(set(sources)),
        "reasoning_data": {"steps": reasoning_steps}
    }
