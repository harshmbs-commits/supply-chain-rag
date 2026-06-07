import os
import pandas as pd
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

df = pd.read_csv("SCMS_Delivery_History_Dataset.csv")
df = df.fillna("Unknown")
texts = df.apply(lambda row: " | ".join([f"{col}: {row[col]}" for col in df.columns]), axis=1).tolist()

documents = [Document(page_content=text) for text in texts]
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = text_splitter.split_documents(documents)

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma.from_documents(chunks, embeddings, persist_directory="./chroma_db")

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))

question = "Which country had the highest freight cost?"
docs = vectorstore.as_retriever().invoke(question)
context = "\n".join([doc.page_content for doc in docs])
prompt = f"Based on this supply chain data:\n{context}\n\nAnswer this question: {question}"
response = llm.invoke(prompt)

print("Question:", question)
print("Answer:", response.content)