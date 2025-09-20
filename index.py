import os
import sqlite3
import pandas as pd
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase

# ===================
# PAGE CONFIG & STYLING
# ===================
st.set_page_config(
    page_title="📝 Gemini SQL Dashboard ",
    page_icon="🗄️",
    layout="wide"
)

# Background image
bg_image_url = "https://images.unsplash.com/photo-1529070538774-1843cb3265df?auto=format&fit=crop&w=1950&q=80"
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("{bg_image_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: white !important;
    }}
    .block-container {{
        background-color: rgba(0,0,0,0.75);
        padding: 2rem;
        border-radius: 1rem;
    }}
    .stDataFrame {{
        background-color: rgba(255,255,255,0.95);
        color: black !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📝 Gemini SQL Dashboard See Tables  And Ask  your Queries")
st.caption("Query your SQLite database in natural language with Gemini AI")

# ===================
# LOAD ENV & GEMINI API
# ===================
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    st.error("❌ GOOGLE_API_KEY not found in .env file.")
    st.stop()
os.environ["GOOGLE_API_KEY"] = google_api_key

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    google_api_key=google_api_key
)

# ===================
# CONNECT TO DB
# ===================
db_files = list(Path(".").glob("*.db"))
if not db_files:
    st.error("⚠️ No SQLite (.db) file found in this folder.")
    st.stop()

db_path = db_files[0]
st.success(f"Connected to `{db_path.name}`")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Prepare SQL Agent
db_url = f"sqlite:///{db_path}"
db = SQLDatabase.from_uri(db_url)
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent = create_sql_agent(llm=llm, toolkit=toolkit, verbose=True)

# ===================
# SIDEBAR: TABLES & INFO
# ===================
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [t[0] for t in cursor.fetchall()]
st.sidebar.header("📂 Tables")
selected_table = st.sidebar.selectbox("Select a table", tables)

if selected_table:
    st.subheader(f"📑 Table: `{selected_table}`")
    cursor.execute(f"PRAGMA table_info({selected_table});")
    columns_info = cursor.fetchall()
    cols_df = pd.DataFrame(columns_info, columns=["cid", "Name", "Type", "NotNull", "Default", "PrimaryKey"])
    st.write("**Columns & Types:**")
    st.dataframe(cols_df.drop("cid", axis=1), use_container_width=True)

    df = pd.read_sql_query(f"SELECT * FROM {selected_table} LIMIT 10", conn)
    st.write("**Sample Rows:**")
    st.dataframe(df, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.info("Made with ❤️ using Streamlit & Gemini AI")

# ===================
# QUERY SECTION
# ===================
st.subheader("🔍 Ask a question about your database")
query = st.text_input("Enter your question (e.g., 'Show first 5 customers'):")

if st.button("Run Query"):
    if query.strip() == "":
        st.warning("Please enter a query.")
    else:
        with st.spinner("Running query with Gemini AI..."):
            try:
                result = agent.invoke({"input": query})
                st.success("✅ Result:")
                st.write(result["output"])
            except Exception as e:
                st.error(f"Error: {e}")
