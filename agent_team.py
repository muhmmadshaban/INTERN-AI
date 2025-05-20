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

def chat(resume_text:str):
    # PATH = "MUHMMAD SHABAN RESUME (1).pdf"
    # resume_pdf_path = PATH
    # resume_text = extract_text_from_pdf(resume_pdf_path)
    print("Extracted Resume Text:")
    print(resume_text[:500])  # Preview for verification

    # Agent to find relevant startups and local companies
    startup_finder = Agent(
        model=Groq(id="llama3-70b-8192"),
        tools=[DuckDuckGo(), GoogleSearch()],
        role="Startup and Local Company Finder",
        show_tool_calls=True,
        markdown=True,
        instructions=[
            "Extract skills and tools from the resume.",
            "Find startups and local (non-MNC) companies working in those areas.",
            "Prioritize those offering internships or hiring interns.",
            "Exclude MNCs or large multinational corporations.",
            "Return table: Company Name, Tech Stack, Website, Location, Internship Info or Careers Page Link.",
        ],
        debug_mode=True
    )

    # Agent to fetch contact info like HR emails or recruiter profiles
    contact_finder = Agent(
        model=Groq(id="llama3-70b-8192"),
        tools=[GoogleSearch()],
        role="HR and Recruiter Contact Finder",
        show_tool_calls=True,
        markdown=True,
        instructions=[
            "Find HR, recruiter, or internship coordinator contacts for given companies.",
            "Include email, LinkedIn profile, or careers page.",
            "Only include contacts from startups or local companies.",
            "Ignore generic company support emails or unrelated contact pages.",
            "Output: Company Name, HR Name (if available), Email, LinkedIn, Source Link.",
        ],
        debug_mode=True
    )

    # Leader agent to coordinate everything
    leader_agent = Agent(
        model=Groq(id="llama3-70b-8192"),
        role="Startup Internship Research Leader",
        show_tool_calls=True,
        markdown=True,
        team=[startup_finder, contact_finder],
        instructions=[
            "1. Extract skills from the resume.",
            "2. Use that to find relevant startups or local companies working in those areas.",
            "3. Ensure the companies are not MNCs, only local or early-stage companies.",
            "4. Find HR/recruiter contacts for each company.",
            "5. Combine everything in a structured table: Company Name, Tech Area, Website, Location, Internship Info, HR Email/LinkedIn, Source.",
        ],
        debug_mode=True
    )

    # Leader agent prompt
    prompt = (
    "Given the following resume, perform the following tasks:\n"
    "1. Extract relevant tools, programming languages, and domains of interest.\n"
    "2. Identify startups and local companies (preferably from the same country mentioned in the resume; avoid MNCs) that are working in the extracted domains and offering internships.\n"
    "3. must Find HR or recruiter contact emails, LinkedIn profiles, or official contact pages for those companies.\n\n"
    f"{resume_text}\n\n"
    "Provide the output in the form of a structured table with the following columns:\n"
    "Company Name | Tech Stack / Area | Website | Location | Internship Info / Careers Page | HR Email / LinkedIn | Source"
)


    # Run the workflow

    print("\n🔍 Startup & Local Internship Opportunities:\n")
    response =  leader_agent.run(prompt)
    return response
    # leader_agent.print_response(prompt)

# chat()
