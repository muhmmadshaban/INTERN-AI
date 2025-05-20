import streamlit as st
import requests
import re
from agent_team import extract_text_from_pdf

# CSS to change the background of the whole page
st.markdown(
    """
    <style>
    /* Set full page background */
    body {
        background-color: #e6f0fa;  /* a soft, calm light blue */
        color: #333333;             /* dark gray text for good readability */
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .main > div {
        background-color: #ffffff;  /* crisp white content background */
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); /* subtle shadow for depth */
    }
    </style>
    """,
    unsafe_allow_html=True,
)
def extract_markdown_from_response(response_str):
    # Extract text inside content="..." before content_type=
    match = re.search(r'content="(.*?)"\scontent_type=', response_str, re.DOTALL)
    if match:
        markdown_text = match.group(1)
        # Unescape newlines and other escaped characters
        markdown_text = markdown_text.encode('utf-8').decode('unicode_escape')
        return markdown_text
    else:
        # fallback: if pattern not matched, return raw response_str
        return response_str
    


API_ENDPOINT = "http://127.0.0.1:8000/chat"  # Ensure this matches your FastAPI endpoint

st.title("🤖 AGENT_INTERN")
st.write(
    "Upload your resume and let our AI agents find relevant startups and local companies for internships. ")
resume = st.file_uploader("Upload Your Resume", type=["pdf"])  # Restrict to PDF files

if resume is not None:
    # Extract text from the uploaded PDF resume
    text = extract_text_from_pdf(resume)
    message = text  # Use the extracted text as the message
    st.write(message)
    if st.button("Send"):
        if message:
            with st.spinner("Waiting for response..."):
                try:
                    response = requests.post(API_ENDPOINT, json={"message": message})
                    if response.status_code == 200:
                        data = response.json()
                        raw_response = data.get("")  # Adjusted to match your API response key
                        markdown_content = extract_markdown_from_response(raw_response)

                        # Show the cleaned markdown content
                        st.markdown(markdown_content, unsafe_allow_html=True)

                    else:
                        st.error(f"Error {response.status_code}: {response.text}")
                except Exception as e:
                    st.error(f"Request failed: {e}")
        else:
            st.warning("No text extracted from the resume.")
else:
    st.warning("Please upload a resume to proceed.")

def extract_markdown_from_response(response_str):
    # Extract text inside content="..." before content_type=
    match = re.search(r'content="(.*?)"\scontent_type=', response_str, re.DOTALL)
    if match:
        markdown_text = match.group(1)
        # Unescape newlines and other escaped characters
        markdown_text = markdown_text.encode('utf-8').decode('unicode_escape')
        return markdown_text
    else:
        # fallback: if pattern not matched, return raw response_str
        return response_str
