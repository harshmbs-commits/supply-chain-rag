# Case Study: Supply Chain Intelligence Assistant

## Executive Summary

A hybrid RAG + SQL AI tool that enables supply chain analysts to query 10,000+ 
row logistics datasets using plain English — eliminating the dependency on SQL 
expertise and Excel pivot tables for routine analytical questions.

---

## User Persona

**Name:** Priya Sharma  
**Role:** Supply Chain Analyst  
**Organisation:** Mid-size NGO managing pharmaceutical procurement across 
Sub-Saharan Africa  
**Experience:** 3-5 years in logistics and procurement operations  
**Technical Skills:** Intermediate Excel, basic SQL, Tableau viewer (not builder)

**A typical day for Priya:**
- Receives 5-10 ad-hoc questions from program managers and country directors
- Spends 2-3 hours building Excel pivot tables to answer questions that should 
  take minutes
- Writes SQL queries for complex questions — or waits for a data analyst to do it
- Struggles to spot patterns across 10,000+ shipment records manually
- Presents findings in PowerPoint — which becomes outdated the moment data changes

**Priya's frustration:**
> "I know the answer is in the data. I just can't get to it fast enough."

---

## Problem Statement

Supply chain analysts working with large logistics datasets face two compounding 
problems:

**Problem 1 — Pattern Recognition at Scale**  
Manually identifying patterns across thousands of shipment records is 
time-consuming and error-prone. A dataset with 10,000+ rows across 33 variables 
cannot be meaningfully analysed through manual Excel filtering. Critical insights 
— like which vendors consistently delay pediatric ARV shipments, or which 
shipment modes drive cost overruns — remain hidden.

**Problem 2 — Accessibility Gap**  
Non-technical stakeholders (program managers, country directors, procurement 
heads) cannot query data themselves. Every question routes through the analyst, 
creating a bottleneck. The analyst becomes a query-translation layer rather than 
a strategic advisor.

**The combined impact:**
- Analysts spend 40-60% of their time on data retrieval rather than analysis
- Decision-makers wait hours or days for answers that should take seconds
- Strategic insights are missed because routine queries consume all available 
  bandwidth

---

## Existing Alternatives & Why They Fall Short

| Tool | How It's Used | Limitation |
|---|---|---|
| Excel + Pivot Tables | Filter and aggregate shipment data | Breaks down beyond 10,000 rows. Requires rebuilding for every new question. Non-technical users cannot operate independently. |
| SQL Queries | Extract specific data cuts | Requires technical knowledge. Every new question needs a new query. No natural language interface. |
| BI Dashboards (Tableau/Power BI) | Pre-built visualisations | Only answers pre-defined questions. Cannot handle ad-hoc queries. Requires data team to update. |
| Manual Report | Periodic summary documents | Always outdated. Cannot respond to real-time questions. |

**The gap none of these fill:**  
A non-technical user asking a new, specific question about the data in plain 
English — and getting an accurate answer in seconds.

---

## The Solution

**Supply Chain Intelligence Assistant** — a hybrid RAG + SQL AI tool that:

1. Ingests the full logistics dataset (10,324 rows, 33 columns)
2. Routes each question to the appropriate engine automatically
3. For numerical questions: generates and executes a SQL query against SQLite
4. For contextual questions: retrieves semantically relevant chunks from ChromaDB
5. Uses Groq (llama-3.1-8b-instant) to synthesise a coherent, accurate answer
6. Falls back gracefully when questions are outside the dataset scope

**The core value proposition:**  
Any stakeholder — technical or non-technical — can get answers to supply chain 
questions in seconds, without writing a single line of SQL or building a single 
pivot table.

---

## How the Routing Works

User Question
↓
Is it out of scope? → YES → Polite fallback message
↓ NO
Is it numerical? → YES → SQL Agent → SQLite → Precise answer
↓ NO
RAG Engine → ChromaDB → Contextual answer
    ↓
Groq LLM interprets and formats the answer
↓
User rates the answer 👍 / 👎

---

## Use Cases

### Use Case 1 — Vendor Performance Analysis
**User:** Procurement Manager  
**Question:** "Which vendors supplied pediatric ARV products and what shipment 
mode did they use?"  
**Old way:** Build pivot table filtering by Sub Classification = Pediatric AND 
Product Group = ARV, then cross-reference vendor and shipment mode columns. 
20-30 minutes.  
**New way:** Type the question. Get answer in seconds.

### Use Case 2 — Route and Mode Analysis
**User:** Logistics Coordinator  
**Question:** "What products were shipped by air freight and which countries 
received them?"  
**Old way:** SQL query joining shipment mode, product, and country columns. 
Requires technical knowledge.  
**New way:** Plain English question. Instant answer.

### Use Case 3 — Country-Level Procurement Insights
**User:** Country Director  
**Question:** "Which countries received shipments and what products did they 
receive?"  
**Old way:** Request from analyst → analyst builds report → 24-48 hour turnaround.  
**New way:** Director queries directly. No analyst dependency.

### Use Case 4 — Freight Cost Analysis (SQL)
**User:** Procurement Manager  
**Question:** "What is the average freight cost per shipment?"  
**SQL Result:** $10,178.44 average across 6,597 shipments with valid freight data  
**Old way:** Export to Excel, create pivot table, calculate averages manually. 
30+ minutes.  
**New way:** Plain English question answered instantly with precise figures.

### Use Case 5 — Country Cost Comparison (SQL)
**User:** Regional Director  
**Question:** "Which country had the highest total freight cost?"  
**SQL Result:** Nigeria — $8,290,645.67 total freight cost  
**Old way:** SQL query across multiple tables, requires technical knowledge.  
**New way:** Natural language query returns precise answer in seconds.

### Use Case 6 — Shipment Mode Cost Analysis (SQL)
**User:** Logistics Coordinator  
**Question:** "What is the average freight cost per kg for air shipments?"  
**SQL Result:** $5.07 per kg for air vs $0.53 per kg for ocean  
**Old way:** Manual calculation across 6,000+ rows in Excel.  
**New way:** Instant precise answer from SQL agent.

---

## Actual System Results

The following results were generated by running the SQL agent against the 
live dataset:

| Question | Answer |
|---|---|
| Average freight cost per shipment | $11,103.23 |
| Country with highest total freight cost | Nigeria — $14,268,550.39 |
| Most frequent vendor | SCMS from RDC — 5,404 shipments |
| Average freight cost per kg — Air | $33.52 |

*Note: Freight cost calculations exclude 14% of records where cost is listed 
as "Included in Commodity Cost" rather than a separate value.*

---

## Success Metrics

### Primary Metrics

| Metric | Definition | Target |
|---|---|---|
| Answer Relevance Rate | % of questions that receive a relevant, on-topic answer | >80% |
| Fallback Rate | % of out-of-scope questions correctly intercepted | >90% |
| Response Time | Time from question submission to answer display | <15 seconds |
| Hallucination Rate | % of answers containing factually incorrect information | <10% |

### Secondary Metrics

| Metric | Definition | Target |
|---|---|---|
| User Satisfaction | Thumbs up rate on answers | >75% |
| Retrieval Precision | % of retrieved chunks relevant to the question | >70% |
| Query Coverage | % of reasonable supply chain questions the system can answer | >60% |

---

## Ground Truth Evaluation Questions

### RAG Questions (Pattern & Context)

| # | Question | Type |
|---|---|---|
| 1 | Which countries received shipments and what products did they receive? | Simple — categorical |
| 2 | What products were shipped by air freight? | Simple — filtered |
| 3 | Which vendors supplied ARV products? | Medium — filtered |
| 4 | Which countries received pediatric ARV products and which vendors supplied them? | Medium — multi-variable |
| 5 | What shipment modes are used in the dataset? | Simple — categorical |
| 6 | Which vendors supplied pediatric products? | Medium — filtered |
| 7 | Which manufacturing sites supplied ARV products? | Medium — filtered |

### SQL Questions (Precise Numerical)

| # | Question | Type |
|---|---|---|
| 1 | How many shipments were sent to each country? | Count |
| 2 | How many shipments were sent by air versus truck? | Count — comparison |
| 3 | How many ARV shipments were there compared to HRDT? | Count — comparison |
| 4 | How many pediatric ARV shipments were sent by air freight? | Count — multi-variable |
| 5 | Which country received the highest number of shipments? | Ranking |
| 6 | Which vendor had the most shipments? | Ranking |
| 7 | Which shipment mode was used most frequently? | Ranking |
| 8 | What is the average freight cost per shipment? | Aggregation |
| 9 | Which shipment mode has the highest average freight cost? | Aggregation — comparison |
| 10 | What is the total freight cost of all shipments to Nigeria? | Aggregation — filtered |
| 11 | Which country had the highest total freight cost? | Aggregation — ranking |
| 12 | What is the average weight per shipment? | Aggregation |
| 13 | Which shipment mode carries the heaviest shipments on average? | Aggregation — comparison |
| 14 | What is the average freight cost per kg for air versus ocean shipments? | Complex — multi-variable |
| 15 | Which country had the highest average freight cost per shipment? | Complex — ranking |

---

## Known Limitations

- Freight cost analysis excludes 14% of records where cost is listed as 
  "Included in Commodity Cost" — these are filtered out before SQL calculations
- Free tier LLM APIs (Groq + Gemini) have daily request limits — a four-provider 
  fallback chain ensures maximum uptime
- Fallback keyword list covers common supply chain terms — highly unusual 
  phrasings may occasionally slip through

  User Query (Natural Language)
↓
Out-of-Scope Guardrail
↓
Keyword Router
↓           ↓
SQL Path     RAG Path
↓           ↓
SQLite      ChromaDB
↓       (k=20 chunks)
└────┬───┘
↓
Groq LLM (llama-3.1-8b-instant)
Fallback: Gemini 2.5 Flash
↓
Answer + Feedback (👍/👎)
↓
feedback_log.csv

**Why this architecture:**
- Hybrid routing handles both numerical and contextual questions accurately
- HuggingFace embeddings run locally — zero API cost
- ChromaDB stores vectors persistently — no reprocessing on every query
- Four-provider LLM fallback chain — maximum uptime on free tier
- Feedback logging enables future model evaluation and improvement

---

## Business Impact Potential

| Metric | Before | After |
|---|---|---|
| Time to answer ad-hoc question | 20-60 minutes | <15 seconds |
| Analyst dependency for stakeholder queries | High | Eliminated |
| Questions answered per day | 5-10 | Unlimited |
| Technical skill required to query data | SQL/Excel proficiency | None |
| Out-of-scope question handling | Crash or wrong answer | Graceful fallback |

---

*Built by Harsh Gupta — Enterprise SaaS Consultant*  
*LinkedIn: linkedin.com/in/harsh-gupta-2401*  
*Live Demo: https://supply-chain-rag.streamlit.app*