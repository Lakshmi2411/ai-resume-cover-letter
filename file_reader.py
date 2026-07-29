import pypdf
import docx


def extract_text(file_path):
    if file_path.endswith(".pdf"):
        reader = pypdf.PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text

    elif file_path.endswith(".docx"):
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text

    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    else:
        raise ValueError(
            "Unsupported file format. Please upload a PDF, DOCX, or TXT file."
        )


if __name__ == "__main__":
    text = extract_text("sample_resumes\\LChakka_CV_Antare.pdf")
    print(text)
