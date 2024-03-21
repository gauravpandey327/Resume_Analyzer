# web.py

import streamlit as st  # Importing Streamlit library for web app development
from resume_analysis import analyze_resume_and_job_description  # Importing resume analysis function
from tabulate import tabulate  # Importing tabulate for creating tables

# Setting the title of the web app
st.title("Resume Analysis Tool")

# Displaying introductory text
st.markdown("""
Welcome to the Resume Analysis Tool. This application helps you understand how well various resumes align with a specific job description. 
Follow the steps below to get started.
""")

# Input for number of job vacancies
job_vacancies = st.number_input("Enter the number of job vacancies:", min_value=1, value=1)

# Expander to collapse/expand the file upload section
with st.expander("Step 1: Upload Your Files"):
    # Instructions for file upload
    st.markdown("""
    Please upload the job description and the resumes. Both the job description and the resumes can be in either PDF or DOCX format.
    """)
    # File uploader for job description
    job_description_file = st.file_uploader("Upload job description (PDF or DOCX):", type=['pdf', 'docx'], key='job_description', accept_multiple_files=False)
    # File uploader for resumes
    resume_files = st.file_uploader("Upload resumes (PDF or DOCX):", type=['pdf', 'docx'], key='resumes', accept_multiple_files=True)

if job_description_file is not None and resume_files is not None and len(resume_files) > 0:
    # Indicating analysis process
    st.markdown("Step 2: Analyzing Your Files...")
    results = []

    for resume_file in resume_files:
        # Showing loading spinner while analyzing each resume
        with st.spinner(text=f"Analyzing {resume_file.name}..."):
            # Analyzing each resume
            matched_key_info, matched_common_words, overall_score, score, key_info_score = analyze_resume_and_job_description(resume_file, job_description_file)

            results.append({
                "Filename": resume_file.name,
                "Details": {
                    "Key Info": matched_key_info,
                    "Common Words": matched_common_words,
                    "Scores": {
                        "Key Info Score": key_info_score,
                        "Job Description Score": score,
                        "Overall Score": overall_score
                    }
                }
            })

    # Sort the resumes based on overall score
    results.sort(key=lambda x: x["Details"]["Scores"]["Overall Score"], reverse=True)

    # Display the top matching resumes based on the number of job vacancies
    st.subheader(f"Top {job_vacancies} Resumes Matching the Job Description")

    for result in results[:job_vacancies]:
        st.markdown(f"""
        <div style="border-radius:10px; border: 1px solid #ccc; padding: 10px; margin-bottom: 10px;">
            <h4>{result["Filename"]}</h4>
            <p><b>Overall Score:</b> {result["Details"]["Scores"]["Overall Score"]}</p>
            <p><b>Key Info Score:</b> {result["Details"]["Scores"]["Key Info Score"]}</p>
            <p><b>Job Description Score:</b> {result["Details"]["Scores"]["Job Description Score"]}</p>
        """, unsafe_allow_html=True)
        
        with st.expander("More Details"):
            key_info_table_data = []
            for keyword, status, _ in result["Details"]["Key Info"]:
                keywords = keyword.split(" || ")
                formatted_keywords = ", ".join(keywords)
                key_info_table_data.append([formatted_keywords, 'Present' if status=="Yes" else 'Not Present'])

            key_info_table = tabulate(key_info_table_data, headers=['Keyword', 'Status'], tablefmt="pipe", numalign="left")
            st.markdown(key_info_table, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)  # Space between tables
            
            common_words_table = tabulate(result["Details"]["Common Words"], headers=['Keyword', 'Occurrences in Resume', 'Occurrences in Job Description'], tablefmt="pipe", numalign="left")
            st.markdown(common_words_table, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)  # Close the div

    # Display scores for every resume
    st.subheader("Scores for Every Resume Matching the Job Description")
    for result in results:
        st.markdown(f"""
        <div style="border-radius:10px; border: 1px solid #ccc; padding: 10px; margin-bottom: 10px;">
            <h4>{result["Filename"]}</h4>
            <p><b>Overall Score:</b> {result["Details"]["Scores"]["Overall Score"]}</p>
            <p><b>Key Info Score:</b> {result["Details"]["Scores"]["Key Info Score"]}</p>
            <p><b>Job Description Score:</b> {result["Details"]["Scores"]["Job Description Score"]}</p>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("More Details"):
            key_info_table_data = []
            for keyword, status, _ in result["Details"]["Key Info"]:
                keywords = keyword.split(" || ")
                formatted_keywords = ", ".join(keywords)
                key_info_table_data.append([formatted_keywords, 'Present' if status=="Yes" else 'Not Present'])

            key_info_table = tabulate(key_info_table_data, headers=['Keyword', 'Status'], tablefmt="pipe", numalign="left")
            st.markdown(key_info_table, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)  # Space between tables
            
            common_words_table = tabulate(result["Details"]["Common Words"], headers=['Keyword', 'Occurrences in Resume', 'Occurrences in Job Description'], tablefmt="pipe", numalign="left")
            st.markdown(common_words_table, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)  # Close the div
else:
    # Warning message if no files are uploaded
    st.warning("Please upload the job description and at least one resume to proceed with the analysis.")
