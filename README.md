# 🏥 MediParse AI: Medical Report Parsing & Standardization

**Domain Knowledge Project | MSc Software Technology** **Author:** Rahul M  

---

## 📌 Project Overview
**MediParse AI** is an Intelligent Document Processing (IDP) application designed to extract, anonymize, and standardize unstructured medical laboratory reports. Utilizing multimodal Large Language Models (LLMs), the system converts varied formats of clinical lab reports—including messy handwriting, misaligned tables, and multi-page PDFs—into a structured, wide-format clinical database ready for analysis.

## ✨ Key Features
* **Multimodal AI Extraction:** Bypasses traditional OCR limitations to accurately read complex layouts, varied tables, and handwritten annotations (e.g., circled abnormal values).
* **Automated Standardization:** Maps disparate test names (e.g., "SGOT", "AST", "SERUM SGOT") to a single standardized medical terminology dictionary.
* **Strict Patient Anonymization:** Extracts relevant metadata (Age, Gender, Lab Name, Date) while strictly filtering out Personally Identifiable Information (PII) like patient names to maintain privacy.
* **PDF & Batch Processing:** Seamlessly handles multi-page PDFs and batches of images simultaneously, flattening the data into a single master Excel sheet.
* **Interactive Analytics:** Features a built-in Plotly dashboard for tracking batch abnormalities and an interactive data grid for manual pre-export review.

## 🛠️ Tech Stack
* **Frontend UI:** Streamlit
* **Data Manipulation:** Python, Pandas
* **AI Engine:** Google Gemini (Multimodal JSON structured outputs)
* **Document Parsing:** PyMuPDF (`fitz`), Pillow
* **Visualizations:** Plotly Express

---

## 🚀 Local Setup Instructions

### 1. Prerequisites
Ensure you have Python 3.8+ installed on your machine. Clone this repository to your local environment.

### 2. Install Dependencies
Navigate to the project directory in your terminal and install the required packages:
```bash
pip install -r requirements.txt
```

### 3. Configure API Keys
This application uses the Google Gemini API for multimodal extraction. 
1. Create a folder named `.streamlit` in the root directory.
2. Inside that folder, create a file named `secrets.toml`.
3. Add your Gemini API Key to the file like this:
```toml
GEMINI_API_KEY = "your_actual_api_key_here"
```

### 4. Run the Application
Start the Streamlit server by running:
```bash
streamlit run app.py
```
The application will automatically open in your default web browser at `http://localhost:8501`.

---
