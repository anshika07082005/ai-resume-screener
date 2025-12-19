from PyPDF2 import PdfReader

def extract_text_from_pdf(upload_file):
    upload_file.file.seek(0)
    reader = PdfReader(upload_file.file)

    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"

    return text
