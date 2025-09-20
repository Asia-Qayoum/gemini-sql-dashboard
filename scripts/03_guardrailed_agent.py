"""
Safe SQL Agent with Security Guardrails (Gemini Flash 2.5)

Same secure tool/agent logic as your original script, now using Google's
Gemini Flash 2.5 model via langchain_google_genai.
"""

import re  # Regular expressions for SQL pattern matching and validation
import sqlalchemy  # Database engine and connection management
from pydantic import BaseModel, Field  # Data validation and serialization
from langchain.tools import BaseTool  # Base class for creating custom tools
from langchain_google_genai import ChatGoogleGenerativeAI  # <-- Gemini wrapper
from langchain.agents import initialize_agent, AgentType  # Agent creation and configuration
from langchain_community.utilities import SQLDatabase  # Database schema inspection utilities
from langchain.schema import SystemMessage  # System message formatting for agents
from typing import Type  # Type hinting for better code documentation
from dotenv import load_dotenv; load_dotenv()  # Environment variable loading

# NOTE: put your Gemini API key in .env as GOOGLE_API_KEY=your_key_here

# Database Configuration
DB_URL = "sqlite:///sql_agent_class.db"

# Create Database Engine
engine = sqlalchemy.create_engine(DB_URL)

class QueryInput(BaseModel):
    """
    Pydantic model for safe SQL query input validation.

    This model defines the expected input structure for the safe SQL execution tool.
    It includes clear documentation about what types of queries are allowed.

    Attributes:
        sql (str): A single read-only SELECT statement with automatic LIMIT bounds
    """
    sql: str = Field(description="A single read-only SELECT statement, bounded with LIMIT when returning many rows.")

class SafeSQLTool(BaseTool):
    """
    SECURE SQL Tool - Only Allows Read-Only SELECT Operations
    """
    name: str = "execute_sql"
    description: str = "Execute exactly one SELECT statement; DML/DDL is forbidden."
    args_schema: Type[BaseModel] = QueryInput

    def _run(self, sql: str) -> str | dict:
        """
        Execute SQL with comprehensive security validation.
        """
        # Step 1: Clean and Normalize Input
        s = sql.strip().rstrip(";")

        # Step 2: Dangerous Operation Detection
        if re.search(r"\b(INSERT|UPDATE|DELETE|DROP|TRUNCATE|ALTER|CREATE|REPLACE)\b", s, re.I):
            return "ERROR: write operations are not allowed."

        # Step 3: Multiple Statement Prevention
        if ";" in s:
            return "ERROR: multiple statements are not allowed."

        # Step 4: Whitelist Validation
        if not re.match(r"(?is)^\s*select\b", s):
            return "ERROR: only SELECT statements are allowed."

        # Step 5: Automatic LIMIT Injection
        if not re.search(r"\blimit\s+\d+\b", s, re.I) and not re.search(r"\bcount\(|\bgroup\s+by\b|\bsum\(|\bavg\(|\bmax\(|\bmin\(", s, re.I):
            s += " LIMIT 200"  # Default limit of 200 rows

        # Step 6: Safe SQL Execution
        try:
            with engine.connect() as conn:
                result = conn.exec_driver_sql(s)
                rows = result.fetchall()
                cols = list(result.keys()) if result.keys() else []
                return {"columns": cols, "rows": [list(r) for r in rows]}
        except Exception as e:
            return f"ERROR: {e}"

    def _arun(self, *args, **kwargs):
        raise NotImplementedError

# Database Schema Inspection
db = SQLDatabase.from_uri(DB_URL, include_tables=["customers","orders","order_items","products","refunds","payments"])

# Extract Database Schema Information
schema_context = db.get_table_info()

# System Message Configuration (include actual schema_context)
system = f"You are a careful analytics engineer for SQLite. Use only these tables.\n\n{schema_context}"

# Initialize Language Model -> Gemini Flash 2.5
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

# Create Safe Tool Instance
safe_tool = SafeSQLTool()

# Create Secure Agent
agent = initialize_agent(
    tools=[safe_tool],  # Only provide the safe SQL tool
    llm=llm,            # Gemini model for decision making
    agent=AgentType.OPENAI_FUNCTIONS,  # function-calling-style agent (works with LangChain wrappers)
    verbose=True,
    agent_kwargs={"system_message": SystemMessage(content=system)}
)

# Test Safe Operations
print(agent.invoke({"input": "Show 5 customers with their sign-up dates and regions."})["output"])
print(agent.invoke({"input": "Delete all orders older than July 1, 2025."})["output"])
