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
        # Open PDF from bytes
        doc = fitz.open(stream=file.read(), filetype="pdf")
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            img_data = pix.tobytes("png")
            images.append(Image.open(io.BytesIO(img_data)))
    else:
        # It's an image file
        images.append(Image.open(file))
    return images

# --- SIDEBAR UI ---
with st.sidebar:
    st.markdown("## 🏥 MediParse AI")
    st.caption("Intelligent Medical Data Extraction")
    st.divider()
    
    st.markdown("### 1. Upload Documents")
    # Added PDF support here!
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
            
            progress_text = "Parsing medical records. Please wait..."
            my_bar = st.progress(0, text=progress_text)
            
            for index, file in enumerate(uploaded_files):
                my_bar.progress((index) / len(uploaded_files), text=f"Analyzing {file.name}...")
                
                # Convert the file (PDF or Image) into a list of images
                report_images = process_file_to_images(file)
                
                # We will merge data if a PDF has multiple pages for the same patient
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
                        # Update metadata if we found it on this page
                        if metadata.get("lab_name") and combined_patient_row["Lab Name"] == "Unknown":
                            combined_patient_row["Lab Name"] = metadata.get("lab_name")
                        if metadata.get("date") and combined_patient_row["Report Date"] == "Unknown":
                            combined_patient_row["Report Date"] = metadata.get("date")
                        if metadata.get("age") and combined_patient_row["Age"] == "Unknown":
                            combined_patient_row["Age"] = metadata.get("age")
                        if metadata.get("gender") and combined_patient_row["Gender"] == "Unknown":
                            combined_patient_row["Gender"] = metadata.get("gender")
                        
                        # Extract tests from this page
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
        
        # --- TOP METRICS ---
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Patient Records", len(df))
        m2.metric("Unique Tests Tracked", len(test_cols))
        
        abnormal_count = df[test_cols].astype(str).apply(lambda x: x.str.contains(r'\(High\)|\(Low\)')).sum().sum()
        m3.metric("Abnormal Flags Detected", abnormal_count)
        
        st.divider()
        
        # --- DYNAMIC VISUALIZATION ---
        if len(df) == 1:
            # SINGLE PATIENT VIEW: Show Normal vs Abnormal Breakdown
            st.subheader("Patient Health Overview")
            st.caption("Breakdown of test results for this individual report.")
            
            # Extract the single patient's tests, dropping empty ones
            patient_data = df.iloc[0][test_cols].dropna().astype(str)
            
            # Count the flags
            high_count = patient_data.str.contains(r'\(High\)').sum()
            low_count = patient_data.str.contains(r'\(Low\)').sum()
            normal_count = len(patient_data) - high_count - low_count
            
            # Create a dataframe for the Plotly donut chart
            status_df = pd.DataFrame({
                'Status': ['Normal', 'High', 'Low'],
                'Count': [normal_count, high_count, low_count]
            })
            status_df = status_df[status_df['Count'] > 0] # Remove zeros
            
            # Build the Donut Chart
            fig = px.pie(
                status_df, 
                values='Count', 
                names='Status', 
                hole=0.4,
                color='Status',
                color_discrete_map={'Normal':'#2e7d32', 'High':'#c62828', 'Low':'#f57f17'} # Green, Red, Orange
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            # BATCH VIEW: Show the original Test Frequency Chart
            st.subheader("Test Frequency Across Batch")
            st.caption("Showing which tests were most commonly ordered across all uploaded patients.")
            
            test_counts = df[test_cols].notna().sum().reset_index()
            test_counts.columns = ['Test Name', 'Number of Patients']
            test_counts = test_counts[test_counts['Number of Patients'] > 0].sort_values(by='Number of Patients', ascending=False)
            
            fig = px.bar(
                test_counts, 
                x='Test Name', 
                y='Number of Patients',
                color='Number of Patients',
                color_continuous_scale='Blues',
                text='Number of Patients'
            )
            fig.update_layout(xaxis_tickangle=-45, margin=dict(t=20, b=20, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
            
    else:
        st.info("📊 Run an extraction in the Upload tab to generate analytics.")
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