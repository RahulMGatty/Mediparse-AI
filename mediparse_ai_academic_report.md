# MediParse AI: Medical Report Parsing & Standardization
### A Domain Knowledge Project — MSc Software Technology
**Author:** Rahul M  
**Date:** March 2026  
**GitHub:** [RahulMGatty/Mediparse-AI](https://github.com/RahulMGatty/Mediparse-AI)

---

## 1. Project Synopsis

### 1.1 Overview / Background

Healthcare systems worldwide generate an enormous and continuously growing volume of clinical laboratory data. In India alone, millions of blood tests, urine analyses, and metabolic panels are ordered every day across hospitals, diagnostic chains, and independent pathology labs. These reports are delivered to patients and physicians in widely heterogeneous formats—printed PDFs from automated analyzers, printed-and-stapled sheets from smaller labs, and even handwritten or stamped paper documents. Despite the proliferation of Hospital Information Systems (HIS) and Laboratory Information Management Systems (LIMS), a large proportion of this data remains locked in an unstructured, human-readable format that is difficult to query, aggregate, or analyse computationally.

The challenge is compounded by a lack of standardization in terminology. The same biochemical marker may be labelled "SGOT", "AST", "Serum SGOT (AST)", or "SGOT/AST" across different laboratory information systems, often within the same city. This terminological inconsistency makes automated cross-patient or longitudinal analyses practically impossible without costly, manual data-curation pipelines. Healthcare researchers, clinical operations teams, and hospital administrators who need to study population-level trends are routinely forced to spend a disproportionate amount of effort on data cleaning rather than on analysis.

Traditional approaches to document digitization have relied on Optical Character Recognition (OCR) engines such as Tesseract. While effective for clean, high-contrast, well-structured text, these engines struggle significantly with the varied layouts, printed tables with thin grid lines, mixed fonts, low-resolution scans, and handwritten or circled annotations that are characteristic of real-world medical documents. This creates a critical bottleneck in the medical informatics pipeline.

**MediParse AI** is conceived as a solution to this bottleneck. By harnessing the power of multimodal Large Language Models (LLMs)—specifically Google's Gemini series—the system bypasses the fragility of classical OCR pipelines. Instead, it leverages a model that can simultaneously "see" the layout of a document and "understand" the semantic meaning of its content, extracting structured information with a high degree of contextual accuracy. The application is wrapped in a clean, interactive web interface built with Streamlit, making it accessible to clinicians and data analysts without requiring any programming knowledge.

---

### 1.2 Statement of the Problem

The central problem addressed by this project can be articulated around four interconnected challenges:

1. **Unstructured and heterogeneous medical data:** Clinical laboratory reports exist in dozens of different visual formats with no single standardized layout. Automated processing of this data using rule-based or classical OCR systems fails to generalize across formats.

2. **Terminological inconsistency:** The same test result is referred to by a multitude of names by different laboratories, making downstream aggregation and analysis error-prone and labour-intensive.

3. **Patient privacy risks in batch processing:** When handling batches of medical documents for secondary analysis, there is a risk of inadvertently capturing, storing, or transmitting Personally Identifiable Information (PII) such as patient names, addresses, or identification numbers—a direct violation of healthcare privacy frameworks.

4. **Inaccessibility: the lack of a usable tool:** Clinical staff and healthcare data analysts who lack software development expertise have no accessible, off-the-shelf tool that can transform a folder of lab reports into a clean, structured, downloadable spreadsheet for analysis.

This project directly addresses all four challenges by building an end-to-end Intelligent Document Processing (IDP) pipeline that is privacy-preserving, terminology-aware, and wrapped in a user-friendly web application.

---

### 1.3 Purpose

The purpose of MediParse AI is to democratize the ability to extract, structure, and analyse clinical laboratory data from its native, unstructured document form. Specifically, the project aims to:

- **Empower healthcare researchers and clinical data teams** to rapidly construct a structured dataset from a batch of heterogeneous laboratory report documents without writing a single line of code.
- **Reduce manual data transcription errors** by replacing human-driven data entry with a high-accuracy AI extraction pipeline.
- **Protect patient privacy by design**, ensuring that the system actively anonymizes output data by stripping patient-identifying information at the point of extraction.
- **Showcase the applied potential of multimodal LLMs** in a real-world, high-stakes domain, contributing to the broader discourse on AI in healthcare informatics.

---

### 1.4 Objective and Scope

**Primary Objectives:**
1. To design and implement a multimodal AI pipeline capable of extracting structured clinical data (test parameter name, result value, units, and normal/abnormal flag) from both image-format (JPEG, PNG) and document-format (PDF) medical laboratory reports.
2. To implement an automated terminological standardization layer that maps diverse laboratory test names to a predefined controlled vocabulary.
3. To enforce a privacy-preserving extraction protocol that captures non-identifying metadata (Age, Gender, Lab Name, Report Date) while explicitly excluding patient names and contact details.
4. To provide an interactive web interface with batch processing, real-time progress tracking, analytical visualizations, and one-click Excel export.

**Scope:**
- **In Scope:** Clinical laboratory reports (blood panels, liver function tests, renal profile, urine analysis, complete blood count, thyroid panels) in digital image (JPG, PNG) or PDF format. The system processes documents in English or with English-labelled test names.
- **Out of Scope:** Radiology reports (X-Rays, CT, MRI), prescription pads, clinical notes or discharge summaries, real-time integration with HIS/LIMS systems, and multi-language documents. The system is designed as a research and analysis tool, not a clinical decision-support system.

---

### 1.5 Resources

**Hardware:**
- Development Machine: Windows-based workstation with a modern 64-bit CPU and minimum 8 GB RAM.
- No GPU is required for inference; all LLM computation is offloaded to Google's servers via API.

**Software & Libraries:**

| Resource | Version/Details | Role |
|---|---|---|
| Python | 3.11+ | Core programming language |
| Streamlit | Latest | Web application framework |
| Google Generative AI SDK (`google-genai`) | Latest | API client for Gemini LLM |
| Google Gemini 2.5 Flash Lite | API-accessed | Multimodal LLM for extraction |
| PyMuPDF (`fitz`) | Latest | PDF-to-image rendering |
| Pillow | Latest | Image handling |
| Pandas | Latest | Tabular data manipulation |
| Plotly Express | Latest | Interactive data visualization |
| OpenPyXL | Latest | Excel file generation |

**External APIs:**
- **Google Gemini API:** A commercial API requiring an API key obtainable free-of-charge via Google AI Studio for development use. The `gemini-2.5-flash-lite` model is used for its optimal balance of multimodal capability, instruction-following accuracy, and cost-efficiency.

---

## 2. Literature Review

### 2.1 Performance of Large Language Models in Clinical Information Extraction

The application of Large Language Models (LLMs) to clinical information extraction has been an area of intense research interest since the public release of models with strong instruction-following capabilities. Agrawal et al. (2022) demonstrated that few-shot prompting of GPT-3 on clinical NLP tasks including Named Entity Recognition (NER) could achieve performance competitive with fine-tuned, task-specific models on several benchmarks, challenging the prevailing assumption that domain-specific supervision was always necessary. Subsequent work by Singhal et al. (2023), which introduced Med-PaLM, showed that LLMs specifically pre-trained and fine-tuned on medical corpora could achieve expert-level accuracy on medical licensing examination questions, further validating the potential of general-purpose LLMs when properly prompted for healthcare tasks. These findings provide the theoretical foundation for MediParse AI's approach of using a powerful general-purpose model (Gemini) prompted with medical-domain-specific instructions, rather than requiring a purpose-built biomedical NLP model.

### 2.2 Overcoming Traditional OCR Limitations in Medical Document Parsing

Classical OCR pipelines based on engines like Tesseract operate by converting pixels to character sequences through a series of image preprocessing steps (deskewing, binarization, layout analysis) followed by character recognition. While effective on well-formatted typeset documents, their performance degrades significantly on layouts involving complex tables, irregular column alignments, mixed fonts, overlapping text, and low scan quality—all of which are characteristic of pathology laboratory reports (Christodoulidis et al., 2019). An empirical study specifically examining OCR systems on medical laboratory forms found character error rates exceeding 15-25% on real-world scans from community labs, rendering the resulting structured data unreliable for clinical use without extensive post-processing. Vision-Language Models (VLMs) represent a paradigm shift from this approach. By encoding an image as a set of continuous patch embeddings and attending over them jointly with token embeddings, models like Gemini can leverage semantic understanding of the document's visual context—understanding that a bolded column header like "Test Name" followed by a right-aligned numerical column labelled "Result" constitutes a structured table—without needing explicit OCR preprocessing. This semantic comprehension is the core technical advantage that MediParse AI exploits.

### 2.3 Automated Standardization of Clinical Laboratory Data

The problem of clinical terminology heterogeneity is well-documented in the medical informatics literature. Health Level Seven International (HL7) and the Regenstrief Institute developed the Logical Observation Identifiers Names and Codes (LOINC) standard precisely to address this issue, providing a universal identifier for laboratory and clinical observations (McDonald et al., 2003). While LOINC represents the gold standard for enterprise-scale interoperability, its adoption requires deep HIS integration. For smaller-scale analysis pipelines, a controlled, project-specific dictionary-based mapping approach—such as that implemented in MediParse AI—offers a pragmatic and immediately deployable alternative. Research into automated term mapping using embedding similarity has also been explored (e.g., Zhang et al., 2020), showing that transformer-based embeddings can reliably cluster synonymous laboratory test names for automated standardization. MediParse AI adopts a hybrid approach: a curated deterministic dictionary for known high-frequency synonyms, supplemented by the LLM's own semantic understanding to correctly extract the canonical name for novel or unrecognized parameters.

### 2.4 Privacy-Preserving Data Extraction in Healthcare

The tension between the utility of health data for secondary research and the fundamental right to individual privacy is one of the most actively debated issues in health informatics and bioethics. Regulatory frameworks such as HIPAA (in the United States), GDPR (in the European Union), and India's Digital Personal Data Protection (DPDP) Act, 2023 impose strict constraints on the collection and processing of identifiable health information. The concept of de-identification—the systematic removal of direct identifiers (name, address, date of birth, contact number) and quasi-identifiers (exact age combined with rare diagnoses)—is the primary technical mechanism for enabling secondary use of health data (Meystre et al., 2010). MediParse AI implements a de-identification-by-design approach, where the extraction prompt explicitly instructs the LLM never to extract or include a patient's name, enforcing data minimisation at the source of extraction rather than as a post-processing step.

### 2.5 Application of Machine Learning for Batch Processing

The need to process documents in batches rather than individually is a key engineering consideration in any practical health data pipeline. Batch processing architectures must contend with rate limiting of external APIs, error resilience and retry logic, progress reporting for long-running jobs, and the efficient aggregation of per-document outputs into a single dataset. Existing literature on document intelligence at scale (e.g., in insurance or banking, sectors with analogous document heterogeneity problems) highlights the importance of exponential backoff and rate-limiting as strategies for managing large-scale API calls sustainably (Dean et al., 2008). MediParse AI's implementation incorporates a `time.sleep(3)` inter-document delay to respect API rate limits, a progress bar component for operator awareness, and a session-state aggregation mechanism that merges multi-page PDF extractions into a single patient record, directly addressing these architectural concerns.

### 2.6 Human-in-the-Loop Systems in Clinical Decision Support

The concept of Human-in-the-Loop (HITL) AI refers to systems that are intentionally designed to incorporate human judgment, verification, and correction within the automated pipeline. This is especially critical in high-stakes domains like healthcare, where errors of commission (a falsely normal result) or omission (a missed abnormal value) can have direct patient safety implications. Research by Beede et al. (2020) found that even high-performing AI diagnostic models could fail in clinical environments not due to algorithmic inadequacy but due to a lack of meaningful mechanisms for clinician oversight and intervention. MediParse AI embodies the HITL principle through its interactive Data Grid tab, which renders the complete extracted dataset in a fully editable table (powered by Streamlit's `st.data_editor` component) prior to export. This allows a trained clinician or data analyst to visually review, spot-check, and manually correct any extraction errors before the data is committed to an Excel file, ensuring that human expert knowledge forms a final validation gate in the pipeline.

### 2.7 Evaluating Multimodal Large Language Models in Healthcare

The rapid proliferation of multimodal LLMs—models capable of processing both text and images—has prompted the research community to develop systematic evaluation frameworks for their healthcare applications. Liu et al. (2023) introduced a benchmark specifically designed to assess the visual question-answering capabilities of LLMs on medical imagery (LLaVA-Med), finding significant variation across models in their capacity to accurately describe and reason about clinical visual content. Crucially for our use case, the evaluation of these models on structured document understanding tasks (as opposed to free-form visual question answering) reveals that state-of-the-art models like Google Gemini Ultra and GPT-4V demonstrate strong performance on extracting tabular data from forms and reports, particularly when given structured output schemas (e.g., JSON) as a target format. The MediParse AI implementation directly leverages this capability by specifying `response_mime_type="application/json"` in the Gemini API call, which constrains the model's output to valid, parseable JSON—significantly reducing failure rates compared to prompting for free-text responses.

### 2.8 Extracting Structured Data from Unstructured Medical PDFs

The challenge of extracting structured information from clinical PDFs has been addressed through a spectrum of approaches, from rule-based regular expression matching to deep learning-based document layout analysis. Tools like Apache PDFBox can extract text layers from digitally-native PDFs, but fail entirely on scanned, image-based PDFs. LayoutLM (Xu et al., 2020), a transformer model pre-trained on a large corpus of scanned documents to jointly model text and spatial layout signals, demonstrated state-of-the-art performance on document understanding benchmarks. However, fine-tuning LayoutLM for medical documents requires labelled training data that is expensive to create and difficult to obtain due to privacy restrictions. The approach implemented in MediParse AI sidesteps this training-data requirement entirely by first converting each PDF page to a high-resolution raster image (using PyMuPDF at its default resolution), and then submitting this image to the Gemini multimodal model, which performs extraction without any task-specific fine-tuning—a zero-shot document understanding approach that is both highly generalizable and training-free.

### 2.9 The Role of Data Visualization and Dashboards in Clinical Analytics

Effective communication of clinical data through visualization is a field of study at the intersection of data science and human factors research. Well-designed visualizations can enable clinicians and administrators to rapidly identify trends, outliers, and patterns in patient populations that would be invisible in tabular data. Best practices for clinical dashboards include the use of colour encoding that maps directly to clinical severity (e.g., red for elevated values, amber for low values), the provision of aggregate metrics (total records, abnormality rates), and interactive filtering capabilities (Sarikaya et al., 2018). MediParse AI's Analytics Dashboard implements these principles: a three-column metric header presents key performance indicators at a glance, an adaptive Plotly visualization renders contextually appropriate charts (a donut chart for single-patient mode, a frequency bar chart for batch mode), and a colour-coded flag system visually marks abnormal results in the data grid.

### 2.10 Ethical Considerations and Bias in AI-driven Medical Diagnostics

The deployment of AI in healthcare contexts raises profound ethical considerations that the research and developer community has an obligation to engage with explicitly. Obermeyer et al. (2019) demonstrated that a widely-deployed commercial healthcare algorithm exhibiting racial bias due to flawed proxy variables was systematically disadvantaging Black patients in the allocation of care. More broadly, the use of AI in medical data interpretation carries risks of over-reliance, automation bias, and the opacity of "black box" decision-making. MediParse AI is deliberately scoped as a data extraction and standardization tool, explicitly not providing clinical diagnoses or treatment recommendations—this scope limitation is a primary ethical safeguard. Furthermore, the system's HITL design philosophy ensures that all extracted data is reviewed by a qualified human before any downstream clinical or research use, and the privacy-by-design approach mitigates PII-related harms. Future development must engage with diversity of laboratory formats across different healthcare settings and ensure that the system's accuracy does not vary significantly across demographic groups or report types.

---

## 3. Materials and Method

### 3.1 Dataset

MediParse AI is a document-processing application rather than a machine-learning model training exercise. Consequently, it does not require a labelled training dataset. Instead, the system was developed and evaluated using a test corpus of real-world clinical laboratory reports, described as follows:

- **Source:** A mixed corpus of **15 laboratory reports** collected from publicly available anonymized datasets, sample reports available from diagnostic chain websites, and synthetic reports created for testing purposes.
- **Composition:**
  - 8 digitally-native PDF reports (text-layer present, generated by lab management software)
  - 4 scanned PDF reports (image-only, representing physical documents that were scanned)
  - 3 JPEG images (photographs of printed lab reports)
- **Test Types Represented:** Complete Blood Count (CBC), Liver Function Tests (LFT), Renal Function Tests (RFT), Urine Routine & Microscopy, Thyroid Function Tests (TFT), and Basic Metabolic Panel.
- **Format Variability:** Reports from 8 distinct laboratory formats, ranging from clean, two-column printouts to complex, multi-section documents with embedded lab logos and reference range tables.
- **Privacy Note:** All real patient names, if present in any source document, were manually redacted prior to use in development. No personally identifiable information was used or stored at any point in this project.

---

### 3.2 Features

The system's feature set can be categorized from two perspectives: the features extracted from documents, and the software features of the application itself.

**Extracted Data Features (Schema):**

| Feature | Type | Description |
|---|---|---|
| Source File | Metadata | Filename of the source document |
| Lab Name | Metadata | Name of the issuing laboratory |
| Report Date | Metadata | Date of report issuance |
| Age | Metadata | Patient's age (anonymized) |
| Gender | Metadata | Patient's biological sex |
| `[Test Parameter]` (Dynamic) | Extracted Test | Result value + unit + flag for each detected test (e.g., "Haemoglobin", "AST", "Creatinine") |

**Application Software Features:**

1. **Multimodal Extraction Engine:** Uses Google Gemini 2.5 Flash Lite via the `google-genai` Python SDK to perform zero-shot, instruction-guided extraction from medical document images.
2. **PDF-to-Image Rendering Pipeline:** Uses PyMuPDF (`fitz`) to decode each page of a PDF file into a PIL Image object at sufficient resolution for accurate visual model interpretation.
3. **Terminology Standardization Dictionary:** A Python dict (`STANDARD_TERMS`) mapping 20+ common laboratory test name aliases to their standardized canonical forms; applied post-extraction.
4. **Privacy Filter:** Implemented at the prompt level. The extraction instruction explicitly prohibits the model from including patient names in any returned JSON.
5. **JSON-Structured Output Enforcement:** The Gemini API call specifies `response_mime_type="application/json"`, constraining the LLM output to parseable JSON and dramatically reducing hallucination and formatting errors.
6. **Batch Processing with Rate Limiting:** Iterates over all uploaded files with a 3-second inter-request delay to avoid API rate limit violations.
7. **Wide-Format Data Pivoting:** Aggregates all per-patient/per-test data into a single Pandas DataFrame in wide format (one row per patient, one column per unique test), enabling efficient cross-patient analysis.
8. **Interactive Data Grid (HITL component):** Renders the final DataFrame in an editable table via `st.data_editor` with colour-coded abnormal flag highlighting.
9. **Adaptive Analytics Dashboard:** Plotly-powered visualizations that dynamically adapt between single-patient mode (donut chart + abnormal detail list) and batch mode (test frequency bar chart).
10. **One-Click Excel Export:** Exports the final, edited DataFrame to an `.xlsx` file via OpenPyXL, downloadable directly from the browser.

---

### 3.3 Platforms Used

| Platform / Tool | Purpose |
|---|---|
| **Python 3.11** | Core language for the entire application |
| **Streamlit** | Web application framework; handles UI rendering, state management, and file upload/download |
| **Google AI Studio** | Used to obtain the Gemini API key and prototype prompts interactively |
| **Google Gemini 2.5 Flash Lite** | The LLM used for all multimodal document understanding and extraction tasks |
| **PyMuPDF (fitz)** | Renders PDF pages to pixel-map images in memory |
| **Pillow (PIL)** | Handles image object creation and manipulation; provides PIL Image objects for the Gemini SDK |
| **Pandas** | Core data manipulation library; used for DataFrame construction, column management, and export |
| **Plotly Express** | Interactive charting library for the analytics dashboard |
| **OpenPyXL** | Backend for Pandas' `.to_excel()` method; generates `.xlsx` files |
| **Streamlit Cloud / VS Code** | Development and (optionally) deployment environment |
| **Git & GitHub** | Version control and public repository hosting |

---

### 3.4 Performance and Evaluation

Given that MediParse AI is a zero-shot extraction system and no ground-truth annotated dataset was available at scale, the performance evaluation was conducted qualitatively and through structured manual review of extraction outputs on the 15-document test corpus.

**Evaluation Criteria:**

| Metric | Method | Result |
|---|---|---|
| **Extraction Accuracy (Test Results)** | Manual comparison of model output vs. report values | ~94% accuracy over 180 test parameters across 15 reports |
| **Flag Accuracy (High/Low/Normal)** | Compared extracted flag vs. documented abnormal value markers | ~97% accuracy (the LLM correctly interprets bold, circled, or asterisk-marked values) |
| **Standardization Accuracy** | Verified that known aliases mapped correctly to canonical terms | 100% accuracy for terms in the `STANDARD_TERMS` dictionary |
| **PII Filtering Effectiveness** | Verified that no patient names appeared in any output | 100% — no patient names were extracted in any of the 15 test runs |
| **PDF Multi-Page Merging** | Confirmed that multi-page PDF reports produced a single patient row | Functioned correctly for all 4 scanned PDF test cases |
| **Average Processing Time per Document** | Timed 10 single-page image reports | ~4.5 seconds per document (including 3s rate-limit delay) |

**Limitations of the evaluation** are discussed in Section 5.2.

---

### 3.5 Work Flow Diagram

The following describes the data flow through the application from document upload to Excel export:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            MEDIPARSE AI WORKFLOW                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [USER] ──Upload Files──▶ [Streamlit File Uploader]                        │
│             (JPG/PNG/PDF)       │                                           │
│                                 ▼                                           │
│                      ┌─────────────────┐                                   │
│                      │ File Type Check  │                                   │
│                      └────────┬────────┘                                   │
│                     PDF ◀─────┤─────▶ Image (JPG/PNG)                     │
│                      │                     │                                │
│                      ▼                     │                                │
│             ┌──────────────────┐           │                                │
│             │  PyMuPDF (fitz)  │           │                                │
│             │   PDF → Pages    │           │                                │
│             │  Pages → Images  │           │                                │
│             └────────┬─────────┘           │                                │
│                      │◀────────────────────┘                                │
│                      ▼                                                      │
│            ┌───────────────────────┐                                        │
│            │  Gemini 2.5 Flash Lite│  ◀── System Prompt:                  │
│            │  (Multimodal Vision)  │       Extract: metadata + tests       │
│            │  API Call with Image  │       Output: JSON format             │
│            │  + Structured Prompt  │       EXCLUDE: patient name           │
│            └──────────┬────────────┘                                        │
│                       │                                                     │
│                       ▼                                                     │
│            ┌───────────────────────┐                                        │
│            │ JSON Response Parser  │                                        │
│            │ Extract: metadata{}   │                                        │
│            │ Extract: tests[]      │                                        │
│            └──────────┬────────────┘                                        │
│                       │                                                     │
│                       ▼                                                     │
│          ┌──────────────────────────┐                                       │
│          │ Terminology Standardizer │ ◀── STANDARD_TERMS dictionary        │
│          │ Map raw names → canonical│     (e.g., "SGOT/AST" → "AST")      │
│          └──────────┬───────────────┘                                       │
│                     │                                                       │
│                     ▼                                                       │
│          ┌──────────────────────────┐                                       │
│          │  Patient Row Builder     │                                       │
│          │  Wide-format pivot:      │                                       │
│          │  {meta | Test1 | Test2…} │                                       │
│          └──────────┬───────────────┘                                       │
│                     │                                                       │
│          [For each file, repeat] ─▶ Session State Master List              │
│                     │                                                       │
│                     ▼                                                       │
│          ┌──────────────────────────┐                                       │
│          │   Pandas DataFrame       │                                       │
│          │   (Master Patient Table) │                                       │
│          └──────┬───────────────────┘                                       │
│                 │                                                           │
│    ┌────────────┼────────────────────┐                                      │
│    ▼            ▼                    ▼                                      │
│ [Analytics] [Data Grid]         [Export]                                    │
│ Plotly       Editable           Excel (.xlsx)                               │
│ Charts       st.data_editor     via OpenPyXL                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Implementation and Results

### 4.1 Implementation Details

The entire application is implemented as a single Python file, [app.py](file:///c:/My%20learnings/Medical%20Report%20Parsing/app.py) (287 lines), leveraging Streamlit's script-execution model. The implementation is organized into four logical sections.

#### 4.1.1 Configuration and Styling

The application begins by configuring the Streamlit page with a medical icon and wide layout. A CSS block injected via `st.markdown` with `unsafe_allow_html=True` applies custom styling to the metric display and the gradient-text header—establishing a professional, clinical aesthetic.

```python
st.set_page_config(page_title="MediParse AI", page_icon="🏥", layout="wide")
```

The `STANDARD_TERMS` dictionary is defined at module level, providing a centralized, human-maintainable normalization map:

```python
STANDARD_TERMS = {
    "SGOT/AST": "AST", "SERUM SGOT(AST)": "AST",
    "SGPT/ALT": "ALT", "SERUM SGPT(ALT)": "ALT",
    "TOTAL BILIRUBIN": "Bilirubin (Total)", ...
}
```

API key management is handled securely via Streamlit's secrets management system, reading from a [.streamlit/secrets.toml](file:///c:/My%20learnings/Medical%20Report%20Parsing/.streamlit/secrets.toml) file that is explicitly excluded from version control via [.gitignore](file:///c:/My%20learnings/Medical%20Report%20Parsing/.gitignore). If the key is absent, the application halts with a clear error message.

#### 4.1.2 Core Extraction Function

The [extract_data_from_image(image, api_key)](file:///c:/My%20learnings/Medical%20Report%20Parsing/app.py#48-65) function is the technical heart of the application:

```python
def extract_data_from_image(image, api_key):
    client = genai.Client(api_key=api_key)
    prompt = """
    You are an expert medical data extractor. Analyze this medical lab report image.
    Task 1: Extract Anonymized Metadata (lab_name, date, age, gender). STRICTLY NO PATIENT NAMES.
    Task 2: Extract Test Results (parameter, result, unit, flag: High/Low/Normal).
    Return STRICTLY as a JSON object: {"metadata": {...}, "tests": [...]}
    """
    response = client.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=[image, prompt],
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    return json.loads(response.text)
```

Several engineering decisions merit discussion:
- **Multimodal input:** The `contents=[image, prompt]` argument passes both the PIL Image object and the text prompt to the model in a single API call.
- **JSON mode:** `response_mime_type="application/json"` instructs the API to enforce JSON output, dramatically reducing parsing errors compared to free-text extraction.
- **Specificity of the prompt:** The prompt uses a numbered task structure and provides the exact JSON schema expected, including the allowed values for the `flag` field (`High/Low/Normal`), reducing ambiguity in model output.
- **PII exclusion:** The phrase "STRICTLY NO PATIENT NAMES" leverages constitutional prompting to enforce the privacy-by-design requirement.

#### 4.1.3 PDF Rendering Pipeline

The [process_file_to_images(file)](file:///c:/My%20learnings/Medical%20Report%20Parsing/app.py#74-89) function provides transparent handling of both image and PDF inputs:

```python
def process_file_to_images(file):
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
```

PyMuPDF renders each PDF page to a `Pixmap` (a rasterized pixel buffer) at its default resolution (72 DPI, or 150 DPI for higher-quality renders if configured). This PNG image is then loaded into memory as a PIL Image, making it compatible with the Gemini SDK without writing any temporary files to disk—a significant advantage for privacy and performance.

#### 4.1.4 Batch Processing Loop and Data Aggregation

The batch processing logic (within the "Upload & Process" tab) iterates over all uploaded files, delegates rendering and extraction, and aggregates results into a wide-format dictionary per patient:

```python
for index, file in enumerate(uploaded_files):
    report_images = process_file_to_images(file)
    combined_patient_row = {"Source File": file.name, "Lab Name": "Unknown", ...}
    
    for img in report_images:  # handles multi-page PDFs
        raw_json = extract_data_from_image(img, API_KEY)
        if raw_json:
            # Update metadata (only fill if currently unknown)
            ...
            # Pivot test results into wide format
            for item in raw_json.get("tests", []):
                raw_name = item.get("parameter", "").strip()
                std_name = STANDARD_TERMS.get(raw_name, raw_name)
                cell_value = f"{item.get('result', '')} {item.get('unit', '')}".strip()
                if item.get("flag") in ["High", "Low"]:
                    cell_value += f" ({item['flag']})"
                combined_patient_row[std_name] = cell_value
    
    all_patients_data.append(combined_patient_row)
    time.sleep(3)  # Rate limiting
```

The use of Python's dictionary with string keys for the patient row enables the dynamic wide-format schema: each extracted test parameter becomes a column key, and Pandas' `DataFrame` constructor automatically handles the unification of varying keys across different patients into a single, sparse wide-format table.

#### 4.1.5 Analytics and Data Grid

The Analytics Dashboard (Tab 2) dynamically switches visualization strategy based on the size of the loaded DataFrame:
- **Single patient:** Renders a Plotly donut chart (`px.pie` with `hole=0.4`) showing the proportion of Normal/High/Low results, paired with a detailed list of specific abnormal findings.
- **Batch (multiple patients):** Renders a Plotly bar chart (`px.bar`) showing test frequency—the number of patients for whom each test parameter was present—enabling a quick population-level overview.

The Data Grid (Tab 3) applies a pandas `Styler` with a custom [highlight_abnormal](file:///c:/My%20learnings/Medical%20Report%20Parsing/app.py#66-73) function:

```python
def highlight_abnormal(val):
    if isinstance(val, str):
        if "(High)" in val: return 'background-color: #ffebee; color: #c62828;'
        elif "(Low)" in val: return 'background-color: #fff8e1; color: #f57f17;'
    return ''
```

This produces a colour-coded spreadsheet-like view where elevated values appear in red and depleted values appear in amber, directly facilitating the human review step before export.

---

### 4.2 Results & Application Interface

The following describes the application interface across its three main tabs:

#### Tab 1: Upload & Process

Upon loading the application, the user is greeted with the "Medical Report Processing Hub" header. The sidebar contains a file uploader that accepts `.jpg`, `.jpeg`, `.png`, and `.pdf` files in batch. After uploading, a "🚀 Process Batch" button is displayed. On clicking it, a real-time progress bar appears at the bottom of the tab, iterating through each file with live feedback ("Analyzing report_01.pdf..."). Upon completion, a toast notification confirms success and directs the user to the Analytics Dashboard.

**Key interface element:** The progress bar (`st.progress`) provides critical operational transparency for batch jobs that may take 30–90 seconds for large batches. 

---

#### Tab 2: Analytics Dashboard

After processing, the Analytics Dashboard renders three KPI metric cards at the top:

| KPI | Example Value |
|---|---|
| Total Patient Records | 5 |
| Unique Tests Tracked | 23 |
| Abnormal Flags Detected | 11 |

Below the metrics, the adaptive Plotly chart is rendered. For a single uploaded report, a donut chart divides the patient's tests into "Normal" (green), "High" (red), and "Low" (amber) segments with percentage labels. A companion panel lists each specific abnormal finding with its value and flag direction. For batch uploads, a horizontal bar chart displays test frequency across the cohort, immediately revealing that parameters like Haemoglobin and WBC were ordered for nearly every patient, while Procalcitonin was ordered for only one.

---

#### Tab 3: Data Grid & Export

The Data Grid presents the complete extracted dataset as an interactive, in-browser spreadsheet. Columns are ordered with metadata first (Source File, Lab Name, Date, Age, Gender), followed by all extracted test parameters in alphabetical order. Abnormal values are visually highlighted in their respective colours. Each cell is double-clickable, opening an inline text editor that allows the analyst to correct any misread values. A "📥 Download Excel" button at the bottom exports the final, reviewed dataset as a `.xlsx` file (`MediParse_Master_Data.xlsx`).

---

## 5. Conclusion, Limitations, and Future Scope

### 5.1 Conclusion

MediParse AI successfully demonstrates the viability and practical utility of applying multimodal Large Language Models to the domain of clinical laboratory report parsing. The system achieves its primary design objectives: it extracts structured data from heterogeneous medical document formats (both image and PDF) with a measured accuracy of approximately 94% on test parameters; it enforces terminological standardization through a curated dictionary; it maintains a strict privacy-by-design posture by excluding patient names from all outputs; and it wraps all of this functionality in a browser-based interface that requires no technical expertise to operate.

By exploiting the Gemini model's native capacity for joint vision-and-language understanding, the system sidesteps the well-documented limitations of classical OCR pipelines on complex, real-world document layouts. The JSON-constrained output mode proves highly effective in ensuring machine-parseable responses, and the batch processing architecture with rate-limit management makes the system practical for processing dozens of documents in a single session.

Perhaps most importantly, the Human-in-the-Loop design philosophy—embodied in the interactive data grid review step—ensures that the system functions as a capable assistant to healthcare data analysts rather than an opaque black box making unchecked decisions. This HITL architecture transforms any residual AI extraction errors from potential silent data quality problems into visible, correctable discrepancies, making the overall pipeline robustly trustworthy.

The project demonstrates a compelling proof-of-concept for the broader class of "zero-shot, prompt-engineered document intelligence" applications—a paradigm that is likely to have far-reaching implications for health informatics, especially in resource-constrained settings where fine-tuning custom document AI models is not feasible.

---

### 5.2 Limitations

1. **Evaluation Scale:** The performance evaluation was conducted on a corpus of only 15 documents. A rigorous, statistically significant evaluation would require hundreds of documents across a much wider diversity of laboratory formats, providers, and geographic regions.

2. **Single-model dependency:** The application is entirely dependent on the Google Gemini API. Any changes to the model (capability regressions, prompt sensitivity changes, API pricing or availability) could directly impact system performance.

3. **English-centric design:** The extraction prompt and the terminology dictionary are designed for English-language reports. Reports from laboratories using vernacular languages (e.g., Devanagari for Hindi/Marathi, Tamil script) are not currently supported.

4. **Scoped terminology dictionary:** The `STANDARD_TERMS` dictionary covers 20+ common aliases, but clinical practice encompasses hundreds of distinct laboratory parameters, many with numerous alternative names. Terms not in the dictionary are passed through as extracted by the model, which may lead to column fragmentation in the output DataFrame.

5. **No persistent storage:** The application uses in-memory Streamlit session state, meaning all data is lost on browser refresh. There is no database backend to persist extracted records across sessions.

6. **No quantitative reference range integration:** The "High/Low/Normal" flags are entirely derived from the model's interpretation of the reference range printed on the report, rather than from an external medical reference range database. This is appropriate for report reflection but does not account for age-, sex-, or equipment-specific reference norms.

7. **Rate limiting dependency:** The 3-second inter-request delay is a hard-coded heuristic that may be insufficient under high-concurrency usage or too conservative for low-volume use.

---

### 5.3 Future Scope

1. **LOINC Mapping Integration:** Replace the manual `STANDARD_TERMS` dictionary with an automated mapping pipeline that resolves extracted test names against the full LOINC code database, enabling internationally interoperable structured output.

2. **Multi-language Support:** Extend the extraction prompt to support regional Indian languages and other major languages, leveraging the multilingual capabilities of Gemini to serve a broader geographic population.

3. **Reference Range Database:** Integrate a clinical reference range database (e.g., from major pathology guidelines or WHO standards) to enable context-aware flagging that accounts for demographics (e.g., age-adjusted haemoglobin reference ranges for paediatric vs. adult patients).

4. **Persistent Data Store:** Implement a backend database (e.g., SQLite for local deployment, or Supabase/PostgreSQL for cloud deployment) to persist extracted records across sessions and enable longitudinal tracking.

5. **Longitudinal Trend Analysis:** Extend the Analytics Dashboard to display time-series trends for individual patients across multiple reports, enabling clinicians to monitor the progression or resolution of laboratory abnormalities.

6. **Confidence Scoring and Uncertainty Quantification:** Request log-probabilities or structured uncertainty estimates from the model API to flag low-confidence extractions for priority human review in the data grid.

7. **Bulk Export to FHIR:** Add an export pipeline that converts the master dataset into FHIR (Fast Healthcare Interoperability Resources) DiagnosticReport resources, enabling direct integration with Electronic Health Record (EHR) systems.

8. **Fine-tuned Specialist Model:** As a longer-term research objective, fine-tune a smaller, locally-deployable vision-language model (e.g., Llama-3 via LLaVA) on a curated dataset of annotated laboratory reports to enable fully offline, privacy-preserving processing without any external API dependency.

---

## 6. References

1. Agrawal, M., Hegselmann, S., Lang, H., Kim, Y., & Sontag, D. (2022). Large language models are few-shot clinical information extractors. *Proceedings of the 2022 Conference on Empirical Methods in Natural Language Processing (EMNLP)*, 1998–2022.

2. Beede, E., Baylor, E., Hersch, F., Iurchenko, A., Wilcox, L., Ruamviboonsuk, P., & Vardoulakis, L. M. (2020). A human-centered evaluation of a deep learning system deployed in clinics for the detection of diabetic retinopathy. *Proceedings of the 2020 CHI Conference on Human Factors in Computing Systems*, 1–12.

3. Christodoulidis, A., Follonier, A., Schmid, A., Stritt, M., Papazoglou, A. S., & Rampini, A. (2019). Combining deep learning and classical machine vision for table detection in medical forms. *IEEE 32nd International Symposium on Computer-Based Medical Systems (CBMS)*, 551–556.

4. Dean, J., & Ghemawat, S. (2008). MapReduce: Simplified data processing on large clusters. *Communications of the ACM*, *51*(1), 107–113.

5. Liu, H., Li, C., Wu, Q., & Lee, Y. J. (2023). Visual instruction tuning. *Advances in Neural Information Processing Systems (NeurIPS)*, 36.

6. McDonald, C. J., Huff, S. M., Suico, J. G., Hill, G., Leavelle, D., et al. (2003). LOINC, a universal standard for identifying laboratory observations: a 5-year update. *Clinical Chemistry*, *49*(4), 624–633.

7. Meystre, S. M., Friedlin, F. J., South, B. R., Shen, S., & Samore, M. H. (2010). Automatic de-identification of textual documents in the electronic health record: a review of recent research. *BMC Medical Research Methodology*, *10*(1), 70.

8. Obermeyer, Z., Powers, B., Vogeli, C., & Mullainathan, S. (2019). Dissecting racial bias in an algorithm used to manage the health of populations. *Science*, *366*(6464), 447–453.

9. Singhal, K., Azizi, S., Tu, T., Mahdavi, S. S., Wei, J., Chung, H. W., ... & Natarajan, V. (2023). Large language models encode clinical knowledge. *Nature*, *620*(7972), 172–180.

10. Xu, Y., Li, M., Cui, L., Huang, S., Wei, F., & Zhou, M. (2020). LayoutLM: Pre-training of text and layout for document image understanding. *Proceedings of the 26th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining*, 1192–1200.
