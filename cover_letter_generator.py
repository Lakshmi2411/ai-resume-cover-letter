import os
import requests
from dotenv import load_dotenv
from docx import Document

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """You are an expert career coach and professional writer who specializes in 
writing compelling, personalized cover letters. Write in a confident, professional, yet warm 
tone. Avoid generic phrases like "I am writing to express my interest." Make the letter specific 
to the candidate's actual experience and the job description provided. Keep it to 3-4 paragraphs."""

FEW_SHOT_EXAMPLE = """Example:
Job Description snippet: "Looking for a backend engineer with Python and AWS experience to build 
scalable microservices."
Resume snippet: "3 years building Python microservices on AWS Lambda, reduced latency by 25%."

Cover Letter:
Dear Hiring Manager,

When I reduced API latency by 25% at my current role by rethinking how our microservices handled 
caching, I learned that the best engineering solutions often come from questioning assumptions 
rather than adding complexity. That instinct is exactly what draws me to this backend engineering 
role.

Over the past three years, I've built and maintained Python microservices on AWS Lambda, 
handling tens of thousands of daily requests. I'm comfortable owning systems end to end, from 
architecture decisions to the CloudWatch dashboards that tell me something's wrong at 2am.

I'd welcome the chance to bring that same ownership mentality to your team's infrastructure 
challenges.

Sincerely,
[Candidate Name]
"""


def generate_cover_letter(resume_text, jd_text, temperature=0.7):
    user_prompt = (
        f"{FEW_SHOT_EXAMPLE}\n\nNow write a cover letter for this candidate:\n\n"
        f"Job Description:\n{jd_text}\n\nResume:\n{resume_text}"
    )

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        # Note: no response_format/json mode here, we WANT free-form prose
    }

    response = requests.post(URL, headers=headers, json=payload)
    data = response.json()
    return data["choices"][0]["message"]["content"]


import json


def extract_name_and_company(resume_text, jd_text, temperature=0.1):
    """Uses the LLM to pull the candidate's name from the resume and the
    company name from the job description, returned as JSON."""

    system_prompt = """Extract the candidate's full name from the resume text, and the 
company name from the job description text. Respond only in valid JSON with this structure:
{
  "candidate_name": "...",
  "company_name": "..."
}
If either cannot be found, use "Unknown" as the value."""

    user_prompt = f"Resume:\n{resume_text}\n\nJob Description:\n{jd_text}"

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "response_format": {"type": "json_object"},
    }

    response = requests.post(URL, headers=headers, json=payload)
    data = response.json()
    reply = data["choices"][0]["message"]["content"]

    try:
        return json.loads(reply)
    except json.JSONDecodeError:
        return {"candidate_name": "Unknown", "company_name": "Unknown"}


def make_filename(person_name, company_name):
    # Clean up spaces and special characters so it's a safe filename
    safe_person = "_".join(person_name.strip().split())
    safe_company = "_".join(company_name.strip().split())
    return f"{safe_person}_{safe_company}_CoverLetter.docx"


def save_as_docx(letter_text, filename):
    doc = Document()
    for paragraph in letter_text.split("\n\n"):
        if paragraph.strip():
            doc.add_paragraph(paragraph.strip())
    doc.save(filename)
    print(f"\nSaved cover letter to {filename}")


if __name__ == "__main__":
    from file_reader import extract_text

    resume_path = input("Enter path to your resume file (pdf/docx/txt): ")
    resume_text = extract_text(resume_path)

    print("\nPaste the job description below. Type END on a new line when done:\n")
    jd_lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        jd_lines.append(line)
    jd_text = "\n".join(jd_lines)

    letter = generate_cover_letter(resume_text, jd_text)

    print("\n--- Generated Cover Letter ---\n")
    print(letter)

    extracted = extract_name_and_company(resume_text, jd_text)
    print(f"\nDetected candidate: {extracted['candidate_name']}")
    print(f"Detected company: {extracted['company_name']}")

    filename = make_filename(extracted["candidate_name"], extracted["company_name"])
    save_as_docx(letter, filename)
