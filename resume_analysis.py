# resume_analysis.py

import re  # Importing regular expression module for pattern matching
import nltk  # Importing Natural Language Toolkit for text processing
from PyPDF2 import PdfReader  # Importing PdfReader for PDF text extraction
import docx2txt  # Importing docx2txt for DOCX text extraction
from collections import Counter  # Importing Counter for counting occurrences of words
from pdfminer.high_level import extract_text  # Importing extract_text for PDF text extraction
import fitz  # Importing fitz for PDF text extraction

# Ensure NLTK resources are downloaded
nltk.download('punkt', quiet=True)  # Downloading tokenizer models
nltk.download('stopwords', quiet=True)  # Downloading stopwords corpus

# Define custom stopwords: digits and alphabets
custom_stopwords = [str(i) for i in range(10)]  # Creating a list of digits from 0 to 9
custom_stopwords.extend([chr(ord('a') + i) for i in range(26)])  # Adding lowercase alphabets from 'a' to 'z'

# Define key pieces of information expected in a resume with weights and regex patterns for each
key_info = {
    'email || gmail': (True, 10, r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),  # Email regex pattern
    'phone || mobile': (True, 10, r'\+?[1-9]\d{1,14}'),  # Phone number regex pattern
    'education': (True, 10, ''),  # Placeholder for education regex pattern
    'experience': (True, 15, ''),  # Placeholder for experience regex pattern
    'internships || internship': (True, 10, ''),  # Placeholder for internship regex pattern
    'skills || skill': (True, 10, ''),  # Placeholder for skills regex pattern
    'certifications || certification || achievements': (True, 10, ''),  # Placeholder for certifications regex pattern
    'projects || project': (True, 10, ''),  # Placeholder for projects regex pattern
    'linkedin': (True, 5, r'\blinkedin\.com/[a-zA-Z0-9]+\b'),  # LinkedIn profile regex pattern
    'github': (True, 10, r'\bgithub\.com/[a-zA-Z0-9]+\b')  # GitHub profile regex pattern
}

def extract_text_from_file(file):
    """
    Extracts text from a file (PDF or DOCX).
    
    Args:
        file: File object representing the uploaded file.
        
    Returns:
        str: Extracted text from the file.
    """
    if file.type == "application/pdf":  # Check if the file is a PDF
        try:
            # Read the content of the file stream
            file.seek(0)
            pdf_content = file.read()
            
            # Open the PDF document using PyMuPDF
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            
            # Extract text from each page
            text = ""
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                text += page.get_text()
            
            return text
        except Exception as e:
            print(f"Error extracting text from PDF file: {e}")
            return None
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":  # Check if the file is a DOCX
        try:
            text = docx2txt.process(file)  # Extract text using docx2txt
            return text
        except Exception as e:
            print(f"Error extracting text from DOCX file: {e}")
            return None
    else:
        print("Unsupported file format. Please upload PDF or DOCX files.")
        return None

def preprocess_text(text):
    """
    Preprocesses text by converting it to lowercase.
    
    Args:
        text: Input text to be preprocessed.
        
    Returns:
        str: Preprocessed text in lowercase.
    """
    lower_text = text.lower()
    return lower_text

def remove_stopwords(tokens):
    """
    Removes stopwords from a list of tokens.
    
    Args:
        tokens: List of tokens.
        
    Returns:
        list: Tokens with stopwords removed.
    """
    stopwords = set(nltk.corpus.stopwords.words('english'))
    filtered_tokens = [token for token in tokens if token not in stopwords and token not in custom_stopwords]
    return filtered_tokens

def tokenize_text(text):
    """
    Tokenizes text into words.
    
    Args:
        text: Input text to be tokenized.
        
    Returns:
        list: List of tokens.
    """
    tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(text)
    return tokens

def calculate_keyword_score(resume_words, job_description_words):
    """
    Calculates the score based on the occurrence of keywords in both the resume and the job description.
    
    Args:
        resume_words: List of words in the resume.
        job_description_words: List of words in the job description.
        
    Returns:
        tuple: Score and matched keywords.
    """
    resume_word_count = Counter(resume_words)
    job_description_word_count = Counter(job_description_words)

    common_words = set(resume_word_count).intersection(set(job_description_word_count))
    score = sum(resume_word_count[word] * job_description_word_count[word] for word in common_words)
    
    matched_keywords = [(word, resume_word_count[word], job_description_word_count[word]) for word in common_words]
    return score, matched_keywords

def check_key_info_presence(preprocessed_text, key_info):
    """
    Checks for the presence of key information in the preprocessed text using regex patterns.
    
    Args:
        preprocessed_text: Preprocessed text.
        key_info: Dictionary containing key information patterns.
        
    Returns:
        tuple: Key information score and matched information.
    """
    matched_info = []
    key_info_score = 0
    for key, (is_required, weight, regex_pattern) in key_info.items():
        if regex_pattern:  # If a regex pattern is provided, use it for matching
            present = bool(re.search(regex_pattern, preprocessed_text))
        else:  # If no regex pattern is provided, check for substrings
            keyword_alternatives = key.split(" || ")
            present = any(alt.lower() in preprocessed_text for alt in keyword_alternatives)
        if present:
            key_info_score += weight
            matched_info.append([key, "Yes", weight])
        else:
            matched_info.append([key, "No", weight])
    return key_info_score, matched_info

def analyze_resume_and_job_description(resume_stream, job_description_stream):
    """
    Analyzes the resume and job description, returning the matched key information, job description keywords, and scores.
    
    Args:
        resume_stream: File object representing the resume file.
        job_description_stream: File object representing the job description file.
        
    Returns:
        tuple: Matched key information, matched keywords, overall score, resume score, key information score.
    """
    resume_text = extract_text_from_file(resume_stream)  # Extract text from resume
    job_description_text = extract_text_from_file(job_description_stream)  # Extract text from job description

    preprocessed_resume_text = preprocess_text(resume_text)  # Preprocess resume text
    preprocessed_job_description_text = preprocess_text(job_description_text)  # Preprocess job description text

    resume_tokens = tokenize_text(preprocessed_resume_text)  # Tokenize resume text
    job_description_tokens = tokenize_text(preprocessed_job_description_text)  # Tokenize job description text

    resume_words = remove_stopwords(resume_tokens)  # Remove stopwords from resume tokens
    job_description_words = remove_stopwords(job_description_tokens)  # Remove stopwords from job description tokens

    key_info_score, matched_key_info = check_key_info_presence(preprocessed_resume_text, key_info)  # Check key information presence
    score, matched_keywords = calculate_keyword_score(resume_words, job_description_words)  # Calculate keyword score

    overall_final_score = score + key_info_score * 0.5  # Calculate overall final score

    return matched_key_info, matched_keywords, overall_final_score, score, key_info_score
