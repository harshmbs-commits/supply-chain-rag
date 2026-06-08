import streamlit as st
import os
import pandas as pd
import sqlite3
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

st.title("Supply Chain Intelligence Assistant")
st.write("Ask any question about the supply chain shipment data.")

@st.cache_resource
def load_rag_system():
    df = pd.read_csv("SCMS_Delivery_History_Dataset.csv")
    df = df.fillna("Unknown")
    key_columns = ['Country', 'Shipment Mode', 'Vendor', 'Item Description', 
                   'Product Group', 'Sub Classification', 'Scheduled Delivery Date', 
                   'Delivered to Client Date', 'Weight (Kilograms)', 
                   'Freight Cost (USD)', 'Line Item Quantity', 'Unit Price', 
                   'Manufacturing Site']
    texts = df[key_columns].fillna('Unknown').apply(
        lambda row: " | ".join([f"{col}: {row[col]}" for col in key_columns]), axis=1
    ).tolist()
    documents = [Document(page_content=text) for text in texts]
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(chunks, embeddings, persist_directory="./chroma_db")
    return vectorstore

@st.cache_resource
def load_sql_database():
    df = pd.read_csv("SCMS_Delivery_History_Dataset.csv")
    df['Freight_Clean'] = pd.to_numeric(df['Freight Cost (USD)'], errors='coerce')
    df['Weight_Clean'] = pd.to_numeric(df['Weight (Kilograms)'], errors='coerce')
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    df.to_sql('shipments', conn, index=False)
    return conn

def get_llm():
    providers = [
        {"type": "groq", "model": "llama-3.1-8b-instant"},
        {"type": "groq", "model": "llama3-70b-8192"},
        {"type": "gemini", "model": "gemini-2.5-flash-lite"},
        {"type": "gemini", "model": "gemini-2.5-flash"},
    ]
    for provider in providers:
        try:
            if provider["type"] == "groq":
                llm = ChatGroq(
                    model=provider["model"],
                    groq_api_key=os.getenv("GROQ_API_KEY")
                )
            else:
                llm = ChatGoogleGenerativeAI(
                    model=provider["model"],
                    google_api_key=os.getenv("GOOGLE_API_KEY")
                )
            llm.invoke("hi")
            st.sidebar.success(f"Using: {provider['model']}")
            return llm
        except:
            continue
    return ChatGroq(
        model="llama-3.1-8b-instant",
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

def is_sql_question(question):
    sql_keywords = ['how many', 'average', 'total', 'highest', 'lowest', 
                    'most', 'least', 'count', 'per kg', 'cost', 'maximum', 
                    'minimum', 'sum', 'ranking', 'rank', 'expensive', 'cheapest']
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in sql_keywords)

def answer_with_sql(question, conn, llm):
    schema = """
    Table: shipments
    Columns:
    - Country (text)
    - Shipment Mode (text): Air, Truck, Ocean, Air Charter
    - Vendor (text)
    - Product Group (text): ARV, HRDT, ANTM, ACT, MRDT
    - Sub Classification (text): Adult, Pediatric
    - Line Item Quantity (numeric)
    - Line Item Value (numeric)
    - Unit Price (numeric)
    - Manufacturing Site (text)
    - Freight_Clean (numeric): freight cost in USD, NULL where not available
    - Weight_Clean (numeric): weight in kg, NULL where not available
    """
    prompt = f"""You are a SQL expert. Given this database schema:
{schema}

Generate a SQLite SQL query to answer: {question}

Rules:
- Use Freight_Clean for freight cost calculations
- Use Weight_Clean for weight calculations
- Filter NULL values when using Freight_Clean or Weight_Clean
- Do NOT include the word SQLite anywhere in the query
- Column names with spaces must be wrapped in double quotes
- Return ONLY the SQL query, nothing else

SQL Query:"""

    sql_response = llm.invoke(prompt)
    sql_query = sql_response.content.strip().replace('```sql', '').replace('```', '').strip()

    try:
        result = conn.execute(sql_query).fetchall()
        columns = [desc[0] for desc in conn.execute(sql_query).description]
        result_text = " | ".join(columns) + "\n"
        for row in result[:20]:
            result_text += " | ".join([str(x) for x in row]) + "\n"

        answer_prompt = f"""Based on these SQL results:
{result_text}

Answer this question in plain English: {question}
Rules:
- Always include specific numbers from results
- Round decimals to 2 places
- Format currency with $ sign
- Format large numbers with commas
- Never say a value is not provided"""

        final_answer = llm.invoke(answer_prompt)
        return final_answer.content, "sql"

    except Exception as e:
        return f"Could not process this numerical query: {str(e)}", "error"

def answer_with_rag(question, vectorstore, llm):
    docs = vectorstore.as_retriever(search_kwargs={"k": 20}).invoke(question)
    context = "\n".join([doc.page_content for doc in docs])
    prompt = f"Based on this supply chain data:\n{context}\n\nAnswer this question: {question}"
    response = llm.invoke(prompt)
    return response.content, "rag"

vectorstore = load_rag_system()
conn = load_sql_database()

st.markdown("### Recommended Questions")
st.write("Click any question below or type your own:")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**📊 Analytical Questions (SQL)**")
    sql_questions = [
        "What is the average freight cost per shipment?",
        "Which country received the highest number of shipments?",
        "What is the average freight cost per kg for air shipments?"
    ]
    for q in sql_questions:
        if st.button(q, key=f"sql_{q}"):
            st.session_state.selected_question = q

with col2:
    st.markdown("**🔍 Pattern Questions (AI)**")
    rag_questions = [
        "Which countries received pediatric ARV products and which vendors supplied them?",
        "What products were shipped by air freight?"
    ]
    for q in rag_questions:
        if st.button(q, key=f"rag_{q}"):
            st.session_state.selected_question = q

if "selected_question" not in st.session_state:
    st.session_state.selected_question = ""

question = st.text_input(
    "Your question:", 
    value=st.session_state.selected_question, 
    placeholder="e.g. Which vendor had the most shipments?"
)

if st.button("Ask"):
    if question:
        with st.spinner("Searching supply chain data..."):
            llm = get_llm()
            if is_sql_question(question):
                answer, source = answer_with_sql(question, conn, llm)
                st.info("📊 Answered using SQL — precise numerical analysis")
            else:
                answer, source = answer_with_rag(question, vectorstore, llm)
                st.info("🔍 Answered using AI — contextual pattern analysis")

            st.success("Answer:")
            st.write(answer)
    else:
        st.warning("Please enter a question first.")