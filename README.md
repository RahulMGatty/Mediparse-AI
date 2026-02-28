# 🏥 MediParse AI: Medical Report Parsing & Standardization

**Domain Knowledge Project | MSc Software Technology** **Author:** [Your Name]  

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

## 💻 Full Application Code (`app.py`)
Below is the complete source code for the MediParse AI application.

```python
import streamlit as st
import pandas as pd
import json
import time
import io
import fitz  # PyMuPDF for handling PDFs
from PIL import Image
from google import genai
from google.genai import types
import plotly.express as px

# --- CONFIGURATION & STYLING ---
st.set_page_config(page_title="MediParse AI", page_icon="🏥", layout="wide")

st.markdown("""
    <style>
    .main .block-container { padding-top: 2rem; max-width: 95%; }
    [data-testid="stMetricValue"] { font-size: 2.5rem; color: #0068c9; }
    .custom-header {
        background: linear-gradient(90deg, #0068c9 0%, #00b4d8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.5rem;
        padding-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

STANDARD_TERMS = {
    "SGOT/AST": "AST", "SERUM SGOT(AST)": "AST",
    "SGPT/ALT": "ALT", "SERUM SGPT(ALT)": "ALT",
    "TOTAL BILIRUBIN": "Bilirubin (Total)", "SERUM ALBUMIN": "Albumin",
    "ALKALINE PHOSPHATASE": "ALP", "ALKALINE PHOSPHATSE": "ALP",
    "Procalcitonin": "Procalcitonin (PCT)", "Platelet count": "Platelets",
    "Mean Cell Volume (MCV)": "MCV", "Neutrophils.": "Neutrophils",
    "Lymphocytes": "Lymphocytes", "Pus Cells (W.B.C)": "Urine WBC",
    "Red Blood Cells (R.B.C)": "Urine RBC"
}

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("🔑 API Key not found! Please check your .streamlit/secrets.toml file.")
    st.stop()

# --- CORE FUNCTIONS ---
def extract_data_from_image(image, api_key):
    client = genai.Client(api_key=api_key)
    prompt = """
    You are an expert medical data extractor. Analyze this medical lab report image.
    Task 1: Extract Anonymized Metadata (lab_name, date, age, gender). STRICTLY NO PATIENT NAMES.
    Task 2: Extract Test Results (parameter, result, unit, flag: High/Low/Normal).
    Return STRICTLY as a JSON object: {"metadata": {...}, "tests": [...]}
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=[image, prompt],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
    except Exception as e:
        return None

def highlight_abnormal(val):
    if isinstance(val, str):
        if "(High)" in val:
            return 'background-color: #ffebee; color: #c62828;'
        elif "(Low)" in val:
            return 'background-color: #fff8e1; color: #f57f17;'
    return ''

def process_file_to_images(file):
    """Converts uploaded file (Image or PDF) into a list of PIL Images."""
    images = []
    if file.name.lower().endswith('.pdf'):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            img_data = pix.tobytes("png")
            images.append(Image.open(io.BytesIO(img_data)))
    else:
        images.append(Image.open(file))
    return images

# --- SIDEBAR UI ---
with st.sidebar:
    st.markdown("## 🏥 MediParse AI")
    st.caption("Intelligent Medical Data Extraction")
    st.divider()
    
    st.markdown("### 1. Upload Documents")
    uploaded_files = st.file_uploader("Select Lab Reports", type=["jpg", "jpeg", "png", "pdf"], accept_multiple_files=True, label_visibility="collapsed")
    
    st.divider()
    st.info("💡 **Workflow:**\n1. Upload batches of images or PDFs.\n2. Review automated charts.\n3. Edit data directly in the grid.\n4. Export to Excel.")

# --- MAIN CANVAS UI ---
st.markdown('<div class="custom-header">Medical Report Processing Hub</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📤 Upload & Process", "📈 Analytics Dashboard", "✏️ Data Grid & Export"])

with tab1:
    if not uploaded_files:
        st.info("👈 **Awaiting Documents:** Please upload medical report images or PDFs in the sidebar to begin processing.")
    else:
        st.markdown(f"**{len(uploaded_files)} Document(s) Ready for Processing**")
        
        if st.button("🚀 Process Batch", type="primary"):
            st.session_state['processing_done'] = False
            all_patients_data = []
            
            my_bar = st.progress(0, text="Parsing medical records. Please wait...")
            
            for index, file in enumerate(uploaded_files):
                my_bar.progress((index) / len(uploaded_files), text=f"Analyzing {file.name}...")
                
                report_images = process_file_to_images(file)
                
                combined_patient_row = {
                    "Source File": file.name,
                    "Lab Name": "Unknown",
                    "Report Date": "Unknown",
                    "Age": "Unknown",
                    "Gender": "Unknown"
                }
                
                for img in report_images:
                    raw_json = extract_data_from_image(img, API_KEY)
                    
                    if raw_json:
                        metadata = raw_json.get("metadata", {})
                        if metadata.get("lab_name") and combined_patient_row["Lab Name"] == "Unknown":
                            combined_patient_row["Lab Name"] = metadata.get("lab_name")
                        if metadata.get("date") and combined_patient_row["Report Date"] == "Unknown":
                            combined_patient_row["Report Date"] = metadata.get("date")
                        if metadata.get("age") and combined_patient_row["Age"] == "Unknown":
                            combined_patient_row["Age"] = metadata.get("age")
                        if metadata.get("gender") and combined_patient_row["Gender"] == "Unknown":
                            combined_patient_row["Gender"] = metadata.get("gender")
                        
                        for item in raw_json.get("tests", []):
                            raw_name = item.get("parameter", "").strip()
                            std_name = STANDARD_TERMS.get(raw_name, raw_name)
                            cell_value = f"{item.get('result', '')} {item.get('unit', '')}".strip()
                            if item.get("flag") in ["High", "Low"]:
                                cell_value += f" ({item['flag']})"
                            
                            combined_patient_row[std_name] = cell_value
                            
                all_patients_data.append(combined_patient_row)
                
                if index < len(uploaded_files) - 1:
                    time.sleep(3) 
                    
            my_bar.progress(1.0, text="✅ Batch processing complete!")
            
            st.session_state['master_data'] = all_patients_data
            st.session_state['processing_done'] = True
            st.toast("Extraction Complete! Check the Analytics Dashboard.", icon="✅")

with tab2:
    if 'processing_done' in st.session_state and st.session_state['processing_done']:
        df = pd.DataFrame(st.session_state['master_data'])
        metadata_cols = ["Source File", "Lab Name", "Report Date", "Age", "Gender"]
        test_cols = sorted([col for col in df.columns if col not in metadata_cols])
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Patient Records", len(df))
        m2.metric("Unique Tests Tracked", len(test_cols))
        abnormal_count = df[test_cols].astype(str).apply(lambda x: x.str.contains(r'\(High\)|\(Low\)')).sum().sum()
        m3.metric("Abnormal Flags Detected", abnormal_count)
        
        st.divider()
        st.subheader("Test Frequency Across Batch")
        test_counts = df[test_cols].notna().sum().reset_index()
        test_counts.columns = ['Test Name', 'Number of Patients']
        test_counts = test_counts[test_counts['Number of Patients'] > 0].sort_values(by='Number of Patients', ascending=False)
        
        fig = px.bar(test_counts, x='Test Name', y='Number of Patients', color='Number of Patients', color_continuous_scale='Blues', text='Number of Patients')
        fig.update_layout(xaxis_tickangle=-45, margin=dict(t=20, b=20, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📊 Run a batch in the Upload tab to generate analytics.")

with tab3:
    if 'processing_done' in st.session_state and st.session_state['processing_done']:
        st.subheader("Interactive Data Grid")
        st.caption("Double-click any cell to manually correct OCR errors before exporting.")
        
        df = pd.DataFrame(st.session_state['master_data'])
        metadata_cols = ["Source File", "Lab Name", "Report Date", "Age", "Gender"]
        test_cols = sorted([col for col in df.columns if col not in metadata_cols])
        df = df[metadata_cols + test_cols]
        
        styled_df = df.style.map(highlight_abnormal, subset=test_cols)
        edited_df = st.data_editor(styled_df, use_container_width=True, num_rows="dynamic", height=400)
        
        st.divider()
        col1, col2 = st.columns([1, 4])
        with col1:
            excel_file = "MediParse_Master_Data.xlsx"
            edited_df.to_excel(excel_file, index=False)
            with open(excel_file, "rb") as f:
                st.download_button(label="📥 Download Excel", data=f, file_name=excel_file, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary", use_container_width=True)
    else:
        st.info("✏️ Run a batch to populate the data grid.")
```
