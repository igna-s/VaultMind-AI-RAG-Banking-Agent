import os
import json
import uuid
import base64
import httpx
from datetime import datetime
from typing import Literal, Annotated, Optional

from markdownify import markdownify
from pydantic import BaseModel, Field
from tavily import TavilyClient
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool, InjectedToolArg, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from agent.state import DeepAgentState

# Initialize models
# User specified using Groq instead of OpenAI
summarization_model = ChatGroq(model="llama-3.1-8b-instant", temperature=0.0)
tavily_client = TavilyClient()

class Summary(BaseModel):
    """Schema for webpage content summarization."""
    filename: str = Field(description="Name of the file to store.")
    summary: str = Field(description="Key learnings from the webpage.")

def get_today_str() -> str:
    return datetime.now().strftime("%a %b %-d, %Y")

SUMMARIZE_PROMPT = """Summarize the following webpage content. 
Also suggest a concise filename (ending in .md) to save this content.
Content: {webpage_content}
Date: {date}
"""

def summarize_webpage_content(webpage_content: str) -> Summary:
    try:
        structured_model = summarization_model.with_structured_output(Summary)
        summary_and_filename = structured_model.invoke([
            HumanMessage(content=SUMMARIZE_PROMPT.format(
                webpage_content=webpage_content[:10000], # Limit context
                date=get_today_str()
            ))
        ])
        return summary_and_filename
    except Exception as e:
        # Fallback if structured output fails or model issue
        return Summary(
            filename="search_result.md",
            summary=webpage_content[:500] + "..."
        )

def run_tavily_search(search_query: str, max_results: int = 1, topic="general", include_raw_content=True) -> dict:
    return tavily_client.search(
        search_query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic
    )

def process_search_results(results: dict) -> list[dict]:
    processed_results = []
    HTTPX_CLIENT = httpx.Client(timeout=30.0)

    for result in results.get('results', []):
        url = result['url']
        try:
            response = HTTPX_CLIENT.get(url)
            if response.status_code == 200:
                raw_content = markdownify(response.text)
                summary_obj = summarize_webpage_content(raw_content)
            else:
                raw_content = result.get('raw_content', '')
                summary_obj = Summary(
                    filename="URL_error.md",
                    summary=result.get('content', 'Error reading URL.')
                )
        except Exception:
            raw_content = result.get('raw_content', '')
            summary_obj = Summary(
                filename="connection_error.md",
                summary=result.get('content', 'Could not fetch URL.')
            )

        # Uniquify filename
        uid = base64.urlsafe_b64encode(uuid.uuid4().bytes).rstrip(b"=").decode("ascii")[:8]
        name, ext = os.path.splitext(summary_obj.filename)
        summary_obj.filename = f"{name}_{uid}{ext}"

        processed_results.append({
            'url': result['url'],
            'title': result['title'],
            'summary': summary_obj.summary,
            'filename': summary_obj.filename,
            'raw_content': raw_content,
        })
    return processed_results

@tool
def tavily_search(
    query: str,
    state: Annotated[DeepAgentState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
    max_results: Annotated[int, InjectedToolArg] = 1,
    topic: Annotated[Literal["general", "news", "finance"], InjectedToolArg] = "general",
) -> Command:
    """Search web and save detailed results to files while returning minimal context."""
    
    search_results = run_tavily_search(query, max_results=max_results, topic=topic)
    processed_results = process_search_results(search_results)
    
    files = state.get("files", {}).copy()
    saved_files = []
    summaries = []
    
    for result in processed_results:
        filename = result['filename']
        file_content = f"""# Search Result: {result['title']}

**URL:** {result['url']}
**Query:** {query}
**Date:** {get_today_str()}

## Summary
{result['summary']}

## Raw Content
{result['raw_content'] if result['raw_content'] else 'No raw content available'}
"""
        files[filename] = file_content
        saved_files.append(filename)
        summaries.append(f"- {filename}: {result['summary']}...")
    
    summary_text = f"""🔍 Found {len(processed_results)} result(s) for '{query}':

{chr(10).join(summaries)}

Files: {', '.join(saved_files)}
"""

    return Command(
        update={
            "files": files,
            "messages": [ToolMessage(summary_text, tool_call_id=tool_call_id)]
        }
    )
