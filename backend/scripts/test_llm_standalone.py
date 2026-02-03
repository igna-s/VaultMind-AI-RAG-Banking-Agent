#!/usr/bin/env python3
"""
Standalone LLM test script - runs the agent loop without the full backend.
Usage: python -m scripts.test_llm_standalone "¿Cuál es el precio del BTC?"
       python -m scripts.test_llm_standalone "What's the BTC price and who is Argentina's president?"
"""

import asyncio
import os
import sys

# Setup path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.insert(0, backend_dir)

from dotenv import load_dotenv  # noqa: E402

load_dotenv(os.path.join(backend_dir, ".env"))


async def test_agent(query: str):
    """Run the agent with the given query and print results."""
    from app.services.llm import generate_response_stream

    print(f"\n{'=' * 60}")
    print(f"🔍 QUERY: {query}")
    print(f"{'=' * 60}\n")

    step_count = 0

    async for event in generate_response_stream(query):
        event_type = event.get("type")

        if event_type == "status":
            step_count += 1
            print(f"  Step {step_count}: {event['content']}")

        elif event_type == "error":
            print(f"  ❌ ERROR: {event['content']}")

        elif event_type == "answer":
            print(f"\n{'=' * 60}")
            print("📝 FINAL RESPONSE:")
            print(f"{'=' * 60}")
            print(event["response"])

            if event.get("sources"):
                print(f"\n📚 Sources: {', '.join(event['sources'])}")

            reasoning = event.get("reasoning_data", {})
            steps = reasoning.get("steps", [])
            print(f"\n📊 Total reasoning steps: {len(steps)}")

            # Show step breakdown
            if steps:
                print("\n📋 Step breakdown:")
                for s in steps:
                    action = s.get("action", "unknown")
                    content = s.get("content", "")[:60]
                    print(f"   {s.get('step', '?')}. [{action}] {content}...")


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        # Default multi-question test
        query = "¿Cuánto vale el Bitcoin hoy y quién es el presidente de Argentina?"

    print("\n" + "=" * 60)
    print("🧪 VaultMind AI - Standalone LLM Test")
    print("=" * 60)

    # Check API keys
    groq_key = os.getenv("GROQ_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")

    print(f"✅ GROQ_API_KEY: {'Set' if groq_key else '❌ MISSING'}")
    print(f"✅ TAVILY_API_KEY: {'Set' if tavily_key else '⚠️ Missing (web search disabled)'}")

    if not groq_key:
        print("\n❌ Cannot run test - GROQ_API_KEY is required!")
        sys.exit(1)

    asyncio.run(test_agent(query))

    print("\n" + "=" * 60)
    print("✅ TEST COMPLETE")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
