# AI Resume & Cover Letter Assistant

A terminal-based AI assistant that helps job seekers review, tailor, and generate application
materials using an LLM (via the Groq API). Built as a learning project to practice structured
output, prompt engineering, and multi-feature CLI design.

## Features

- 📝 **Resume Review** — general feedback on strengths, weaknesses, and ATS-friendliness
- 🎯 **JD Matching** — compares a resume against a job description and scores the fit
- ✏️ **Resume Tailoring** — rewrites/reframes an existing resume to better align with a job
  description, without inventing new skills or achievements
- 💌 **Cover Letter Generator** — writes a personalized cover letter based on the resume and job
  description
- 🤖 **Unified CLI Router** (`main.py`) — a single menu-driven entry point to run any of the above,
  or all of them together

## Tech Stack

- Python 3.13
- Groq API (Llama 3.3 70B)
- `python-dotenv` for environment variable management
- `requests` for API calls
- `pypdf` / `python-docx` for reading resumes (PDF, DOCX, TXT)
- `python-docx` for generating downloadable `.docx` output files

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Lakshmi2411/ai-resume-cover-letter.git
   cd ai-resume-cover-letter
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv ai-env
   ai-env\Scripts\activate    # Windows
   source ai-env/bin/activate # Mac/Linux
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory and add your Groq API key:
   ```
   GROQ_API_KEY=your_key_here
   ```
   (Get a free key from [console.groq.com](https://console.groq.com))

## Usage

Run the unified assistant:
```bash
python main.py
```

You'll be asked to:
1. Choose a feature (1–5)
2. Provide the path to your resume file (PDF, DOCX, or TXT)
3. Paste a job description if the feature requires one (type `END` on a new line when done)

Individual scripts can also be run standalone:
```bash
python resume_reviewer.py
python jd_matcher.py
python resume_rewriter.py
python cover_letter_generator.py
```

## Example Output

**JD Match:**
```json
{
  "match_score": 8,
  "matching_skills": ["Python", "AWS", "Microservices", "Problem solving"],
  "missing_skills": ["Rust", "Typescript", "Azure or GCP experience"],
  "suggestions": ["Highlight any experience with emerging technologies..."]
}
```

**Tailored resume and cover letter** are saved automatically as `.docx` files, named using the
candidate's name and the company detected from the job description, e.g.:
```
John_Doe_TechCorp_TailoredResume.docx
John_Doe_TechCorp_CoverLetter.docx
```

## How It Works

Each feature follows the same core pattern: combine relevant text inputs (resume, job
description) into a prompt, send it to the LLM with a role-specific system prompt and a few-shot
example, then either parse the structured JSON response (for review/matching) or use the
free-form text response directly (for the rewritten resume/cover letter).

The **resume rewriter** includes explicit guardrail instructions telling the model never to
invent skills, tools, or achievements that aren't in the original resume, only to reframe and
reorder existing content. This is a deliberate anti-hallucination measure, since fabricated
experience on a resume could cause real harm to the candidate.

## What I Learned

- JSON mode / structured output for reliable, parseable LLM responses
- Few-shot prompting to guide output format and tone
- Role prompting to shape the model's persona and behavior
- Output parsing (`json.loads`) and handling malformed responses gracefully
- Guardrail prompting to prevent hallucination in high-stakes rewriting tasks
- Reading and extracting text from PDF, DOCX, and TXT files
- Generating downloadable `.docx` files programmatically with `python-docx`
- Designing a simple menu-based CLI router to tie multiple features together
- Chaining multiple LLM calls for different sub-tasks (e.g. using the LLM itself to extract a
  name/company for filenames)

## Known Limitations

- Company name detection depends on the job description explicitly naming the employer;
  recruiter-posted listings (e.g. via Totaljobs, Indeed) often show the agency's name instead
  of the actual hiring company
- The resume rewriter aims to avoid fabricating skills, but always review the output against
  your original resume before submitting an application
- No persistence, each run is a single, standalone session

## Future Improvements

- [ ] Add a Streamlit web interface
- [ ] LLM-based intent detection instead of a manual menu (true agentic routing)
- [ ] Live job market search (RAG) to recommend trending certifications and tech stacks
- [ ] Support additional file formats and multiple resume versions

## License

MIT