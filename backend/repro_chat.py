import asyncio
import os
import sys
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Add backend to sys.path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.services.llm import generate_response_stream
from app.models import ChatMessage

async def main():
    print("--- Starting Multi-Turn Chat Test ---")
    
    # Turn 1
    query1 = "Quien es Peron?"
    print(f"\nUser: {query1}")
    
    history = []
    response1 = ""
    
    print("AI (Turn 1):")
    async for event in generate_response_stream(query1, context_chunks=[], history=[]):
        if event["type"] == "status":
            print(f"  [Status] {event['content']}")
        elif event["type"] == "result":
            response1 = event["response"]
            print(f"  [Result] {response1}")
            
    if not response1:
        print("FAILED TURN 1")
        return

    # Mock History
    history.append(ChatMessage(role="user", content=query1))
    history.append(ChatMessage(role="ai", content=response1))
    
    # Turn 2
    query2 = "Y cuanto vale el BTC?"
    print(f"\nUser: {query2}")
    
    print("AI (Turn 2):")
    async for event in generate_response_stream(query2, context_chunks=[], history=history):
        if event["type"] == "status":
            print(f"  [Status] {event['content']}")
        elif event["type"] == "result":
            print(f"  [Result] {event['response']}")
            print(f"  [Steps] {len(event['reasoning_data']['steps'])}")

if __name__ == "__main__":
    asyncio.run(main())
