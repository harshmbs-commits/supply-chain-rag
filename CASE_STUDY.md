# Case Study: Supply Chain Intelligence Assistant

## Executive Summary

A RAG-based AI tool that enables supply chain analysts to query 10,000+ row logistics datasets using plain English — eliminating the dependency on SQL expertise and Excel pivot tables for routine analytical questions.

---

## User Persona

**Name:** Priya Sharma
**Role:** Supply Chain Analyst
**Organisation:** Mid-size NGO managing pharmaceutical procurement across Sub-Saharan Africa
**Experience:** 3-5 years in logistics and procurement operations
**Technical Skills:** Intermediate Excel, basic SQL, Tableau viewer (not builder)

**A typical day for Priya:**
- Receives 5-10 ad-hoc questions from program managers and country directors
- Spends 2-3 hours building Excel pivot tables to answer questions that should take minutes
- Writes SQL queries for complex questions — or waits for a data analyst to do it
- Struggles to spot patterns across 10,000+ shipment records manually
- Presents findings in PowerPoint — which becomes outdated the moment data changes

**Priya's frustration:**
> "I know the answer is in the data. I just can't get to it fast enough."

---

## Problem Statement

Supply chain analysts working with large logistics datasets face two compounding problems:

**Problem 1 — Pattern Recognition at Scale**
Manually identifying patterns across thousands of shipment records is time-consuming and error-prone. A dataset with 10,000+ rows across 33 variables cannot be meaningfully analysed through manual Excel filtering. Critical insights — like which vendors consistently delay pediatric ARV shipments, or which shipment modes drive cost overruns — remain hidden.

**Problem 2 — Accessibility Gap**
Non-technical stakeholders (program managers, country directors, procurement heads) cannot query data themselves. Every question routes through the analyst, creating a bottleneck. The analyst becomes a query-translation layer rather than a strategic advisor.

**The combined impact:**
- Analysts spend 40-60% of their time on data retrieval rather than analysis
- Decision-makers wait hours or days for answers that should take seconds
- Strategic insights are missed because routine queries consume all available bandwidth

---

## Existing Alternatives & Why They Fall Short

| Tool | How It's Used | Limitation |
|---|---|---|
| Excel + Pivot Tables | Filter and aggregate shipment data | Breaks down beyond 10,000 rows. Requires rebuilding for every new question. Non-technical users cannot operate independently. |
| SQL Queries | Extract specific data cuts | Requires technical knowledge. Every new question needs a new query. No natural language interface. |
| BI Dashboards (Tableau/Power BI) | Pre-built visualisations | Only answers pre-defined questions. Cannot handle ad-hoc queries. Requires data team to update. |
| Manual Report | Periodic summary documents | Always outdated. Cannot respond to real-time questions. |

**The gap none of these fill:**
A non-technical user asking a new, specific question about the data in plain English — and getting an accurate answer in seconds.

---

## The Solution

**Supply Chain Intelligence Assistant** — a RAG-based AI tool that:

1. Ingests the full logistics dataset (10,324 rows, 33 columns)
2. Converts it into searchable vector embeddings
3. Accepts natural language questions from any user
4. Retrieves the most relevant data chunks semantically
5. Uses Google Gemini to synthesise a coherent, accurate answer

**The core value proposition:**
Any stakeholder — technical or non-technical — can get answers to supply chain questions in seconds, without writing a single line of SQL or building a single pivot table.

---

## Use Cases

### Use Case 1 — Vendor Performance Analysis
**User:** Procurement Manager
**Question:** "Which vendors supplied pediatric ARV products and what shipment mode did they use?"
**Old way:** Build pivot table filtering by Sub Classification = Pediatric AND Product Group = ARV, then cross-reference vendor and shipment mode columns. 20-30 minutes.
**New way:** Type the question. Get answer in seconds.

### Use Case 2 — Route and Mode Analysis
**User:** Logistics Coordinator
**Question:** "What products were shipped by air freight and which countries received them?"
**Old way:** SQL query joining shipment mode, product, and country columns. Requires technical knowledge.
**New way:** Plain English question. Instant answer.

### Use Case 3 — Country-Level Procurement Insights
**User:** Country Director
**Question:** "Which countries received shipments and what products did they receive?"
**Old way:** Request from analyst → analyst builds report → 24-48 hour turnaround.
**New way:** Director queries directly. No analyst dependency.

---

## Success Metrics

### Primary Metrics

| Metric | Definition | Target |
|---|---|---|
| Answer Relevance Rate | % of questions that receive a relevant, on-topic answer | >80% |
| Fallback Rate | % of questions where system correctly identifies it cannot answer | <15% |
| Response Time | Time from question submission to answer display | <15 seconds |
| Hallucination Rate | % of answers containing factually incorrect information vs dataset | <10% |

### Secondary Metrics

| Metric | Definition | Target |
|---|---|---|
| User Satisfaction | Thumbs up rate on answers (once feedback implemented) | >75% |
| Retrieval Precision | % of retrieved chunks relevant to the question | >70% |
| Query Coverage | % of reasonable supply chain questions the system can answer | >60% |

### How Metrics Are Measured

**Answer Relevance & Hallucination Rate:**
A ground truth evaluation set of 20 questions with known correct answers is run through the system monthly. Answers are manually reviewed against the dataset.

**Response Time:**
Measured from button click to answer display. Logged automatically by Streamlit.

**Fallback Rate:**
Tracked by monitoring how often the system returns "insufficient data" responses vs substantive answers.

---

## Ground Truth Evaluation Questions

The following questions have verified correct answers from the dataset and are used to evaluate system performance:

| # | Question | Type |
|---|---|---|
| 1 | Which countries received shipments? | Simple — categorical |
| 2 | What products were shipped by air freight? | Simple — filtered |
| 3 | Which vendors supplied ARV products? | Medium — filtered |
| 4 | Which countries received pediatric ARV products? | Medium — multi-variable |
| 5 | What shipment modes are used in the dataset? | Simple — categorical |
| 6 | Which vendors supplied pediatric products? | Medium — filtered |
| 7 | Which manufacturing sites supplied ARV products? | Medium — filtered |
| 8 | What is the most common shipment mode? | Complex — analytical |
| 9 | Which countries received the highest quantity shipments? | Complex — analytical |
| 10 | Compare ARV vs HRDT shipment patterns across countries | Complex — multi-variable |

---

## Known Limitations

**Current Version (v1):**
- Freight cost analysis is limited — 14% of records list freight as "Included in Commodity Cost" rather than a separate value
- Precise numerical calculations (exact averages, totals) are approximate due to semantic retrieval
- Free tier API limits restrict to ~20 requests per day on Gemini 2.5 Flash Lite

**Planned Version 2 Improvements:**
- SQL agent layer for precise numerical queries (counts, averages, totals, rankings)
- User feedback mechanism (thumbs up/down) to track satisfaction
- Fallback mechanism for graceful handling of unanswerable questions
- Conversation memory for follow-up questions

---

## Technical Architecture

User Query (Natural Language)
↓
HuggingFace Embeddings (all-MiniLM-L6-v2)
↓
ChromaDB Vector Store — Semantic Search (k=20 chunks)
↓
Retrieved Context + Original Question
↓
Google Gemini 2.5 Flash Lite
↓
Natural Language Answer → Streamlit UI

**Why this architecture:**
- HuggingFace embeddings run locally — zero API cost, no version compatibility issues
- ChromaDB stores vectors persistently — no reprocessing on every query
- Gemini Flash Lite — fastest free tier model with 1,000 requests/day limit
- Streamlit — industry standard for AI prototyping, free public deployment

---

## Business Impact Potential

| Metric | Before | After |
|---|---|---|
| Time to answer ad-hoc question | 20-60 minutes | <15 seconds |
| Analyst dependency for stakeholder queries | High | Low |
| Questions answered per day | 5-10 | Unlimited |
| Technical skill required to query data | SQL/Excel proficiency | None |

---

*Built by Harsh Gupta — Enterprise SaaS Consultant*
*LinkedIn: linkedin.com/in/harsh-gupta-2401*
*Live Demo: https://supply-chain-rag.streamlit.app*