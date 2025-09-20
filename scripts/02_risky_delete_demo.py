"""
⚠️ DANGEROUS SQL Agent Demo - ALLOWS ANY SQL INCLUDING DELETE (Gemini Version) ⚠️

This script is an unsafe demonstration of executing ANY SQL via an agent,
now using Google's Gemini Flash 2.5 model (langchain_google_genai).
DO NOT use this pattern in production.
"""

# ⚠️ DEMO ONLY — allows arbitrary SQL including DELETE
import sqlalchemy  # SQL database engine and connection management
from langchain_google_genai import ChatGoogleGenerativeAI  # Gemini chat model integration
from langchain.agents import initialize_agent, AgentType  # Agent creation and types
from langchain.tools import BaseTool  # Base class for creating custom tools
from pydantic import BaseModel, Field  # Data validation and serialization
from typing import Type  # Type hinting for better code documentation
from langchain.schema import SystemMessage  # System message formatting for agents
from dotenv import load_dotenv  # Environment variable loading

# Load environment variables from .env file (including GOOGLE_API_KEY)
load_dotenv()

# Database Configuration
DB_URL = "sqlite:///SQLAgent/sql_agent_class.db"

# Create Database Engine
engine = sqlalchemy.create_engine(DB_URL)

class SQLInput(BaseModel):
    """
    Pydantic model for SQL tool input validation.

    WARNING: This accepts any SQL string and does NOT sanitize it.
    """
    sql: str = Field(description="Any SQL statement.")  # Field with description for AI understanding

class ExecuteAnySQLTool(BaseTool):
    """
    DANGEROUS Custom Tool - Executes ANY SQL Without Restrictions.
    """
    name: str = "execute_any_sql"
    description: str = "Executes ANY SQL, including DML/DDL. DEMO ONLY."
    args_schema: Type[BaseModel] = SQLInput

    def _run(self, sql: str) -> str | dict:
        """
        Execute SQL statement with NO safety restrictions.
        Returns structured results for SELECT, or success message for non-SELECT.
        """
        with engine.connect() as conn:
            try:
                result = conn.exec_driver_sql(sql)

                # DANGEROUS: Automatically commit all transactions
                try:
                    conn.commit()
                except Exception:
                    # Some SQLAlchemy dialects may not support explicit commit on a connection object;
                    # this is intentionally blunt for the demo.
                    pass

                try:
                    rows = result.fetchall()
                    cols = rows[0].keys() if rows else []
                    return {"columns": list(cols), "rows": [list(r) for r in rows]}
                except Exception:
                    return "OK (no result set)"
            except Exception as e:
                return f"ERROR: {e}"

    def _arun(self, *args, **kwargs):
        """Async not implemented."""
        raise NotImplementedError

# System Message Configuration
system = """You are a database assistant. You are allowed to execute ANY SQL the user requests. (DEMO ONLY)"""

# Initialize Language Model -> Gemini Flash 2.5
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

# Create Tool Instance
tool = ExecuteAnySQLTool()

# Create Agent with Dangerous Tool
# We use AgentType.OPENAI_FUNCTIONS for the function-calling style agent;
# with Gemini the model wrapper will handle function-style calls similarly.
agent = initialize_agent(
    tools=[tool],  # Provide the dangerous SQL tool
    llm=llm,  # Gemini model for decision making
    agent=AgentType.OPENAI_FUNCTIONS,  # function-calling-style agent
    verbose=True,  # Show execution steps for demonstration
    agent_kwargs={"system_message": SystemMessage(content=system)}  # Set dangerous permissions
)

# DANGEROUS OPERATION: Execute DELETE command
# This will actually delete data from the database if run.
print(agent.invoke({"input": "Delete all orders"})["output"])
