import streamlit as st
import pandas as pd
import json
import time
from PIL import Image
from google import genai
from google.genai import types
import plotly.express as px

# --- CONFIGURATION & STYLING ---
st.set_page_config(page_title="MediParse AI", page_icon="🏥", layout="wide")

st.markdown("""
    <style>
    /* Clean up the main container */
    .main .block-container { padding-top: 2rem; max-width: 95%; }
    
    /* Style the metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        color: #0068c9;
    }
    
    /* Subtle gradient header */
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

# --- SIDEBAR UI ---
with st.sidebar:
    st.markdown("## 🏥 MediParse AI")
    st.caption("Intelligent Medical Data Extraction")
    st.divider()
    
    st.markdown("### 1. Upload Documents")
    uploaded_files = st.file_uploader("Select Lab Reports", type=["jpg", "jpeg", "png"], accept_multiple_files=True, label_visibility="collapsed")
    
    st.divider()
    st.info("💡 **Workflow:**\n1. Upload batches of images.\n2. Review automated charts.\n3. Edit data directly in the grid.\n4. Export to Excel.")

# --- MAIN CANVAS UI ---
st.markdown('<div class="custom-header">Medical Report Processing Hub</div>', unsafe_allow_html=True)

# Three logical tabs
tab1, tab2, tab3 = st.tabs(["📤 Upload & Process", "📈 Analytics Dashboard", "✏️ Data Grid & Export"])

with tab1:
    if not uploaded_files:
        st.info("👈 **Awaiting Documents:** Please upload medical report images in the sidebar to begin processing.")
    else:
        st.markdown(f"**{len(uploaded_files)} Document(s) Ready for Processing**")
        
        # Display thumbnails
        cols = st.columns(min(len(uploaded_files), 6))
        for i, file in enumerate(uploaded_files[:6]):
            cols[i].image(Image.open(file), use_container_width=True)
        if len(uploaded_files) > 6:
            st.caption(f"...and {len(uploaded_files) - 6} more.")
        
        st.divider()
        
        if st.button("🚀 Process Batch", type="primary"):
            st.session_state['processing_done'] = False
            all_patients_data = []
            
            progress_text = "Parsing medical records. Please wait..."
            my_bar = st.progress(0, text=progress_text)
            
            for index, file in enumerate(uploaded_files):
                my_bar.progress((index) / len(uploaded_files), text=f"Analyzing {file.name}...")
                
                image = Image.open(file)
                raw_json = extract_data_from_image(image, API_KEY)
                
                if raw_json:
                    metadata = raw_json.get("metadata", {})
                    patient_row = {
                        "Source File": file.name,
                        "Lab Name": metadata.get("lab_name", "Unknown"),
                        "Report Date": metadata.get("date", "Unknown"),
                        "Age": metadata.get("age", "Unknown"),
                        "Gender": metadata.get("gender", "Unknown")
                    }
                    
                    for item in raw_json.get("tests", []):
                        raw_name = item.get("parameter", "").strip()
                        std_name = STANDARD_TERMS.get(raw_name, raw_name)
                        cell_value = f"{item.get('result', '')} {item.get('unit', '')}".strip()
                        if item.get("flag") in ["High", "Low"]:
                            cell_value += f" ({item['flag']})"
                        patient_row[std_name] = cell_value
                        
                    all_patients_data.append(patient_row)
                
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
        
        # Calculate total abnormalities
        abnormal_count = df[test_cols].astype(str).apply(lambda x: x.str.contains(r'\(High\)|\(Low\)')).sum().sum()
        m3.metric("Abnormal Flags Detected", abnormal_count)
        
        st.divider()
        
        # --- VISUALIZATION ---
        st.subheader("Test Frequency Across Batch")
        # Count how many non-null values exist in each test column
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
        st.info("📊 Run a batch in the Upload tab to generate analytics.")

with tab3:
    if 'processing_done' in st.session_state and st.session_state['processing_done']:
        st.subheader("Interactive Data Grid")
        st.caption("Double-click any cell to manually correct OCR errors before exporting.")
        
        df = pd.DataFrame(st.session_state['master_data'])
        metadata_cols = ["Source File", "Lab Name", "Report Date", "Age", "Gender"]
        test_cols = sorted([col for col in df.columns if col not in metadata_cols])
        df = df[metadata_cols + test_cols]
        
        # Use data_editor instead of dataframe!
        styled_df = df.style.map(highlight_abnormal, subset=test_cols)
        
        # Capture the edited dataframe
        edited_df = st.data_editor(
            styled_df,
            use_container_width=True,
            num_rows="dynamic", # Allows user to delete a row if they want
            height=400
        )
        
        st.divider()
        
        col1, col2 = st.columns([1, 4])
        with col1:
            excel_file = "MediParse_Master_Data.xlsx"
            # Save the EDITED dataframe to Excel, not the raw one
            edited_df.to_excel(excel_file, index=False)
            with open(excel_file, "rb") as f:
                st.download_button(
                    label="📥 Download Excel",
                    data=f,
                    file_name=excel_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    use_container_width=True
                )
    else:
        st.info("✏️ Run a batch to populate the data grid.")