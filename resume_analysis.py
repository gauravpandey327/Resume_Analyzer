import re
import nltk
from pdfminer.high_level import extract_text
from collections import Counter
from io import BytesIO
import os

# Ensure NLTK resources are downloaded
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

# Define key pieces of information expected in a resume with weights
key_info = {
    'email || gmail': (True, 10),
    'phone || mobile': (True, 10),
    'education': (True, 10),
    'experience': (True, 15),
    'internships || internship': (True, 10),
    'skills || skill': (True, 10),
    'certifications || certification || achievements': (True, 10),
    'projects || project': (True, 10),
    'linkedin': (True, 5),
    'github': (True, 10)
}

def extract_text_from_pdf(file_stream):
    """
    Extracts text from a PDF file stream.
    """
    text = extract_text(file_stream)
    return text

def preprocess_text(text):
    """
    Preprocesses text by converting it to lowercase.
    """
    lower_text = text.lower()
    return lower_text

def remove_stopwords(tokens):
    """
    Removes stopwords from a list of tokens.
    """
    stopwords = set(nltk.corpus.stopwords.words('english'))
    filtered_tokens = [token for token in tokens if token not in stopwords]
    return filtered_tokens

def tokenize_text(text):
    """
    Tokenizes text into words.
    """
    tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(text)
    return tokens

def calculate_keyword_score(resume_words, job_description_words):
    """
    Calculates the score based on the occurrence of keywords in both the resume and the job description.
    """
    resume_word_count = Counter(resume_words)
    job_description_word_count = Counter(job_description_words)

    common_words = set(resume_word_count).intersection(set(job_description_word_count))
    score = sum(resume_word_count[word] * job_description_word_count[word] for word in common_words)
    
    matched_keywords = [(word, resume_word_count[word], job_description_word_count[word]) for word in common_words]
    return score, matched_keywords

def check_key_info_presence(preprocessed_text, key_info):
    """
    Checks for the presence of key information in the preprocessed text.
    """
    matched_info = []
    key_info_score = 0
    for key, (is_required, weight) in key_info.items():
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
    """
    resume_text = extract_text_from_pdf(resume_stream)
    job_description_text = extract_text_from_pdf(job_description_stream)

    preprocessed_resume_text = preprocess_text(resume_text)
    preprocessed_job_description_text = preprocess_text(job_description_text)

    resume_tokens = tokenize_text(preprocessed_resume_text)
    job_description_tokens = tokenize_text(preprocessed_job_description_text)

    resume_words = remove_stopwords(resume_tokens)
    job_description_words = remove_stopwords(job_description_tokens)

    key_info_score, matched_key_info = check_key_info_presence(preprocessed_resume_text, key_info)
    score, matched_keywords = calculate_keyword_score(resume_words, job_description_words)

    overall_final_score = score + key_info_score * 0.5
    # print(score)

    return matched_key_info, matched_keywords, overall_final_score, score, key_info_score
