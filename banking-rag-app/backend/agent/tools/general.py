from langchain_core.tools import tool

@tool
def think_tool(reflection: str) -> str:
    """Tool for strategic reflection on research progress and decision-making."""
    return f"Reflection recorded: {reflection}"

# 'task' tool removed as we are using graph delegation now.
