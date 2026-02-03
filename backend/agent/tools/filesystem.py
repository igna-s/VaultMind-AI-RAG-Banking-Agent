from typing import Annotated

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from agent.state import DeepAgentState


@tool
def ls(state: Annotated[DeepAgentState, InjectedState]) -> str:
    """List files in the virtual file system."""
    files = state.get("files", {})
    if not files:
        return "No files found."
    return f"Files: {', '.join(files.keys())}"


@tool
def read_file(file_path: str, state: Annotated[DeepAgentState, InjectedState], limit: int = 2000) -> str:
    """Read contents of a file."""
    files = state.get("files", {})
    if file_path not in files:
        return f"Error: File '{file_path}' not found."
    content = files[file_path]
    return content[:limit] + ("..." if len(content) > limit else "")


@tool
def write_file(
    file_path: str,
    content: str,
    state: Annotated[DeepAgentState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Write content to a file."""
    files = state.get("files", {}).copy()
    files[file_path] = content

    return Command(
        update={
            "files": files,
            "messages": [ToolMessage(f"Successfully wrote to {file_path}", tool_call_id=tool_call_id)],
        }
    )
