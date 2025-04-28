import streamlit as st
from pdf_parser import parse_pdf_resume
from web_scraper import get_job_description
from ats_analyzer import analyze_resume_with_gemini  # Updated import
from embedder import create_embeddings
from chatbot import initialize_chatbot
import logging
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Resume ATS Analyzer", layout="wide")

if "page" not in st.session_state:
    st.session_state.page = "Home"
if "chatbot" not in st.session_state:
    st.session_state.chatbot = None
if "ats_results" not in st.session_state:
    st.session_state.ats_results = None

pages = ["Home", "ATS Analysis", "Chatbot"]
st.session_state.page = st.sidebar.selectbox("Navigate", pages)

if st.session_state.page == "Home":
    st.title("Resume ATS Analyzer")
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
    job_title = st.text_input("Enter Job Title (e.g., Machine Learning Engineer)")
    job_description = st.text_area("Paste Job Description (Optional)")
    
    if st.button("Analyze Resume"):
        if uploaded_file and job_title:
            try:
                os.makedirs("data", exist_ok=True)
                resume_path = "data/temp_resume.pdf"
                with open(resume_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                resume_text, sections = parse_pdf_resume(resume_path)
                if not resume_text:
                    raise ValueError(f"Failed to parse resume: {sections}")
                
                job_desc = get_job_description(job_title, job_description)
                ats_results = analyze_resume_with_gemini(resume_text, job_desc, job_title)  # Updated function
                vectorstore = create_embeddings(resume_text, ats_results)
                chatbot = initialize_chatbot(vectorstore, job_title)
                
                st.session_state.ats_results = ats_results
                st.session_state.chatbot = chatbot
                st.success("Analysis complete! Check ATS Analysis or Chatbot pages.")
            except Exception as e:
                logger.error(f"App error: {str(e)}")
                st.error(f"Error: {str(e)}")
        else:
            st.warning("Please upload a resume and enter a job title.")

elif st.session_state.page == "ATS Analysis":
    st.title("ATS Analysis Results")
    if st.session_state.ats_results:
        results = st.session_state.ats_results
        st.metric("ATS Pass Percentage", f"{results['ats_compatibility_score']}%")
        st.write("**Extracted Skills**: ", ", ".join(results['skills']) or "None")
        st.write("**Extracted Keywords**: ", ", ".join(results['keywords']) or "None")
        st.write("**Trending Skills**: ", ", ".join(results['trending_skills']) or "None")
        st.write("**Trending Keywords**: ", ", ".join(results['trending_keywords']) or "None")
        st.write("**Suggestions for Improvement**:")
        for suggestion in results['suggestions']:
            st.write(f"- {suggestion}")
    else:
        st.info("No analysis available. Please upload a resume on the Home page.")

elif st.session_state.page == "Chatbot":
    st.title("Resume Advisor Chatbot")
    if st.session_state.chatbot:
        query = st.text_input("Ask about your resume or job role (e.g., 'What skills should I add?')")
        if query:
            try:
                response = st.session_state.chatbot(query)
                st.write("**Chatbot Response**:")
                st.write(response)
            except Exception as e:
                logger.error(f"Chatbot error: {str(e)}")
                st.error(f"Chatbot error: {str(e)}")
    else:
        st.info("No chatbot available. Please analyze a resume on the Home page.")