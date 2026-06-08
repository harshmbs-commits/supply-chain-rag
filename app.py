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

st.set_page_config(
    page_title="Supply Chain Intelligence Assistant",
    page_icon="🚢",
    layout="centered"
)

st.markdown("""
<style>
.sc-header {
    background: #0F6E56;
    padding: 28px 32px 20px;
    border-radius: 12px 12px 0 0;
}
.sc-header-title { font-size: 24px; font-weight: 600; color: #E1F5EE; margin: 0 0 6px; }
.sc-header-sub { font-size: 14px; color: #9FE1CB; margin: 0 0 14px; }
.sc-builder { font-size: 12px; color: #9FE1CB; }
.sc-builder a { color: #E1F5EE; text-decoration: underline; }
.sc-stats {
    background: #085041;
    padding: 14px 32px;
    display: flex;
    gap: 0;
}
.sc-stat { flex: 1; text-align: center; border-right: 0.5px solid #1D9E75; padding: 4px 0; }
.sc-stat:last-child { border-right: none; }
.sc-stat-num { font-size: 20px; font-weight: 600; color: #E1F5EE; display: block; }
.sc-stat-label { font-size: 11px; color: #9FE1CB; }
.sc-body {
    border: 0.5px solid #1D9E75;
    border-top: none;
    border-radius: 0 0 12px 12px;
    padding: 24px 32px;
    margin-bottom: 24px;
}
.sc-section-title {
    font-size: 11px; font-weight: 600; color: #1D9E75;
    text-transform: uppercase; letter-spacing: 0.08em; margin: 0 0 12px;
}
.sc-dataset-card {
    background: #f0faf7; border: 0.5px solid #9FE1CB;
    border-radius: 8px; padding: 14px 16px; margin-bottom: 24px;
    font-size: 13px; color: #2d2d2d; line-height: 1.6;
}
.sc-dataset-name { font-weight: 600; color: #085041; margin-bottom: 4px; font-size: 14px; }
.sc-who-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 24px; }
.sc-who-card { background: #f0faf7; border: 0.5px solid #9FE1CB; border-radius: 8px; padding: 12px 14px; }
.sc-who-role { font-size: 13px; font-weight: 600; color: #085041; margin: 0 0 5px; }
.sc-who-use { font-size: 12px; color: #444; margin: 0; line-height: 1.5; }
.sc-insights-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 24px; }
.sc-insight {
    background: #f0faf7; border: 0.5px solid #9FE1CB;
    border-left: 3px solid #1D9E75; border-radius: 8px; padding: 12px 14px;
}
.sc-insight-q { font-size: 11px; color: #666; margin: 0 0 5px; }
.sc-insight-a { font-size: 13px; font-weight: 600; color: #085041; margin: 0; }
.sc-how { display: flex; align-items: center; margin-bottom: 24px; }
.sc-step {
    flex: 1; text-align: center; background: #f0faf7;
    border: 0.5px solid #9FE1CB; border-radius: 8px; padding: 12px 10px;
}
.sc-step-num {
    display: inline-block; width: 22px; height: 22px; background: #1D9E75;
    color: #fff; border-radius: 50%; font-size: 12px; font-weight: 600;
    line-height: 22px; margin-bottom: 6px;
}
.sc-step-title { font-size: 12px; font-weight: 600; color: #085041; margin: 0 0 3px; }
.sc-step-desc { font-size: 11px; color: #555; margin: 0; line-height: 1.4; }
.sc-arrow { font-size: 18px; color: #1D9E75; padding: 0 8px; flex-shrink: 0; }
.sc-divider { border: none; border-top: 0.5px solid #d0ece6; margin: 0 0 12px; }
.sc-disclaimer { font-size: 11px; color: #888; text-align: center; }
.sc-q-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px; }
.sc-q-label {
    font-size: 11px; font-weight: 600; color: #1D9E75;
    text-transform: uppercase; letter-spacing: 0.08em; margin: 0 0 8px;
}
.sc-q-card {
    background: #f0faf7; border: 0.5px solid #9FE1CB;
    border-radius: 8px; padding: 10px 14px; font-size: 13px;
    color: #085041; line-height: 1.4; margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="sc-header">
    <div class="sc-header-title">🚢 Supply Chain Intelligence Assistant</div>
    <div class="sc-header-sub">Ask any question about USAID pharmaceutical supply chain shipment data in plain English</div>
    <div class="sc-builder">
        Built by &nbsp;<a href="https://linkedin.com/in/harsh-gupta-2401" target="_blank">Harsh Gupta</a>
        &nbsp;·&nbsp;
        <a href="https://github.com/harshmbs-commits/supply-chain-rag" target="_blank">GitHub</a>
    </div>
</div>
<div class="sc-stats">
    <div class="sc-stat"><span class="sc-stat-num">10,324</span><span class="sc-stat-label">Shipment records</span></div>
    <div class="sc-stat"><span class="sc-stat-num">33</span><span class="sc-stat-label">Data columns</span></div>
    <div class="sc-stat"><span class="sc-stat-num">40+</span><span class="sc-stat-label">Countries</span></div>
    <div class="sc-stat"><span class="sc-stat-num">5</span><span class="sc-stat-label">Product groups</span></div>
</div>
<div class="sc-body">
    <div class="sc-section-title">Data source</div>
    <div class="sc-dataset-card">
        <div class="sc-dataset-name">📂 USAID Supply Chain Shipment Pricing Dataset</div>
        Pharmaceutical supply chain shipments managed under USAID-funded programs across
        Sub-Saharan Africa and Southeast Asia. Covers ARV, HRDT, and ANTM product groups
        with freight costs, weights, vendors, manufacturing sites, and delivery details.
    </div>
    <div class="sc-section-title">Who can use this</div>
    <div class="sc-who-grid">
        <div class="sc-who-card">
            <div class="sc-who-role">📊 Procurement managers</div>
            <div class="sc-who-use">Analyse freight costs, vendor performance, and shipment modes — no SQL needed</div>
        </div>
        <div class="sc-who-card">
            <div class="sc-who-role">🌍 Country directors</div>
            <div class="sc-who-use">Instantly query which products and vendors serve specific countries</div>
        </div>
        <div class="sc-who-card">
            <div class="sc-who-role">🚛 Logistics coordinators</div>
            <div class="sc-who-use">Compare air vs ocean freight and identify heavyweight shipment patterns</div>
        </div>
    </div>
    <div class="sc-section-title">Sample insights from this data</div>
    <div class="sc-insights-grid">
        <div class="sc-insight">
            <div class="sc-insight-q">Highest freight cost country</div>
            <div class="sc-insight-a">Nigeria — $14.2M total</div>
        </div>
        <div class="sc-insight">
            <div class="sc-insight-q">Most active vendor</div>
            <div class="sc-insight-a">SCMS from RDC — 5,404 shipments</div>
        </div>
        <div class="sc-insight">
            <div class="sc-insight-q">Air vs ocean cost per kg</div>
            <div class="sc-insight-a">$33.52 air vs $0.53 ocean</div>
        </div>
    </div>
    <div class="sc-section-title">How it works</div>
    <div class="sc-how">
        <div class="sc-step">
            <div class="sc-step-num">1</div>
            <div class="sc-step-title">Ask in plain English</div>
            <div class="sc-step-desc">Type any supply chain question — no SQL or Excel required</div>
        </div>
        <div class="sc-arrow">→</div>
        <div class="sc-step">
            <div class="sc-step-num">2</div>
            <div class="sc-step-title">AI routes the query</div>
            <div class="sc-step-desc">Numerical questions go to SQL. Pattern questions go to the RAG engine</div>
        </div>
        <div class="sc-arrow">→</div>
        <div class="sc-step">
            <div class="sc-step-num">3</div>
            <div class="sc-step-title">Get an instant answer</div>
            <div class="sc-step-desc">Groq LLM interprets the results and responds in plain English</div>
        </div>
    </div>
    <hr class="sc-divider">
    <div class="sc-disclaimer">
        ⚠️ Answers are AI-generated based on the dataset. Verify critical figures before use in decisions.
    </div>
</div>
""", unsafe_allow_html=True)


def save_feedback(question, answer, rating):
    file_exists = os.path.isfile("feedback_log.csv")
    with open("feedback_log.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "question", "answer", "rating"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), question, answer, rating])

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
                llm = ChatGroq(model=provider["model"], groq_api_key=os.getenv("GROQ_API_KEY"))
            else:
                llm = ChatGoogleGenerativeAI(model=provider["model"], google_api_key=os.getenv("GOOGLE_API_KEY"))
            llm.invoke("hi")
            return llm
        except:
            continue
    return ChatGroq(model="llama-3.1-8b-instant", groq_api_key=os.getenv("GROQ_API_KEY"))

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
    return not any(k in question.lower() for k in supply_chain_keywords)

def is_sql_question(question):
    sql_keywords = ['how many', 'average', 'total', 'highest', 'lowest',
                    'most', 'least', 'count', 'per kg', 'cost', 'maximum',
                    'minimum', 'sum', 'ranking', 'rank', 'expensive', 'cheapest']
    return any(k in question.lower() for k in sql_keywords)

def answer_with_sql(question, conn, llm):
    q = question.lower()
    if "highest total freight" in q or "most total freight" in q:
        sql_query = """SELECT Country, ROUND(SUM(Freight_Clean), 2) as total_freight
            FROM shipments WHERE Freight_Clean IS NOT NULL
            GROUP BY Country ORDER BY total_freight DESC LIMIT 1"""
    elif "most shipments" in q and "vendor" in q:
        sql_query = """SELECT Vendor, COUNT(*) as shipment_count
            FROM shipments GROUP BY Vendor ORDER BY shipment_count DESC LIMIT 1"""
    elif ("most shipments" in q and "country" in q) or "highest number of shipments" in q:
        sql_query = """SELECT Country, COUNT(*) as shipment_count
            FROM shipments GROUP BY Country ORDER BY shipment_count DESC LIMIT 1"""
    elif "average freight cost per kg" in q and "air" in q:
        sql_query = """SELECT ROUND(AVG(Freight_Clean / Weight_Clean), 2) as avg_cost_per_kg
            FROM shipments WHERE Freight_Clean IS NOT NULL AND Weight_Clean IS NOT NULL
            AND Weight_Clean > 0 AND "Shipment Mode" = 'Air'"""
    elif "average freight cost per kg" in q and "ocean" in q:
        sql_query = """SELECT ROUND(AVG(Freight_Clean / Weight_Clean), 2) as avg_cost_per_kg
            FROM shipments WHERE Freight_Clean IS NOT NULL AND Weight_Clean IS NOT NULL
            AND Weight_Clean > 0 AND "Shipment Mode" = 'Ocean'"""
    elif "average freight cost" in q:
        sql_query = """SELECT ROUND(AVG(Freight_Clean), 2) as avg_freight_cost
            FROM shipments WHERE Freight_Clean IS NOT NULL"""
    else:
        schema = ("Table: shipments\nColumns: Country, Shipment Mode, Vendor, "
                  "Product Group, Sub Classification, Freight_Clean (cost USD), Weight_Clean (kg)")
        prompt = ("SQL expert. SQLite query to answer: " + question + "\nSchema:\n" + schema +
                  "\nRules: use Freight_Clean/Weight_Clean, filter NULLs, "
                  "quote spaced columns, GROUP BY+ORDER BY+LIMIT 10 for rankings, "
                  "no nested aggregates. Return ONLY SQL.\nSQL Query:")
        sql_response = llm.invoke(prompt)
        sql_query = sql_response.content.strip().replace("```sql", "").replace("```", "").strip()

    try:
        result = conn.execute(sql_query).fetchall()
        columns = [desc[0] for desc in conn.execute(sql_query).description]
        result_text = " | ".join(columns) + "\n"
        for row in result[:20]:
            result_text += " | ".join([str(x) for x in row]) + "\n"
        answer_prompt = ("SQL results:\n" + result_text +
                         "\nAnswer in plain English: " + question +
                         "\nRules: specific numbers, 2 decimal places, $ for currency, "
                         "commas for large numbers, 1-2 sentences only.")
        return llm.invoke(answer_prompt).content, "sql"
    except Exception as e:
        return f"Could not process this numerical query: {str(e)}", "error"

def answer_with_rag(question, vectorstore, llm):
    docs = vectorstore.as_retriever(search_kwargs={"k": 20}).invoke(question)
    context = "\n".join([doc.page_content for doc in docs])
    response = llm.invoke("Based on this supply chain data:\n" + context + "\n\nAnswer: " + question)
    return response.content, "rag"

vectorstore = load_rag_system()
conn = load_sql_database()

st.markdown("### Ask a question")
st.markdown("<p style='font-size:13px; color:#666; margin-bottom:14px;'>Click any question below or type your own:</p>", unsafe_allow_html=True)

for key, default in [("selected_question", ""), ("last_question", ""),
                      ("last_answer", ""), ("feedback_given", False)]:
    if key not in st.session_state:
        st.session_state[key] = default

st.markdown("""
<div class="sc-q-grid">
    <div>
        <div class="sc-q-label">📊 Analytical (SQL)</div>
    </div>
    <div>
        <div class="sc-q-label">🔍 Pattern (AI)</div>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    for q in ["What is the average freight cost per shipment?",
               "Which country received the highest number of shipments?",
               "What is the average freight cost per kg for air shipments?"]:
        if st.button(q, key=f"q_{q}", use_container_width=True):
            st.session_state.selected_question = q

with col2:
    for q in ["Which countries received pediatric ARV products and which vendors supplied them?",
               "What products were shipped by air freight?"]:
        if st.button(q, key=f"q_{q}", use_container_width=True):
            st.session_state.selected_question = q

question = st.text_input(
    "Your question:",
    value=st.session_state.selected_question,
    placeholder="e.g. Which vendor had the most shipments?"
)

if st.button("Ask"):
    if question:
        with st.spinner("Searching supply chain data..."):
            if is_out_of_scope(question):
                answer = ("I can only answer questions about the USAID Supply Chain "
                          "Shipment dataset. Try asking about shipment costs, vendors, "
                          "countries, freight modes, or product types.")
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
            save_feedback(st.session_state.last_question, st.session_state.last_answer, "positive")
            st.session_state.feedback_given = True
            st.rerun()
    with col_down:
        if st.button("👎", key="thumbs_down"):
            save_feedback(st.session_state.last_question, st.session_state.last_answer, "negative")
            st.session_state.feedback_given = True
            st.rerun()

if st.session_state.feedback_given:
    st.markdown("---")
    st.success("✅ Thank you for your feedback!")