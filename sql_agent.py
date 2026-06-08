import sqlite3
import pandas as pd
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def create_database():
    df = pd.read_csv("SCMS_Delivery_History_Dataset.csv")
    df['Freight_Clean'] = pd.to_numeric(df['Freight Cost (USD)'], errors='coerce')
    df['Weight_Clean'] = pd.to_numeric(df['Weight (Kilograms)'], errors='coerce')
    conn = sqlite3.connect(':memory:')
    df.to_sql('shipments', conn, index=False)
    return conn

def get_schema():
    return """
    Table: shipments
    Columns:
    - Country (text)
    - Shipment Mode (text): Air, Truck, Ocean, Air Charter
    - Vendor (text)
    - Item Description (text)
    - Product Group (text): ARV, HRDT, ANTM, ACT, MRDT
    - Sub Classification (text): Adult, Pediatric
    - Scheduled Delivery Date (text)
    - Delivered to Client Date (text)
    - Line Item Quantity (numeric)
    - Line Item Value (numeric)
    - Unit Price (numeric)
    - Manufacturing Site (text)
    - Freight_Clean (numeric): actual freight cost in USD, NULL where not available
    - Weight_Clean (numeric): actual weight in kg, NULL where not available
    """

def answer_with_sql(question, conn, llm):
    schema = get_schema()
    
    prompt = f"""You are a SQL expert. Given this database schema:
{schema}

Generate a SQLite SQL query to answer this question: {question}

Rules:
- Use Freight_Clean instead of 'Freight Cost (USD)' for freight cost calculations
- Use Weight_Clean instead of 'Weight (Kilograms)' for weight calculations
- Always filter NULL values when using Freight_Clean or Weight_Clean
- Use proper SQLite syntax
- Do NOT include the word 'SQLite' anywhere in the query
- Column names with spaces must be wrapped in double quotes e.g. "Country"
- Return ONLY the SQL query, nothing else, no explanation, no markdown

SQL Query:"""

    sql_response = llm.invoke(prompt)
    sql_query = sql_response.content.strip()
    sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
    
    try:
        result = conn.execute(sql_query).fetchall()
        columns = [desc[0] for desc in conn.execute(sql_query).description]
        
        result_text = f"Query: {sql_query}\n\nResults:\n"
        result_text += " | ".join(columns) + "\n"
        result_text += "-" * 50 + "\n"
        for row in result[:20]:
            result_text += " | ".join([str(x) for x in row]) + "\n"
        
        answer_prompt = f"""Based on these SQL query results:
{result_text}

Answer this question in plain English: {question}
Rules:
- Always include the specific numbers from the results
- Round decimals to 2 places
- Never say a value is 'not provided' — it is always in the results
- Format currency as USD with $ sign
- Format large numbers with commas"""
        
        final_answer = llm.invoke(answer_prompt)
        return final_answer.content
        
    except Exception as e:
        return f"Could not execute SQL query: {str(e)}"

if __name__ == "__main__":
    from langchain_groq import ChatGroq
    try:
        llm = ChatGroq(model="llama-3.1-8b-instant", groq_api_key=os.getenv("GROQ_API_KEY"))
        llm.invoke("hi")
        print("Using Groq llama-3.1-8b-instant")
    except:
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", google_api_key=os.getenv("GOOGLE_API_KEY"))
        print("Using Gemini 2.5 Flash Lite")
    
    conn = create_database()
    
    test_questions = [
        "What is the average freight cost per kg for air shipments?",
        "Which country has the highest freight cost per kg?",
        "Compare average freight cost per kg across all shipment modes?"
    ]
    
    for question in test_questions:
        print(f"\nQuestion: {question}")
        answer = answer_with_sql(question, conn, llm)
        print(f"Answer: {answer}")
    
    conn.close()