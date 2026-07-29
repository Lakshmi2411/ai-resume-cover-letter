import os
import requests
from dotenv import load_dotenv
from docx import Document
from cover_letter_generator import extract_name_and_company, make_filename

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """You are an expert resume writer. Your job is to rewrite and reframe the 
candidate's EXISTING resume content to better align with the given job description.

STRICT RULES:
- Only rephrase, reorder, or emphasize experience that already exists in the resume.
- NEVER invent new skills, tools, technologies, achievements, or metrics the candidate did not 
  mention.
- You may rephrase vague statements into more specific, achievement-oriented language, but only 
  using information already present or reasonably implied in the original resume.
- Reorder or emphasize sections that are most relevant to the job description.
- Keep the same overall resume format (summary, skills, experience, education).

Return the full rewritten resume as plain text, formatted clearly with section headers."""

FEW_SHOT_EXAMPLE = """Example:
Job Description snippet: "Looking for a backend engineer with strong AWS and API experience."
Original resume snippet: "Worked on backend stuff. Did some Python. Helped team with tasks."

Rewritten snippet:
"Backend Software Engineer with hands-on Python experience, contributing to team projects 
involving API development and collaborative problem-solving."

(Note: no AWS was added here since the original resume didn't mention it, only existing 
content was reframed.)
"""


def rewrite_resume(resume_text, jd_text, temperature=0.4):
    user_prompt = (
        f"{FEW_SHOT_EXAMPLE}\n\nJob Description:\n{jd_text}\n\n"
        f"Original Resume:\n{resume_text}\n\n"
        f"Now rewrite this resume to better align with the job description, "
        f"following the strict rules above."
    )

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
    }

    response = requests.post(URL, headers=headers, json=payload)
    data = response.json()
    return data["choices"][0]["message"]["content"]


def save_resume_as_docx(resume_text, filename):
    doc = Document()
    for line in resume_text.split("\n"):
        if line.strip():
            doc.add_paragraph(line.strip())
    doc.save(filename)
    print(f"\nSaved tailored resume to {filename}")


def make_resume_filename(person_name, company_name):
    safe_person = "_".join(person_name.strip().split())
    safe_company = "_".join(company_name.strip().split())
    return f"{safe_person}_{safe_company}_TailoredResume.docx"


if __name__ == "__main__":
    from file_reader import extract_text

    resume_path = input("Enter path to your resume file (pdf/docx/txt): ")
    resume_text = extract_text(resume_path)

    print("Paste the job description below. Type END on a new line when done:\n")
    jd_lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        jd_lines.append(line)
    jd_text = "\n".join(jd_lines)

    updated_resume = rewrite_resume(resume_text, jd_text)
    print("\n--- Tailored Resume ---\n")
    print(updated_resume)

    extracted = extract_name_and_company(resume_text, jd_text)
    filename = make_resume_filename(
        extracted["candidate_name"], extracted["company_name"]
    )
    save_resume_as_docx(updated_resume, filename)
