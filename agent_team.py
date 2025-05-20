import PyPDF2
from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.googlesearch import GoogleSearch
from phi.tools.duckduckgo import DuckDuckGo
from dotenv import load_dotenv
from io import BytesIO

load_dotenv()

def extract_text_from_pdf(pdf_file):
    """
    Extract all text from an uploaded PDF file or a file path.
    If pdf_file is a file-like object (e.g., uploaded file), it reads directly.
    If pdf_file is a file path string, it opens the file path.
    """
    text = ""
    if hasattr(pdf_file, "read"):
        # It's a file-like object (e.g., UploadedFile from Streamlit)
        pdf_bytes = pdf_file.read()
        pdf_stream = BytesIO(pdf_bytes)
        reader = PyPDF2.PdfReader(pdf_stream)
    else:
        # It's a file path string
        with open(pdf_file, "rb") as f:
            reader = PyPDF2.PdfReader(f)
    for page in reader.pages:
        text += page.extract_text() or ""
    return text
def chat(resume_text: str):
    print("Extracted Resume Text:")
    print(resume_text[:500])  # Preview for verification

    # Agent to find startups and local companies
    startup_finder = Agent(
        model=Groq(id="llama3-70b-8192"),
        tools=[DuckDuckGo(), GoogleSearch()],
        role="Startup and Local Company Finder",
        show_tool_calls=True,
        markdown=True,
        instructions=[
            "Extract technical skills, tools, and domains from the resume.",
            "Find startups and local (non-MNC) companies working in those areas.",
            "Only include companies currently active and found via real sources like websites, news, or search results.",
            "Do not list any company unless their official website or legitimate presence is verified via DuckDuckGo or Google.",
            "Exclude MNCs and vague or unverifiable organizations.",
            "Return these verified companies with basic info: Company Name, Tech Area, Website, Location.",
        ],
        debug_mode=True
    )

    # Agent to find real HR/recruiter contacts
    contact_finder = Agent(
        model=Groq(id="llama3-70b-8192"),
        tools=[GoogleSearch()],
        role="HR and Recruiter Contact Finder",
        show_tool_calls=True,
        markdown=True,
        instructions=[
            "For each verified startup or local company, search for HR or recruiter contacts using Google.",
            "Only include contact if you find one of the following from real sources: company HR email, recruiter LinkedIn profile, or official careers/contact page.",
            "Do NOT make up contact names or emails. Use only what is found via real search results.",
            "Ignore generic support emails, sales contacts, or general inquiries.",
            "Return only companies for which valid contact details are found.",
            "Format: Company Name, HR Name (if available), Email, LinkedIn, Source Link.",
        ],
        debug_mode=True
    )

    # Leader agent to coordinate
    leader_agent = Agent(
        model=Groq(id="llama3-70b-8192"),
        role="Verified Startup Internship Finder",
        show_tool_calls=True,
        markdown=True,
        team=[startup_finder, contact_finder],
        instructions=[
            "1. Extract skills/domains from the resume.",
            "2. Use startup_finder to find real startups and local companies in those areas, using real sources (Google, DuckDuckGo).",
            "3. Pass only verified companies to contact_finder.",
            "4. Use contact_finder to find verified HR/recruiter/careers contacts via Google search.",
            "5. Exclude companies if no contact info is found.",
            "6. Return final result as table only for companies with verified contact info.",
            "Table Columns: Company Name | Tech Area | Website | Location | Internship Info / Careers Page | HR Email / LinkedIn | Source",
        ],
        debug_mode=True
    )

    prompt = (
        "Given the resume below, extract technical skills and domains. "
        "Then find only verified startups or local companies (not MNCs) working in those areas. "
        "Use real-time data via DuckDuckGo or Google to ensure authenticity. "
        "Find only companies that have verifiable HR contacts or careers page — no assumptions or guesses allowed.\n\n"
        f"{resume_text}\n\n"
        "Return only companies with contact details. Format:\n"
        "Company Name | Tech Stack / Area | Website | Location | Internship Info / Careers Page | HR Email / LinkedIn | Source"
    )

    print("\n🔍 Fetching Verified Internship Opportunities...\n")
    response = leader_agent.run(prompt)
    return response
