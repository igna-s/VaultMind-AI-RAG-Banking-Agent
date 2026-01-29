import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

import asyncio

async def test_model_async():
    print("Testing openai/gpt-oss-120b (Async)...")
    try:
        llm = ChatGroq(
            temperature=0,
            model_name="openai/gpt-oss-120b",
            api_key=api_key
        )
        msg = [HumanMessage(content="Hello, are you functional? Reply with 'Yes'.")]
        response = await llm.ainvoke(msg)
        print(f"Response: {response.content}")
        print("Model works (Async)!")
    except Exception as e:
        print(f"Model Failed (Async): {e}")

if __name__ == "__main__":
    asyncio.run(test_model_async())
