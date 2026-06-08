# Supply Chain Intelligence Assistant

A hybrid RAG + SQL AI application that answers natural language questions 
about supply chain shipment data. Built with LangChain, ChromaDB, Groq, 
and Streamlit.

🔗 **Live Demo:** https://supply-chain-rag.streamlit.app  
📁 **Dataset:** USAID Supply Chain Shipment Pricing Data (10,324 rows, 33 columns)

---

## What It Does

This tool allows supply chain professionals to query a large logistics dataset 
using plain English — no SQL, no Excel, no technical knowledge required.

The app automatically detects the type of question and routes it to the 
appropriate engine:

| Question Type | Engine | Example |
|---|---|---|
| Numerical / Analytical | SQL Agent → SQLite | "What is the average freight cost per shipment?" |
| Pattern / Contextual | RAG → ChromaDB | "Which vendors supplied pediatric ARV products?" |
| Out of scope | Fallback guardrail | "What is the GDP of Nigeria?" |

---

## Architecture
User Question
↓
Keyword Router
↓                        ↓
SQL Questions           Contextual Questions
↓                        ↓
SQLite Query            HuggingFace Embeddings
↓                  (all-MiniLM-L6-v2)
SQL Results                   ↓
↓                  ChromaDB Vector Store
↓                  (semantic search, k=20)
↓                        ↓
└──────────┬─────────────┘
↓
Groq LLM (llama-3.1-8b-instant)
Fallback: Gemini 2.5 Flash
↓
Natural Language Answer
↓
User Feedback (👍 / 👎)

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.14 |
| RAG Framework | LangChain |
| Embeddings | HuggingFace (all-MiniLM-L6-v2) — local, zero cost |
| Vector Database | ChromaDB (local) |
| SQL Database | SQLite (in-memory) |
| SQL Agent | LangChain + custom prompt engineering |
| Primary LLM | Groq — llama-3.1-8b-instant |
| Fallback LLM | Google Gemini 2.5 Flash |
| Frontend | Streamlit |
| Deployment | Streamlit Community Cloud |
| Version Control | GitHub |

---

## Key Technical Decisions

**Why a hybrid RAG + SQL architecture?**  
Pure RAG struggles with precise numerical questions — it retrieves text chunks 
but cannot aggregate numbers reliably. A SQL agent runs exact database queries 
for calculations (averages, totals, rankings) while RAG handles pattern and 
context questions. This mirrors how production AI systems at companies like 
Salesforce and ServiceNow handle mixed query types.

**Why HuggingFace embeddings over Google embeddings?**  
HuggingFace embeddings run locally — zero API cost, no version compatibility 
issues, and full control over the embedding process.

**Why ChromaDB over Pinecone?**  
ChromaDB runs locally with zero configuration and no cloud dependency. The RAG 
concepts are identical to enterprise tools like Pinecone — the architecture 
transfers directly.

**Why Groq over Gemini as primary LLM?**  
Groq offers significantly faster inference speeds at free tier. A four-provider 
fallback chain (Groq fast → Groq large → Gemini lite → Gemini full) ensures 
maximum uptime within free tier constraints.

**Why a fallback guardrail?**  
Without guardrails, out-of-scope questions either crash the app or return 
hallucinated answers. The guardrail detects irrelevant questions and returns 
an honest, informative message — a standard practice in production AI systems.

---

## Features

- ✅ Hybrid query routing (SQL for numbers, RAG for context)
- ✅ Multi-provider LLM fallback chain (4 providers)
- ✅ Out-of-scope question detection with graceful fallback message
- ✅ User feedback mechanism (👍 / 👎) with CSV logging
- ✅ Recommended questions panel for guided exploration
- ✅ Live deployment on Streamlit Community Cloud

---

## Dataset

**Source:** USAID Supply Chain Shipment Pricing Dataset (via Kaggle)  
**Size:** 10,324 shipment records, 33 columns  
**Key fields:** Country, Shipment Mode, Vendor, Product Group, 
Sub Classification, Freight Cost (USD), Weight (Kilograms), 
Unit Price, Manufacturing Site

---

## What I Learned

- Hybrid AI architecture design — when to use RAG vs SQL vs rules
- Prompt engineering for SQL generation and natural language interpretation
- LLM fallback chain design for reliability on free tier APIs
- Vector database concepts — semantic search vs keyword search
- Production AI guardrails — handling edge cases gracefully
- End-to-end deployment: local development → GitHub → cloud hosting

---

## About

Built by **Harsh Gupta** — Enterprise SaaS Consultant with 10 years experience 
across logistics, supply chain, and B2B SaaS.  

LinkedIn: linkedin.com/in/harsh-gupta-2401