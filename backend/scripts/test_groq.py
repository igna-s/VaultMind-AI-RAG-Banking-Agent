import os
import sys
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# Load env
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
env_path = os.path.join(os.path.dirname(__file__), '../../Database/.env')
load_dotenv(env_path)

def test_groq():
    api_key = os.getenv("GROQ_API_KEY")
    print(f"🔑 Checking Key: {api_key[:5]}...{api_key[-4:]} (Length: {len(api_key)})")
    
    try:
        llm = ChatGroq(
            temperature=0,
            model_name="llama-3.3-70b-versatile",
            api_key=api_key
        )
        
        print("🤖 Invoking Groq...")
        messages = [HumanMessage(content="Hello, are you online?")]
        response = llm.invoke(messages)
        
        print(f"✅ Success! Response: {response.content}")
        
    except Exception as e:
        print(f"❌ Groq Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_groq()
