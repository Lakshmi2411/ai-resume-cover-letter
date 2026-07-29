# Project Notes: AI Resume & Cover Letter Assistant

## 1. Project Overview

A terminal-based Python application with four AI-powered features, all built on the same core
pattern: take user text input(s), send them to an LLM (Groq API) with a carefully engineered
prompt, and return either structured (JSON) or free-form (prose) output.

**Files and their roles:**

| File | Purpose | Output type |
|---|---|---|
| `file_reader.py` | Extracts text from PDF/DOCX/TXT resumes | plain text |
| `resume_reviewer.py` | General resume feedback | JSON |
| `jd_matcher.py` | Compares resume vs job description | JSON |
| `resume_rewriter.py` | Tailors resume to a job description | plain text + .docx |
| `cover_letter_generator.py` | Writes a personalized cover letter | plain text + .docx |
| `main.py` | Menu-driven router tying everything together | — |

**The overall flow for any feature:**
```
File → extract_text() → prompt built (system + few-shot + user data) → API call → response
       → (parse JSON) OR (save as .docx)
```

---

## 2. Key Concepts (Keywords) Explained

### System Prompt / Role Prompting
The instruction given once, before the conversation, that tells the model **who it is** and
**how to behave**. E.g. *"You are an expert technical recruiter..."* This shapes tone, expertise
level, and constraints for everything that follows. It's the foundation every other technique
builds on.

### Few-Shot Prompting
Instead of only *describing* the desired output, you *show* the model a complete example
(input → ideal output) directly inside the prompt. The model pattern-matches against the
example rather than guessing the format purely from instructions. We used this in every feature,
each had one worked example baked into the prompt.

### JSON Mode / Structured Output
A request setting (`response_format: {"type": "json_object"}`) that forces the API to return
**only** valid JSON, no extra commentary, no markdown fences. This is essential when you plan to
programmatically use the output (index into fields, loop over lists), rather than just display
raw text.

### Output Parsing
Once you get a JSON *string* back from the API, it's still just text to Python. `json.loads()`
converts that string into an actual Python dictionary you can work with:
```python
parsed = json.loads(reply)   # reply was a string, parsed is now a dict
parsed["match_score"]         # now usable like normal Python data
```
Always wrapped in `try/except` because even JSON mode can occasionally fail to produce valid JSON.

### Temperature
A parameter (0 to ~1+) controlling **randomness/creativity** in the model's word choices.
- Low (0.1–0.3): consistent, focused, deterministic — used for resume review, JD matching,
  and name/company extraction (tasks needing reliability, not creativity)
- Higher (0.4–0.7): more natural, varied phrasing — used for resume rewriting and cover letters
  (tasks needing to read like genuine human writing)

### Guardrail Prompting
Explicitly telling the model what it must **NOT** do, not just what it should do. Used in
`resume_rewriter.py`:
> *"NEVER invent new skills, tools, technologies, achievements, or metrics the candidate did not
> mention."*

This is critical whenever fabrication would cause real harm, e.g. a hallucinated skill on a
resume the candidate would then be quizzed on in an interview. It's a direct, practical defense
against hallucination.

### Tool/Function Reuse Across Files (Chaining LLM Calls)
`extract_name_and_company()` (defined in `cover_letter_generator.py`) is imported and reused in
`resume_rewriter.py` and `main.py`. This is the same idea behind **agentic tool use**, breaking a
larger task into smaller, reusable sub-tasks, each potentially its own LLM call or function.

### Router / Menu-Based Dispatch
`main.py` asks the user what they want, then calls the matching function. This is a simplified,
manual version of what an **agentic system** would do automatically by reasoning about intent
rather than a fixed menu, a good stepping stone before building true intent-based routing.

---

## 3. Important Syntax Explained

### Environment variables and `.env`
```python
from dotenv import load_dotenv
load_dotenv()                      # reads .env file into environment
API_KEY = os.getenv("GROQ_API_KEY") # safely retrieves the key without hardcoding it
```
Keeps secrets out of your code and out of Git history (`.env` is in `.gitignore`).

### f-strings for building prompts
```python
user_prompt = f"Job Description:\n{jd_text}\n\nResume:\n{resume_text}"
```
`f"..."` lets you embed variables directly inside a string using `{}`. `\n` inserts a line break.
This is how all your prompts get dynamically assembled from multiple pieces of text.

### Making the API call
```python
response = requests.post(URL, headers=headers, json=payload)
data = response.json()
```
- `requests.post()` sends an HTTP POST request (the standard way to send data to an API)
- `headers` carries authentication (`Authorization: Bearer <key>`) and content type
- `json=payload` automatically converts your Python dict into a JSON request body
- `.json()` converts the API's JSON response back into a Python dict

### Digging into the response
```python
reply = data["choices"][0]["message"]["content"]
```
This is just navigating a nested dictionary/list structure returned by the API:
`data` → `"choices"` (a list of possible responses) → `[0]` (the first one) → `"message"` (dict)
→ `"content"` (the actual text). Every API call in this project follows this same extraction
pattern.

### Reading files based on extension
```python
if file_path.endswith(".pdf"):
    ...
elif file_path.endswith(".docx"):
    ...
```
`.endswith()` checks the tail of a string, used to detect file type from its extension and
branch logic accordingly.

### Extracting text from PDFs and DOCX
```python
reader = pypdf.PdfReader(file_path)
for page in reader.pages:
    text += page.extract_text() + "\n"
```
```python
doc = docx.Document(file_path)
text = "\n".join([para.text for para in doc.paragraphs])
```
Both libraries parse the binary file format into a Python object with a **collection of
paragraphs/pages**, which you loop through to build a single text string.

### Generating a `.docx` file
```python
from docx import Document
doc = Document()
doc.add_paragraph("some text")
doc.save("output.docx")
```
Creates a new, blank Word document object, adds paragraphs one at a time, then writes it to disk.

### Multi-line terminal input
```python
lines = []
while True:
    line = input()
    if line.strip().upper() == "END":
        break
    lines.append(line)
jd_text = "\n".join(lines)
```
`input()` only reads one line at a time, so this loops, collecting each line until the user
types a sentinel value (`END`), then joins them back into one multi-line string.

### Dynamic, safe filenames
```python
safe_person = "_".join(person_name.strip().split())
```
`.split()` breaks a string into words on whitespace, `"_".join(...)` recombines them with
underscores instead, e.g. `"Lakshmi Chakka"` → `"Lakshmi_Chakka"`, safe for use as a filename
(no spaces).

### The `if __name__ == "__main__":` block
```python
if __name__ == "__main__":
    main()
```
This code only runs when the file is executed directly (`python file.py`), **not** when it's
imported by another file (like `main.py` importing functions from `resume_rewriter.py`). This is
why each script can be tested standalone *and* reused as a module.

---

## 4. The Bigger Picture

This project reinforced that most practical LLM applications are built from the **same small set
of building blocks**, repeated and recombined:
1. Gather input text (from files, user typing, or previous LLM output)
2. Construct a prompt (system role + few-shot example + the actual data + any guardrails)
3. Call the API with the right parameters (model, temperature, JSON mode or not)
4. Handle the output (parse as JSON, or save as a file, or just display it)

Once this pattern feels automatic, it becomes much easier to see how larger systems (agents,
RAG pipelines, multi-step workflows) are really just this same loop, chained and orchestrated
across multiple steps.
