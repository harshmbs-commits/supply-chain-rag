import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
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
    key_columns = ['Country', 'Shipment Mode', 'Vendor', 'Item Description', 'Product Group', 'Sub Classification', 'Scheduled Delivery Date', 'Delivered to Client Date', 'Weight (Kilograms)', 'Freight Cost (USD)', 'Line Item Quantity', 'Unit Price', 'Manufacturing Site']
    texts = df[key_columns].fillna('Unknown').apply(lambda row: " | ".join([f"{col}: {row[col]}" for col in key_columns]), axis=1).tolist()
    documents = [Document(page_content=text) for text in texts]
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(chunks, embeddings, persist_directory="./chroma_db")
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", google_api_key=os.getenv("GOOGLE_API_KEY"))
    return vectorstore, llm

vectorstore, llm = load_rag_system()

st.markdown("### Recommended Questions")
st.write("Click any question below or type your own:")

recommended_questions = [
    "Which countries received shipments and what products did they receive?",
    "What products were shipped by air freight?",
    "Which countries received pediatric ARV products and which vendors supplied them?",
    "Which vendors supplied ARV products and what shipment mode did they use?",
    "Compare shipment patterns for ARV versus HRDT product groups across different countries?"
]

if "selected_question" not in st.session_state:
    st.session_state.selected_question = ""

for q in recommended_questions:
    if st.button(q):
        st.session_state.selected_question = q

question = st.text_input("Your question:", value=st.session_state.selected_question, placeholder="e.g. Which vendor had the most shipments?")

if st.button("Ask"):
    if question:
        with st.spinner("Searching supply chain data..."):
            docs = vectorstore.as_retriever(search_kwargs={"k": 20}).invoke(question)
            context = "\n".join([doc.page_content for doc in docs])
            prompt = f"Based on this supply chain data:\n{context}\n\nAnswer this question: {question}"
            response = llm.invoke(prompt)
            st.success("Answer:")
            st.write(response.content)
    else:
        st.warning("Please enter a question first.")