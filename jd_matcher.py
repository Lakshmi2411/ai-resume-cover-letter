import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
URL = "https://api.groq.com/openai/v1/chat/completions"

JD_SYSTEM_PROMPT = """You are an expert technical recruiter. Compare the given resume against the provided job description and evaluate the fit.

You must always respond in valid JSON format with this exact structure:
{
  "match_score": <integer 1-10>,
  "matching_skills": ["skill 1", "skill 2"],
  "missing_skills": ["skill 1", "skill 2"],
  "suggestions": ["specific suggestion 1", "specific suggestion 2"]
}

Do not include any text outside the JSON object."""

FEW_SHOT_EXAMPLE = """Example:
Job Description snippet: "Looking for a backend engineer with 3+ years Python, AWS Lambda, and Docker experience."
Resume snippet: "Built Python scripts for internal tools. Some AWS experience."

Response:
{
  "match_score": 5,
  "matching_skills": ["Python", "AWS"],
  "missing_skills": ["Docker", "Lambda-specific experience", "3+ years demonstrated seniority"],
  "suggestions": ["Highlight any containerization experience even if limited", "Add specific AWS services used, especially Lambda if applicable", "Quantify years of experience clearly"]
}
"""


def match_resume_to_jd(resume_text, jd_text, temperature=0.3):
    user_prompt = (
        f"{FEW_SHOT_EXAMPLE}\n\nJob Description:\n{jd_text}\n\nResume:\n{resume_text}"
    )

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": JD_SYSTEM_PROMPT},
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
        print("Warning: Model did not return valid JSON")
        return {"raw_response": reply}


if __name__ == "__main__":
    from file_reader import extract_text

    resume_text = extract_text("sample_resumes\\sample_resume.txt")

    print("Paste the job description below.")
    print(
        "When done, press Enter, then type END on a new line and press Enter again:\n"
    )

    jd_lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        jd_lines.append(line)

    jd_text = "\n".join(jd_lines)

    result = match_resume_to_jd(resume_text, jd_text)
    print("\n--- Match Results ---")
    print(json.dumps(result, indent=2))
