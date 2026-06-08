import streamlit as st
import os
import pandas as pd
import sqlite3
import csv
from datetime import datetime
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

def save_feedback(question, answer, rating):
    file_exists = os.path.isfile("feedback_log.csv")
    with open("feedback_log.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "question", "answer", "rating"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            question,
            answer,
            rating
        ])

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

def is_out_of_scope(question):
    supply_chain_keywords = [
        'shipment', 'ship', 'freight', 'vendor', 'country', 'cost',
        'product', 'delivery', 'weight', 'air', 'truck', 'ocean',
        'arv', 'supply', 'chain', 'price', 'unit', 'quantity',
        'manufacture', 'site', 'mode', 'pediatric', 'adult',
        'average', 'total', 'highest', 'lowest', 'most', 'least',
        'expensive', 'cheapest', 'shipments', 'vendors', 'countries',
        'hrdt', 'antm', 'act', 'mrdt', 'scms', 'usaid', 'nigeria',
        'zambia', 'ethiopia', 'tanzania', 'uganda', 'south africa',
        'kenya', 'vietnam', 'haiti', 'zimbabwe', 'mozambique'
    ]
    question_lower = question.lower()
    return not any(keyword in question_lower for keyword in supply_chain_keywords)

def is_sql_question(question):
    sql_keywords = ['how many', 'average', 'total', 'highest', 'lowest',
                    'most', 'least', 'count', 'per kg', 'cost', 'maximum',
                    'minimum', 'sum', 'ranking', 'rank', 'expensive', 'cheapest']
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in sql_keywords)

def answer_with_sql(question, conn, llm):
    question_lower = question.lower()

    if "highest total freight" in question_lower or "most total freight" in question_lower:
        sql_query = """
            SELECT Country, ROUND(SUM(Freight_Clean), 2) as total_freight
            FROM shipments
            WHERE Freight_Clean IS NOT NULL
            GROUP BY Country
            ORDER BY total_freight DESC
            LIMIT 1
        """
    elif "most shipments" in question_lower and "vendor" in question_lower:
        sql_query = """
            SELECT Vendor, COUNT(*) as shipment_count
            FROM shipments
            GROUP BY Vendor
            ORDER BY shipment_count DESC
            LIMIT 1
        """
    elif ("most shipments" in question_lower and "country" in question_lower
          or "highest number of shipments" in question_lower):
        sql_query = """
            SELECT Country, COUNT(*) as shipment_count
            FROM shipments
            GROUP BY Country
            ORDER BY shipment_count DESC
            LIMIT 1
        """
    elif "average freight cost per kg" in question_lower and "air" in question_lower:
        sql_query = """
            SELECT ROUND(AVG(Freight_Clean / Weight_Clean), 2) as avg_cost_per_kg
            FROM shipments
            WHERE Freight_Clean IS NOT NULL
            AND Weight_Clean IS NOT NULL
            AND Weight_Clean > 0
            AND "Shipment Mode" = 'Air'
        """
    elif "average freight cost per kg" in question_lower and "ocean" in question_lower:
        sql_query = """
            SELECT ROUND(AVG(Freight_Clean / Weight_Clean), 2) as avg_cost_per_kg
            FROM shipments
            WHERE Freight_Clean IS NOT NULL
            AND Weight_Clean IS NOT NULL
            AND Weight_Clean > 0
            AND "Shipment Mode" = 'Ocean'
        """
    elif "average freight cost" in question_lower:
        sql_query = """
            SELECT ROUND(AVG(Freight_Clean), 2) as avg_freight_cost
            FROM shipments
            WHERE Freight_Clean IS NOT NULL
        """
    else:
        schema = (
            "Table: shipments\n"
            "Columns: Country (text), Shipment Mode (text), Vendor (text),\n"
            "Product Group (text), Sub Classification (text),\n"
            "Freight_Clean (numeric: freight cost USD), "
            "Weight_Clean (numeric: weight kg)"
        )
        prompt = (
            "You are a SQL expert. Generate a SQLite query to answer: "
            + question
            + "\n\nSchema:\n" + schema
            + "\n\nRules:\n"
            "- Use Freight_Clean for costs, Weight_Clean for weight\n"
            "- Filter NULLs: WHERE Freight_Clean IS NOT NULL\n"
            "- Wrap spaced column names in double quotes\n"
            "- Use GROUP BY + ORDER BY + LIMIT 10 for rankings\n"
            "- Never use nested aggregates\n"
            "- Return ONLY the SQL query\n\n"
            "SQL Query:"
        )
        sql_response = llm.invoke(prompt)
        sql_query = sql_response.content.strip().replace("```sql", "").replace("```", "").strip()

    try:
        result = conn.execute(sql_query).fetchall()
        columns = [desc[0] for desc in conn.execute(sql_query).description]
        result_text = " | ".join(columns) + "\n"
        for row in result[:20]:
            result_text += " | ".join([str(x) for x in row]) + "\n"

        answer_prompt = (
            "Based on these SQL results:\n"
            + result_text
            + "\nAnswer this question in plain English: "
            + question
            + "\nRules:\n"
            "- Include specific numbers\n"
            "- Round decimals to 2 places\n"
            "- Format currency with $ sign\n"
            "- Format large numbers with commas\n"
            "- Be direct, one or two sentences only"
        )

        final_answer = llm.invoke(answer_prompt)
        return final_answer.content, "sql"

    except Exception as e:
        return f"Could not process this numerical query: {str(e)}", "error"

def answer_with_rag(question, vectorstore, llm):
    docs = vectorstore.as_retriever(search_kwargs={"k": 20}).invoke(question)
    context = "\n".join([doc.page_content for doc in docs])
    prompt = (
        "Based on this supply chain data:\n"
        + context
        + "\n\nAnswer this question: "
        + question
    )
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

if "last_question" not in st.session_state:
    st.session_state.last_question = ""
if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""
if "feedback_given" not in st.session_state:
    st.session_state.feedback_given = False

question = st.text_input(
    "Your question:",
    value=st.session_state.selected_question,
    placeholder="e.g. Which vendor had the most shipments?"
)

if st.button("Ask"):
    if question:
        with st.spinner("Searching supply chain data..."):
            if is_out_of_scope(question):
                answer = (
                    "I can only answer questions about the USAID Supply Chain "
                    "Shipment dataset. Try asking about shipment costs, vendors, "
                    "countries, freight modes, or product types."
                )
                source = "fallback"
                st.warning("This question appears to be outside the scope of the dataset.")
            else:
                llm = get_llm()
                if is_sql_question(question):
                    answer, source = answer_with_sql(question, conn, llm)
                    st.info("📊 Answered using SQL — precise numerical analysis")
                else:
                    answer, source = answer_with_rag(question, vectorstore, llm)
                    st.info("🔍 Answered using AI — contextual pattern analysis")

            st.session_state.last_question = question
            st.session_state.last_answer = answer
            st.session_state.feedback_given = False
    else:
        st.warning("Please enter a question first.")

if st.session_state.last_answer:
    st.success("Answer:")
    st.write(st.session_state.last_answer)

if st.session_state.last_answer and not st.session_state.feedback_given:
    st.markdown("---")
    st.markdown("**Was this answer helpful?**")
    col_up, col_down, col_spacer = st.columns([1, 1, 8])

    with col_up:
        if st.button("👍", key="thumbs_up"):
            save_feedback(
                st.session_state.last_question,
                st.session_state.last_answer,
                "positive"
            )
            st.session_state.feedback_given = True
            st.rerun()

    with col_down:
        if st.button("👎", key="thumbs_down"):
            save_feedback(
                st.session_state.last_question,
                st.session_state.last_answer,
                "negative"
            )
            st.session_state.feedback_given = True
            st.rerun()

if st.session_state.feedback_given:
    st.markdown("---")
    st.success("✅ Thank you for your feedback!")