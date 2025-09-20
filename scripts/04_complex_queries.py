"""
Advanced Analytics SQL Agent with Complex Query Capabilities (Gemini Flash 2.5)

Same secure analytics logic as your original script, now using Google's
Gemini Flash 2.5 model via langchain_google_genai.
"""

# Load environment variables first (including GOOGLE_API_KEY)
from dotenv import load_dotenv; load_dotenv()

# Core LangChain imports for agent functionality
from langchain_google_genai import ChatGoogleGenerativeAI  # Gemini wrapper
from langchain.agents import initialize_agent, AgentType  # Agent creation and configuration
from langchain.schema import SystemMessage  # System message formatting for agents
from langchain_community.utilities import SQLDatabase  # Database schema inspection utilities

# Data validation and tool creation imports
from pydantic import BaseModel, Field  # Data validation and serialization
from langchain.tools import BaseTool  # Base class for creating custom tools
from typing import Type  # Type hinting for better code documentation

# Database and utility imports
import sqlalchemy  # Database engine and connection management
import re  # Regular expressions for SQL pattern matching and validation

# NOTE: Put your Gemini API key in .env as GOOGLE_API_KEY=your_key_here

# Database Configuration
DB_URL = "sqlite:///sql_agent_class.db"

# Create Database Engine
engine = sqlalchemy.create_engine(DB_URL)

class QueryInput(BaseModel):
    """
    Pydantic model for analytics query input validation.
    """
    sql: str = Field(description="A single read-only SELECT statement, bounded with LIMIT when returning many rows.")

class SafeSQLTool(BaseTool):
    """
    Advanced Analytics SQL Tool - Secure Complex Query Execution
    """
    name: str = "execute_sql"
    description: str = "Execute one read-only SELECT."
    args_schema: Type[BaseModel] = QueryInput

    def _run(self, sql: str) -> str | dict:
        """
        Execute complex analytics SQL with comprehensive security validation.
        """
        # Step 1: Input Normalization
        s = sql.strip().rstrip(";")

        # Step 2: Security Validation Layer
        if re.search(r"\b(INSERT|UPDATE|DELETE|DROP|TRUNCATE|ALTER|CREATE|REPLACE)\b", s, re.I):
            return "ERROR: write operations are not allowed."

        if ";" in s:
            return "ERROR: multiple statements are not allowed."

        if not re.match(r"(?is)^\s*select\b", s):
            return "ERROR: only SELECT statements are allowed."

        # Step 3: Performance Optimization
        if not re.search(r"\blimit\s+\d+\b", s, re.I) and not re.search(
            r"\bcount\(|\bgroup\s+by\b|\bsum\(|\bavg\(|\bmax\(|\bmin\(", s, re.I
        ):
            s += " LIMIT 200"  # Conservative limit for analytics queries

        # Step 4: Secure Query Execution
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

# Advanced Database Schema Configuration
db = SQLDatabase.from_uri(
    DB_URL,
    include_tables=["customers", "orders", "order_items", "products", "refunds", "payments"]
)

# Extract Comprehensive Schema Information
schema_context = db.get_table_info()

# Advanced System Message with Business Logic (include actual schema_context)
system = (
    "You are a careful analytics engineer for SQLite.\n"
    "Use only listed tables. Revenue = sum(quantity*unit_price_cents) - refunds.amount_cents.\n\n"
    f"Schema:\n{schema_context}"
)

# Initialize Advanced Language Model -> Gemini Flash 2.5
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

# Create Analytics Tool Instance
tool = SafeSQLTool()

# Create Advanced Analytics Agent
agent = initialize_agent(
    tools=[tool],
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,  # function-calling-style agent (works with LangChain wrappers)
    verbose=True,
    agent_kwargs={"system_message": SystemMessage(content=system)}
)

# Complex Analytics Query Demonstrations
print(agent.invoke({"input": "Top 5 products by gross revenue (before refunds). Include product name and total_cents."})["output"])
print(agent.invoke({"input": "Weekly net revenue for the last 6 weeks. Return week_start, net_cents."})["output"])
print(agent.invoke({"input": "For each customer, show their first_order_month, total_orders, last_order_date. Return 10 rows."})["output"])
print(agent.invoke({"input": "Rank customers by lifetime net revenue (sum of items minus refunds). Show rank, customer, net_cents. Top 10."})["output"])

# Multi-Turn Conversation Demonstrations
print(agent.invoke({"input": "What categories drive the most revenue?"})["output"])
print(agent.invoke({"input": "Break the top category down by product with totals."})["output"])
