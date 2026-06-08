# Supply Chain Intelligence Assistant

A RAG-based AI application that answers natural language questions about supply chain shipment data using Google Gemini and HuggingFace embeddings.

🔗 **Live Demo:** https://supply-chain-rag.streamlit.app
📁 **Dataset:** USAID Supply Chain Shipment Pricing Data (10,324 rows, 33 columns)

---

## What It Does

This tool allows supply chain professionals to query a large logistics dataset using plain English — no SQL, no Excel, no technical knowledge required.

**Example questions it answers:**
- "Which countries received pediatric ARV products and which vendors supplied them?"
- "What products were shipped by air freight?"
- "Which vendors supplied ARV products?"
- "Which countries received shipments and what products did they receive?"

---

## Architecture

User Question
⬇
HuggingFace Embeddings (all-MiniLM-L6-v2)
⬇
ChromaDB Vector Store (semantic search)
⬇
Retrieved Context + Question → Google Gemini 2.5 Flash
⬇
Natural Language Answer

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.11 |
| RAG Framework | LangChain |
| Embeddings | HuggingFace (all-MiniLM-L6-v2) |
| Vector Database | ChromaDB |
| LLM | Google Gemini 2.5 Flash Lite |
| Frontend | Streamlit |
| Deployment | Streamlit Community Cloud |
| Version Control | GitHub |

---

## Key Technical Decisions

**Why HuggingFace embeddings over Google embeddings?**
HuggingFace embeddings run locally — zero API cost, no version compatibility issues, and full control over the embedding process.

**Why ChromaDB over Pinecone?**
ChromaDB runs locally with zero configuration and no cloud dependency. The RAG concepts are identical to enterprise tools like Pinecone — the architecture transfers directly.

**Why Streamlit over Flask/React?**
Streamlit is the industry standard for AI prototyping — allows rapid iteration without frontend engineering overhead, and offers free public deployment.

---

## What I Learned

- RAG architecture and how retrieval quality directly impacts answer quality
- How data quality issues (bundled freight costs) affect AI system reliability
- API quota management on free tier models
- Vector database concepts — semantic search vs keyword search
- End-to-end AI application deployment

---

## Known Limitations & Next Steps

- Current version uses semantic retrieval — best for pattern and category questions
- Precise numerical calculations (averages, totals) would require adding a SQL agent layer
- Free tier Gemini model has daily request limits

**Version 2 improvements:**
- Add SQL agent for precise numerical analysis
- Expand dataset with cleaner freight cost data
- Add conversation memory for follow-up questions

---

## About

Built by **Harsh Gupta** — Enterprise SaaS Consultant with 10 years experience across logistics, supply chain, and B2B SaaS.

LinkedIn: linkedin.com/in/harsh-gupta-2401