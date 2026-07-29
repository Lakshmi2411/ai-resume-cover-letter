import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """You are an expert technical recruiter with 15 years of experience reviewing resumes for software engineering roles. You give honest, specific, and actionable feedback.

You must always respond in valid JSON format with this exact structure:
{
  "strengths": ["point 1", "point 2"],
  "weaknesses": ["point 1", "point 2"],
  "ats_score": <integer 1-10>,
  "suggestions": ["point 1", "point 2"]
}

Do not include any text outside the JSON object."""

FEW_SHOT_EXAMPLE = """Example:
Resume snippet: "Worked on backend stuff. Did some Python. Helped team with tasks."

Response:
{
  "strengths": ["Has backend and Python experience"],
  "weaknesses": ["Extremely vague language, no metrics, no specific technologies or achievements"],
  "ats_score": 3,
  "suggestions": ["Replace vague phrases with specific achievements, e.g. 'Built REST API in Python/Flask handling 10k requests/day'", "Add quantifiable results wherever possible"]
}
"""


def review_resume(resume_text, temperature=0.3):
    user_prompt = f"{FEW_SHOT_EXAMPLE}\n\nNow review this resume:\n\n{resume_text}"

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "response_format": {"type": "json_object"},
    }

    response = requests.post(URL, headers=headers, json=payload)
    data = response.json()
    reply = data["choices"][0]["message"]["content"]

    try:
        parsed = json.loads(reply)
        return parsed
    except json.JSONDecodeError:
        print("Warning: Model did not return valid JSON")
        return {"raw_response": reply}


if __name__ == "__main__":
    from file_reader import extract_text

    resume_text = extract_text("sample_resumes\\LChakka_CV_Antare.pdf")
    result = review_resume(resume_text)
    print(json.dumps(result, indent=2))
