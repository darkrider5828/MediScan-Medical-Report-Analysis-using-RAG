# 🩺 MediScan – AI-Powered Medical Report Analyzer

[![Python](https://img.shields.io/badge/Python-3.10-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Made With LLM](https://img.shields.io/badge/GenAI-Gemini%201.5-informational)]()

**MediScan** is an AI-driven web application that extracts, analyzes, and interprets medical PDF reports using **Google Gemini 1.5**, **MiniLM embeddings**, and **FAISS vector search**. It enables users to chat with their medical reports, get intelligent summaries, visualizations, and insights—all in a simple browser interface.

---

## 🚀 Features

- 📄 Upload and parse medical PDF reports
- 🔐 Automatic patient anonymization
- 🧾 Extract tabular and textual data using `pdfplumber`
- 🧠 RAG-based Q&A using MiniLM + FAISS + Gemini 1.5
- 📊 Visualize results with charts and tables
- 💬 Chat interface to answer health-related queries contextually
- 💾 Download results as CSV or PDF

---

## 🧠 Demo Use Cases

> 🗨️ _"Summarize the report in bullet points."_  
> 🗨️ _"Is my hemoglobin level within the normal range?"_  
> 🗨️ _"Explain what the values mean in this report."_  
> 🗨️ _"What are the possible issues with low cholesterol?"_

---

## ⚙️ Tech Stack

| Layer         | Tools Used |
|---------------|------------|
| **Frontend**  | HTML, CSS, JavaScript |
| **Backend**   | Flask (Python) |
| **LLM & RAG** | Google Gemini 1.5 Flash, LangChain, MiniLM, FAISS |
| **PDF Parser**| PDFPlumber |
| **Visualization** | Matplotlib, Pandas |
| **Exporting** | ReportLab (PDF), CSV |
| **Security**  | Environment variables via `.env` |
| **Deployment**| Docker-ready (optional) |

---

## 📦 Getting Started

### 1️⃣ Clone the Repo

```bash
git clone https://github.com/darkrider5828/Medical-report-analysis.git
cd Medical-report-analysis
