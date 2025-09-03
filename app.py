import streamlit as st
from pdf_parser import parse_pdf_resume
from web_scraper import get_job_description
from ats_analyzer import analyze_resume_with_gemini
from embedder import create_embeddings
from chatbot import initialize_chatbot
from util import setup_logging
import os

# Configure logging
logger = setup_logging()

# Set page configuration
st.set_page_config(page_title="CareerZync-ATS", layout="wide", initial_sidebar_state="expanded")

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "chatbot" not in st.session_state:
    st.session_state.chatbot = None
if "ats_results" not in st.session_state:
    st.session_state.ats_results = None
if "user_assumed_ats_percentage" not in st.session_state:
    st.session_state.user_assumed_ats_percentage = 75.0
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar navigation
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>CareerZync</h2>", unsafe_allow_html=True)
    pages = ["Home", "ATS Analysis", "Chatbot"]
    st.session_state.page = st.selectbox("Navigate", pages, key="nav_selectbox")
    st.markdown("---")
    st.markdown("**About**")
    st.write("CareerZync-ATS optimizes your resume for ATS systems and provides personalized advice.")
    st.markdown("**Version**: 1.0.0")

# Page: Home
if st.session_state.page == "Home":
    st.markdown("<div class='card'><h1>CareerZync-ATS: Smart Resume Optimizer</h1></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf", help="Upload a PDF resume to analyze.")
            job_title = st.text_input("Enter Job Title", placeholder="e.g., Machine Learning Engineer")
            job_description = st.text_area("Paste Job Description (Optional)", height=150, placeholder="Paste the job description here...")
            st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### Analysis Settings")
            st.session_state.user_assumed_ats_percentage = st.slider(
                "Your Assumed ATS Pass Percentage", 
                0.0, 100.0, st.session_state.user_assumed_ats_percentage, 5.0,
                help="Set the percentage you think your resume will score for ATS compatibility."
            )
            st.markdown("Enter your assumption of how well your resume will pass ATS screening. Compare it with the actual results on the ATS Analysis page.")
            if st.button("Analyze Resume", key="analyze_btn"):
                if uploaded_file and job_title:
                    with st.spinner("Analyzing your resume..."):
                        try:
                            os.makedirs("data", exist_ok=True)
                            resume_path = "data/temp_resume.pdf"
                            # Clear previous resume file
                            if os.path.exists(resume_path):
                                os.remove(resume_path)
                            # Clear previous analysis results
                            st.session_state.ats_results = None
                            st.session_state.chatbot = None
                            st.session_state.chat_history = []
                            
                            with open(resume_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            
                            resume_text, sections = parse_pdf_resume(resume_path)
                            if not resume_text:
                                raise ValueError(f"Failed to parse resume: {sections}")
                            
                            job_desc = get_job_description(job_title, job_description)
                            ats_results = analyze_resume_with_gemini(resume_text, job_desc, job_title)
                            vectorstore = create_embeddings(resume_text, ats_results)
                            chatbot = initialize_chatbot(vectorstore, job_title)
                            
                            st.session_state.ats_results = ats_results
                            st.session_state.chatbot = chatbot
                            st.success("Analysis complete! Navigate to ATS Analysis or Chatbot pages.")
                        except Exception as e:
                            logger.error(f"App error: {str(e)}")
                            st.error(f"Error: {str(e)}")
                else:
                    st.warning("Please upload a resume and enter a job title.")
            st.markdown("</div>", unsafe_allow_html=True)

# Page: ATS Analysis
elif st.session_state.page == "ATS Analysis":
    st.markdown("<div class='card'><h1>ATS Analysis Results</h1></div>", unsafe_allow_html=True)
    
    if st.session_state.ats_results:
        results = st.session_state.ats_results
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.metric("Actual ATS Pass Percentage", f"{results['ats_compatibility_score']}%")
            st.progress(results['ats_compatibility_score'] / 100)
            user_assumption = st.session_state.user_assumed_ats_percentage
            difference = results['ats_compatibility_score'] - user_assumption
            st.metric(
                "Difference from Your Assumption", 
                f"{difference:+.1f}%",
                delta_color="normal"
            )
            st.markdown(f"You assumed your resume would score {user_assumption:.1f}% for ATS compatibility. "
                        f"The actual score is {results['ats_compatibility_score']:.1f}%, "
                        f"which is {difference:+.1f}% {'higher' if difference >= 0 else 'lower'} than your assumption.")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### Skills Overview")
            st.write("**Extracted Skills**: ", ", ".join(results['skills']) or "None")
            st.write("**Trending Skills**: ", ", ".join(results['trending_skills']) or "None")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with st.expander("Keywords Analysis", expanded=True):
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.write("**Extracted Keywords**: ", ", ".join(results['keywords']) or "None")
            st.write("**Trending Keywords**: ", ", ".join(results['trending_keywords']) or "None")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with st.expander("Suggestions for Improvement"):
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            for suggestion in results['suggestions']:
                st.markdown(f"- {suggestion}")
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No analysis available. Please upload a resume on the Home page.")

# Page: Chatbot
elif st.session_state.page == "Chatbot":
    st.markdown("<div class='card'><h1>Resume Advisor Chatbot</h1></div>", unsafe_allow_html=True)
    
    if st.session_state.chatbot:
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            query = st.text_input("Ask about your resume or job role", placeholder="e.g., What skills should I add?")
            if query:
                with st.spinner("Generating response..."):
                    try:
                        response = st.session_state.chatbot(query)
                        st.session_state.chat_history.append({"query": query, "response": response})
                        st.markdown("**Chatbot Response**:")
                        st.markdown(response, unsafe_allow_html=True)
                    except Exception as e:
                        logger.error(f"Chatbot error: {str(e)}")
                        st.error(f"Chatbot error: {str(e)}")
            st.markdown("</div>", unsafe_allow_html=True)
            
            with st.expander("Chat History", expanded=True):
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                if st.session_state.chat_history:
                    for i, chat in enumerate(st.session_state.chat_history):
                        st.markdown(f"**Q{i+1}:** {chat['query']}")
                        st.markdown(f"**A{i+1}:** {chat['response']}")
                        st.markdown("---")
                else:
                    st.write("No chat history available yet.")
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No chatbot available. Please analyze a resume on the Home page.")