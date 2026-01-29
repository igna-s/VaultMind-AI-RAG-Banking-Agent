from datetime import datetime
from typing import Literal

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent

from agent.state import DeepAgentState
from agent.tools.search import tavily_search
from agent.tools.general import think_tool
# from agent.tools.filesystem import read_file

# --- Configuración de modelos ---
model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0)

def get_today_str() -> str:
    return datetime.now().strftime("%a %b %-d, %Y")

RESEARCHER_INSTRUCTIONS = """
You are a research assistant conducting research on the user's input topic. For context, today's date is {date}.

<Task>
Your job is to use tools to gather information about the user's input topic.
You can use any of the tools provided to you to find resources that can help answer the research question.
</Task>

<Available Tools>
1. **tavily_search**: For conducting web searches.
2. **think_tool**: For reflection.
3. **read_file**: To read content you saved.

**CRITICAL: Use think_tool after each search to reflect on results and plan next steps**
</Available Tools>

<Limit>
Stop after you have found sufficient information or if you have searched 5 times.
</Limit>
"""

research_tools = [tavily_search, think_tool] # read_file removed

# Create the agent
# functionality-wise, create_react_agent returns a CompiledGraph
research_agent_graph = create_react_agent(
    model, 
    research_tools, 
    state_schema=DeepAgentState,
    prompt=RESEARCHER_INSTRUCTIONS.format(date=get_today_str())
)
