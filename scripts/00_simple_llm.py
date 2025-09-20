"""
Simple Agent Demo - Agent Framework Without Tools (Gemini Version)

This script is the same as before but uses Google's Gemini Flash 2.5 API
instead of OpenAI's GPT models.
"""

from dotenv import load_dotenv; load_dotenv()

# ✅ Use Gemini instead of OpenAI
from langchain_google_genai import ChatGoogleGenerativeAI  # Gemini wrapper
from langchain.agents import initialize_agent, AgentType
from langchain.schema import SystemMessage
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

class DummyInput(BaseModel):
    query: str = Field(description="Any input - this tool does nothing")

class DummyTool(BaseTool):
    name: str = "dummy_tool"
    description: str = "A dummy tool that does nothing - used only for agent framework demo"
    args_schema: Type[BaseModel] = DummyInput

    def _run(self, query: str) -> str:
        return "This is a dummy tool that does nothing. I can only provide information through conversation."

    def _arun(self, *args, **kwargs):
        raise NotImplementedError

def main():
    print("🤖 Initializing Gemini Flash 2.5 model for agent...")

    # ✅ Gemini Flash 2.5 instead of OpenAI GPT
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0
    )

    system_message = SystemMessage(
        content="""You are a helpful AI assistant specializing in explaining technology concepts.
        You provide clear, concise explanations and are always friendly and professional.
        You have access to one dummy tool, but you should prefer to answer questions directly through conversation."""
    )

    dummy_tool = DummyTool()

    print("🎯 Creating agent with dummy tool (conversational focus)...")
    agent = initialize_agent(
        tools=[dummy_tool],
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        agent_kwargs={
            "system_message": system_message
        }
    )

    print("\n💬 Agent conversation (dummy tool available but focus on chat):")
    print("=" * 60)

    question1 = "What is an AI agent and how does it differ from a chatbot?"
    print(f"Question: {question1}")

    response1 = agent.invoke({"input": question1})
    print(f"Agent Response: {response1['output']}")

    print("\n🔄 Follow-up question:")
    print("=" * 60)

    question2 = "Can you give me a simple example of how agents work?"
    print(f"Question: {question2}")

    response2 = agent.invoke({"input": question2})
    print(f"Agent Response: {response2['output']}")

    print("\n🔍 Agent configuration:")
    print("=" * 60)
    print(f"Agent type: {type(agent)}")
    print(f"Available tools: {len(agent.tools)} (dummy tool only)")
    print(f"LLM model: gemini-2.5-flash")
    print(f"Agent verbose mode: {agent.verbose}")

    print("\n⚖️  Comparison: Direct LLM vs Agent Framework:")
    print("=" * 60)

    test_question = "Explain the concept of machine learning in one sentence."

    print("Direct LLM response:")
    direct_response = llm.invoke(test_question)
    print(f"  {direct_response.content}")

    print("\nAgent framework response:")
    agent_response = agent.invoke({"input": test_question})
    print(f"  {agent_response['output']}")

    print("\n✅ Simple agent demo (Gemini Flash 2.5) completed!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure your .env file contains GOOGLE_API_KEY")
        print("2. Verify your virtual environment is activated")
        print("3. Check that you've installed requirements: pip install -r requirements.txt")
        print("4. Ensure you have internet connection for API calls")
