from file_reader import extract_text
from resume_reviewer import review_resume
from jd_matcher import match_resume_to_jd
from resume_rewriter import rewrite_resume, save_resume_as_docx, make_resume_filename
from cover_letter_generator import generate_cover_letter, extract_name_and_company, make_filename, save_as_docx
import json


def get_multiline_input(prompt_text):
    print(prompt_text)
    lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        lines.append(line)
    return "\n".join(lines)


def main():
    print("=" * 50)
    print("AI Resume & Cover Letter Assistant")
    print("=" * 50)
    print("\nWhat would you like to do?")
    print("1. Review my resume (general feedback)")
    print("2. Match my resume against a job description")
    print("3. Rewrite/tailor my resume for a job description")
    print("4. Generate a tailored cover letter")
    print("5. Do everything (match + rewrite resume + cover letter)")

    choice = input("\nEnter choice (1-5): ").strip()

    resume_path = input("\nEnter path to your resume file (pdf/docx/txt): ")
    resume_text = extract_text(resume_path)

    if choice == "1":
        result = review_resume(resume_text)
        print("\n--- Resume Review ---")
        print(json.dumps(result, indent=2))

    elif choice in ("2", "3", "4", "5"):
        jd_text = get_multiline_input(
            "\nPaste the job description below. Type END on a new line when done:\n"
        )

        if choice == "2":
            result = match_resume_to_jd(resume_text, jd_text)
            print("\n--- Match Results ---")
            print(json.dumps(result, indent=2))

        elif choice == "3":
            updated_resume = rewrite_resume(resume_text, jd_text)
            print("\n--- Tailored Resume ---\n")
            print(updated_resume)
            extracted = extract_name_and_company(resume_text, jd_text)
            resume_filename = make_resume_filename(extracted["candidate_name"], extracted["company_name"])
            save_resume_as_docx(updated_resume, resume_filename)

        elif choice == "4":
            letter = generate_cover_letter(resume_text, jd_text)
            print("\n--- Generated Cover Letter ---\n")
            print(letter)
            extracted = extract_name_and_company(resume_text, jd_text)
            filename = make_filename(extracted["candidate_name"], extracted["company_name"])
            save_as_docx(letter, filename)

        elif choice == "5":
            match_result = match_resume_to_jd(resume_text, jd_text)
            print("\n--- Match Results ---")
            print(json.dumps(match_result, indent=2))

            updated_resume = rewrite_resume(resume_text, jd_text)
            print("\n--- Tailored Resume ---\n")
            print(updated_resume)
            resume_extracted = extract_name_and_company(resume_text, jd_text)
            resume_filename = make_resume_filename(resume_extracted["candidate_name"], resume_extracted["company_name"])
            save_resume_as_docx(updated_resume, resume_filename)

            letter = generate_cover_letter(resume_text, jd_text)
            print("\n--- Generated Cover Letter ---\n")
            print(letter)
            extracted = extract_name_and_company(resume_text, jd_text)
            filename = make_filename(extracted["candidate_name"], extracted["company_name"])
            save_as_docx(letter, filename)

    else:
        print("Invalid choice. Please run again and enter a number from 1-5.")


if __name__ == "__main__":
    main()