import os
import sys

# Adjust path to import agent modules
current_dir = os.path.dirname(os.path.abspath(__file__))
agent_dir = os.path.dirname(current_dir)
if agent_dir not in sys.path:
    sys.path.append(agent_dir)

# Load env vars EARLY
from dotenv import load_dotenv

load_dotenv(os.path.join(agent_dir, ".env"))

from agent.agents.orchestra import delegate_research  # noqa: E402
from agent.tools.filesystem import ls, read_file, write_file  # noqa: E402
from agent.tools.general import think_tool  # noqa: E402
from agent.tools.search import tavily_search  # noqa: E402
from agent.tools.todos import read_todos, write_todos  # noqa: E402


# Mock checking of tool calls
def test_tool(name, func, args, state=None, tool_call_id="test_id"):
    print(f"\n--- Testing {name} ---")
    try:
        if state is None:
            state = {"files": {"existing.txt": "content"}, "todos": [], "messages": [], "remaining_steps": 5}

        # Determine if tool needs injection
        # We can inspect type hints but for this test script we know which ones need what.

        input_args = args.copy()

        # Tools with InjectedState (ls, read_file, write_file, write_todos, read_todos, tavily_search)
        # require 'state' in input if invoked manually outside of a prebuilt node.
        if name in ["ls", "read_file", "write_file", "write_todos", "read_todos", "tavily_search"]:
            input_args["state"] = state

        # Tools with InjectedToolCallId (write_file, tavily_search)
        # These strictly require the input to be a ToolCall dict if invoked directly via invoke?
        # Let's try passing 'tool_call_id' in args first.
        if name in ["write_file", "tavily_search"]:
            input_args["tool_call_id"] = tool_call_id

        # However, tavily_search throws a specific error if not a full tool call object.
        # Let's wrap it for those.
        if name in ["tavily_search", "write_file"]:
            # Construct a specific payload that BaseTool understands as "I am being called by a model"
            # OR we just call the underlying function? No, can't easily access.
            # workaround: The Pydantic model for input expects 'tool_call_id'.
            # The error suggests we need to pass a dict representing the ToolCall.

            tool_call_payload = {
                "name": name,
                "args": args,  # Original args without injections?
                "id": tool_call_id,
                "type": "tool_call",
            }

            # Manually inject state into args because direct invocation doesn't always handle InjectedState binding automatically
            # unless we use the specific LangGraph runtime hooks.
            tool_call_payload["args"]["state"] = state

            # Let's try providing state in config AND tool_call_id in the payload.

            res = func.invoke(tool_call_payload, config={"configurable": {"state": state}})

        else:
            # For simpler tools, just pass args + state
            # Note: If we pass 'state' in args, it might work if schema allows.
            res = func.invoke(input_args)

        print(f"Result Type: {type(res)}")
        if hasattr(res, "update"):
            print(f"Command Update: {res.update}")
        else:
            print(f"Result: {res}")

        print(f"✅ {name} PASSED")
    except Exception as e:
        print(f"❌ {name} FAILED: {e}")
        import traceback

        traceback.print_exc()


def run_tests():
    # 1. LS
    test_tool("ls", ls, {})

    # 2. Write File
    test_tool("write_file", write_file, {"file_path": "test_output.txt", "content": "Hello World"})

    # 3. Read File
    # We need to simulate the state having the file.
    # Since tools return updates but don't mutate state in-place usually (unless using a real graph manager),
    # we manually update the state for the next test.
    state_with_file = {
        "files": {"test_output.txt": "Hello World", "existing.txt": "content"},
        "todos": [],
        "messages": [],
        "remaining_steps": 5,
    }
    test_tool("read_file", read_file, {"file_path": "test_output.txt"}, state=state_with_file)

    # 4. Write Todos
    todos = [{"content": "Test task", "status": "pending"}]
    test_tool("write_todos", write_todos, {"todos": todos})

    # 5. Read Todos
    state_with_todos = {
        "files": {},
        "todos": [{"content": "Test task", "status": "pending"}],
        "messages": [],
        "remaining_steps": 5,
    }
    test_tool("read_todos", read_todos, {}, state=state_with_todos)

    # 6. Think Tool
    test_tool("think_tool", think_tool, {"reflection": "This is a test thought"})

    # 7. Delegate Research
    test_tool("delegate_research", delegate_research, {"topic": "PyTest"})

    # 8. Tavily Search (Requires API Key)
    # Check if key exists
    from dotenv import load_dotenv

    load_dotenv(os.path.join(agent_dir, ".env"))

    if os.getenv("TAVILY_API_KEY"):
        test_tool("tavily_search", tavily_search, {"query": "python langchain", "max_results": 1})
    else:
        print("\n⚠️ Skipping Tavily Search (No API Key)")


if __name__ == "__main__":
    run_tests()
