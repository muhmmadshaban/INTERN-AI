import streamlit as st
import requests
import re
from agent_team import extract_text_from_pdf

# CSS to change the background of the whole page
st.markdown(
    """
    <style>
    body {
        background-color: #e6f0fa;
        color: #333333;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .main > div {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def extract_markdown_from_response(response_str):
    """
    Extracts content="..." portion before content_type=.
    """
    match = re.search(r'content="(.*?)"\scontent_type=', response_str, re.DOTALL)
    if match:
        markdown_text = match.group(1)
        markdown_text = markdown_text.encode('utf-8').decode('unicode_escape')
        return markdown_text
    else:
        return response_str

def extract_markdown_table(markdown_text):
    """
    Extracts the markdown table (lines starting with '|').
    """
    lines = markdown_text.splitlines()
    table_lines = [line for line in lines if line.strip().startswith('|')]
    if len(table_lines) >= 2:
        return "\n".join(table_lines)
    else:
        return "⚠️ No company table found."

API_ENDPOINT = "http://127.0.0.1:8000/chat"

st.title("🤖 AGENT_INTERN")
st.write("Upload your resume and let our AI agents find relevant startups and local companies for internships.")

resume = st.file_uploader("Upload Your Resume", type=["pdf"])

if resume is not None:
    # Step 1: Extract text from uploaded resume
    extracted_text = extract_text_from_pdf(resume)
    st.subheader("📄 Resume Preview")
    st.text(extracted_text)

    # Step 2: Trigger on Send button
    if st.button("Send"):
        if extracted_text.strip():
            with st.spinner("🔍 Analyzing and matching companies..."):
                try:
                    response = requests.post(API_ENDPOINT, json={"message": extracted_text})
                    if response.status_code == 200:
                        data = response.json()
                        raw_response = data.get("response", "")
                        markdown_full = extract_markdown_from_response(raw_response)
                        company_table = extract_markdown_table(markdown_full)

                        st.subheader("🏢 Matched Companies")
                        st.markdown(company_table, unsafe_allow_html=True)
                    elif response.status_code == 500:
                        st.error("Internal server error. Try again later.")
                    else:
                        st.error(f"Error {response.status_code}: {response.text}")
                except Exception as e:
                    st.error(f"❌ Request failed: {e}")
        else:
            st.warning("⚠️ No valid text found in the resume.")
else:
    st.info("📤 Please upload a PDF resume to begin.")
