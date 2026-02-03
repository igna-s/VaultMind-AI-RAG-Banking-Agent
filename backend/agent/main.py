import logging
import os
import sys

from dotenv import load_dotenv

# Load env vars
current_dir = os.path.dirname(os.path.abspath(__file__))
# .env is now in backend/ (parent of agent/)
dotenv_path = os.path.join(os.path.dirname(current_dir), ".env")
load_dotenv(dotenv_path)

# Setup path
# If running as 'python -m agent.main' from 'backend/', sys.path[0] is 'backend/'
# standard imports 'from agent.xxx' work fine.

from langchain_core.messages import HumanMessage  # noqa: E402
from langgraph.checkpoint.memory import MemorySaver  # noqa: E402
from langgraph.checkpoint.postgres import PostgresSaver  # noqa: E402
from psycopg_pool import ConnectionPool  # noqa: E402

from agent.agents.orchestra import MAIN_INSTRUCTIONS  # noqa: E402
from agent.db import init_db  # noqa: E402
from agent.utils import format_messages, show_prompt  # noqa: E402

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    show_prompt(MAIN_INSTRUCTIONS, title="Deep Agent Instructions")

    user_query = "Comparison between React and SolidJS"
    if len(sys.path) > 1 and len(sys.argv) > 1:
        user_query = " ".join(sys.argv[1:])

    print(f"\n🏁 Starting Agent with query: {user_query}\n")

    # DB Persistence Setup
    db_url = os.getenv("DATABASE_URL")
    checkpointer = None
    pool = None

    if db_url:
        try:
            # Initialize Tables
            init_db()

            # Setup Postgres Checkpointer
            # We need a connection string (libpq format) or a pool.
            # PostgresSaver.from_conn_string(db_url) handles it.
            # But wait, checking LangGraph docs...
            # It usually requires a synchronous connection or pool for sync graph execution.
            # For async, AsyncConnectionPool.
            # Our graph execution in main is sync (app.stream).

            pool = ConnectionPool(conninfo=db_url)
            checkpointer = PostgresSaver(pool)

            # First time setup for checkpointer tables if needed?
            # PostgresSaver usually expects tables. .setup() method exists.
            checkpointer.setup()

            print("✅ Postgres Persistence Enabled.")
        except Exception as e:
            logger.error(f"Failed to connect to Database: {e}")
            print("⚠️ Database connection failed. Falling back to MemorySaver.")
            checkpointer = MemorySaver()
    else:
        print("⚠️ DATABASE_URL not found. Using MemorySaver.")
        checkpointer = MemorySaver()

    # Compile Graph
    from agent.agents.orchestra import workflow

    app = workflow.compile(checkpointer=checkpointer)

    thread_id = "group_thread_1"  # In a real app, this comes from user session
    config = {"configurable": {"thread_id": thread_id}}

    print(f"--- Thread ID: {thread_id} ---\n")

    try:
        for event in app.stream(
            {"messages": [HumanMessage(content=user_query)], "files": {}, "todos": []}, config=config
        ):
            for key, value in event.items():
                print(f"\n👉 Node: {key}")
                if "messages" in value:
                    format_messages(value["messages"])
    finally:
        if pool:
            pool.close()

    print("\n" + "=" * 50)
    print("✅ EXECUTION FINISHED")
    print("=" * 50)
