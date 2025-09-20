"""
Simple SQL Agent Demo (Gemini Version)

This script demonstrates the basic usage of LangChain's SQL agent capabilities
using Google's Gemini Flash 2.5 model instead of OpenAI.
"""

# Import necessary LangChain components for SQL agent functionality
from langchain_google_genai import ChatGoogleGenerativeAI  # Gemini chat model integration
from langchain_community.utilities import SQLDatabase  # Database connection wrapper
from langchain.agents.agent_toolkits import SQLDatabaseToolkit, create_sql_agent  # SQL agent tools
from dotenv import load_dotenv; load_dotenv()  # Load environment variables from .env file

# Initialize the Language Model
# ChatGoogleGenerativeAI: Creates a Gemini model instance for the agent
# Parameters:
#   - model: Specifies which Gemini model to use (gemini-2.5-flash)
#   - temperature: Controls randomness (0 = deterministic, 1 = more creative)
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

# Create Database Connection
# SQLDatabase.from_uri: Creates a database wrapper from a connection string
db = SQLDatabase.from_uri("sqlite:///SQLAgent/sql_agent_class.db")

# Create SQL Agent
# create_sql_agent: Factory function that creates a complete SQL-capable agent
# For Gemini we set agent_type="google-genai-tools"
agent = create_sql_agent(
    llm=llm,
    toolkit=SQLDatabaseToolkit(db=db, llm=llm),
    agent_type="google-genai-tools",  # ✅ Gemini-compatible agent type
    verbose=True
)

# Execute a Sample Query
print(agent.invoke({"input": "Delete first 5 customers with their regions."})["output"])
