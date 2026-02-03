import operator
from typing import Annotated, Any

from langgraph.graph import MessagesState


def merge_dicts(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    return {**a, **b}


class DeepAgentState(MessagesState):
    """Estado del agente que incluye archivos, todos y resultados de investigación."""

    files: Annotated[dict[str, str], merge_dicts]
    todos: Annotated[
        list[dict[str, Any]], lambda x, y: y if y else x
    ]  # Replace strategy for TODO list usually, or append? Let's stick to replace/update for now.
    remaining_steps: Annotated[int, operator.add]

    # State for the sub-agent to communicate back specifically if needed,
    # though messages are usually enough.
