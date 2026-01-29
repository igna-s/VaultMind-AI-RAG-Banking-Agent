import asyncio
from dotenv import load_dotenv
import os
import json

load_dotenv()

from app.services.llm import generate_response_stream

async def test_complex():
    print("Starting complex query test...")
    # This query requires at least two searches: "Juan Domingo Peron" and "Bitcoin Price"
    query = "quien es peron, y cuanto vale el btc hoy"
    print(f"Query: {query}")
    
    gen = generate_response_stream(query=query, context_chunks=[], history=[])
    
    steps = 0
    final_response = None
    
    try:
        for event in gen:
            if event['type'] == 'status':
                print(f"STATUS: {event['content']}")
                if "Reasoning" in event['content']:
                    steps += 1
            elif event['type'] == 'result':
                final_response = event['response']
                print(f"FINAL RESPONSE: {final_response[:100]}...")
            elif event['type'] == 'error':
                 print(f"ERROR EVENT: {event['content']}")
    except Exception as e:
        print(f"EXCEPTION: {e}")

    print(f"Total Reasoning Steps: {steps}")
    if steps > 2 and final_response and "could not generate" not in final_response:
        print("SUCCESS: Complex query resolved with multiple steps.")
    else:
        print("FAILURE: Query failed or took too few steps.")

if __name__ == "__main__":
    asyncio.run(test_complex())
