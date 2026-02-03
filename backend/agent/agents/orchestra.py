from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.types import Command

from agent.agents.researcher import research_agent_graph
from agent.rag.retriever import retrieve_documents  # New Import
from agent.state import DeepAgentState
from agent.tools.general import think_tool
from agent.tools.search import tavily_search
from agent.tools.todos import read_todos, write_todos

model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0)

MAIN_INSTRUCTIONS = """
You are the main orchestrator agent. Your job is to help the user by coordinating tasks.

<Tools>
- File system tools: ls, read_file, write_file
- TODO tools: write_todos, read_todos
- Search: tavily_search (for quick lookups)
- Reflection: think_tool
- Research Delegation: delegate_research (for complex topics)
- Context Retrieval: retrieve_context (for user files/policies)
</Tools>

<Strategy>
1. If the user asks a simple question, answer it directly or use `tavily_search`.
2. If the user asks for a complex research task, use `delegate_research`.
3. If the user asks about uploaded files, documents, or company policies, use `retrieve_context`.
4. Keep track of files and TODOs.
</Strategy>
"""


@tool
def delegate_research(topic: str) -> str:
    """Delegate a deep research task to the specialist researcher agent."""
    return f"Delegated research on: {topic}"


@tool
def retrieve_context(query: str, user_id: str, session_id: str | None = None) -> str:
    """Retrieve relevant context from uploaded documents."""
    docs = retrieve_documents(query, user_id, session_id)
    if not docs:
        return "No relevant documents found."

    formatted_docs = []
    for d in docs:
        meta = d.metadata
        formatted_docs.append(f"[Source: {meta.get('source')} | Type: {meta.get('type')}]\n{d.page_content}")

    return "\n\n".join(formatted_docs)


main_tools = [
    # ls, read_file, write_file,
    write_todos,
    read_todos,
    think_tool,
    tavily_search,
    delegate_research,
    retrieve_context,
]

# Bind tools to model
model_with_tools = model.bind_tools(main_tools)


# Nodes
def supervisor_node(state: DeepAgentState) -> Command:
    messages = state["messages"]
    if not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=MAIN_INSTRUCTIONS)] + messages

    response = model_with_tools.invoke(messages)
    return {"messages": [response]}


def researcher_node(state: DeepAgentState) -> Command:
    messages = state["messages"]
    last_message = messages[-1]

    topic = "General Research"
    tool_call_id = None

    if hasattr(last_message, "tool_calls"):
        for tc in last_message.tool_calls:
            if tc["name"] == "delegate_research":
                topic = tc["args"].get("topic", "General Research")
                tool_call_id = tc["id"]
                break

    inputs = {"messages": [HumanMessage(content=f"Please research: {topic}")], "files": state.get("files", {})}

    result = research_agent_graph.invoke(inputs)
    research_output = result["messages"][-1].content

    tool_msg = ToolMessage(
        content=f"Researcher Report:\n{research_output}", tool_call_id=tool_call_id, name="delegate_research"
    )

    return {"messages": [tool_msg], "files": result.get("files", {})}


# Router
def router(state: DeepAgentState) -> Literal["tools", "researcher", "__end__"]:
    messages = state["messages"]
    last_message = messages[-1]

    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return "__end__"

    for tc in last_message.tool_calls:
        if tc["name"] == "delegate_research":
            return "researcher"

    return "tools"


# Graph
workflow = StateGraph(DeepAgentState)

workflow.add_node("supervisor", supervisor_node)
workflow.add_node("tools", ToolNode(main_tools))
workflow.add_node("researcher", researcher_node)

workflow.add_edge(START, "supervisor")
workflow.add_conditional_edges("supervisor", router)
workflow.add_edge("tools", "supervisor")
workflow.add_edge("researcher", "supervisor")

main_agent_graph = workflow.compile()
