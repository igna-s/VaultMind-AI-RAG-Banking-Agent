from typing import Annotated, Any

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from agent.state import DeepAgentState


@tool
def write_todos(
    todos: list[dict[str, Any]],
    state: Annotated[DeepAgentState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Create or update the TODO list."""
    return Command(
        update={"todos": todos, "messages": [ToolMessage("Successfully updated TODOs.", tool_call_id=tool_call_id)]}
    )


@tool
def read_todos(state: Annotated[DeepAgentState, InjectedState]) -> str:
    """Read the current TODO list."""
    todos = state.get("todos", [])
    if not todos:
        return "No TODOs found."

    result = "Current TODO List:\n"
    for i, t in enumerate(todos, 1):
        status_icon = "✅" if t.get("status") == "completed" else "⏳"
        result += f"{i}. {status_icon} {t.get('content')} ({t.get('status')})\n"
    return result
