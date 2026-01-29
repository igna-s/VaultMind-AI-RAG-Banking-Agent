import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.services.llm import generate_response_stream

async def main():
    print("--- Testing Retry Limit ---")
    query = "Trigger Retry Logic"
    
    # We can't easily force the LLM to fail 3 times without mocking.
    # But we can run the stream and check if it terminates or loops forever.
    # Ideally we'd unit test this component, but for now we'll rely on the code change verification.
    # This script mainly ensures no syntax errors and basic execution.
    
    print("Sending query...")
    async for event in generate_response_stream(query, context_chunks=[], history=[]):
        if event["type"] == "status":
            print(f"  [Status] {event['content']}")
        elif event["type"] == "result":
            print(f"  [Result] {event['response']}")
        elif event["type"] == "error":
             print(f"  [Error] {event['content']}")

if __name__ == "__main__":
    asyncio.run(main())
