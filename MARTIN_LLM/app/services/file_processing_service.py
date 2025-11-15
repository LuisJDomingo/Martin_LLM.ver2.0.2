import os
from PyPDF2 import PdfReader
from docx import Document

def extract_text(file_path):
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    if ext == '.txt':
        return extract_text_from_txt(file_path)
    elif ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext == '.docx':
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Formato no soportado: {ext}")
def extract_text_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()
def extract_text_from_pdf(file_path):
    text = ""
    reader = PdfReader(file_path)
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text
def extract_text_from_docx(file_path):
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)


def process_file_with_llm(file_path, llm_model):
    try:
        text = extract_text(file_path)
    except Exception as e:
        return f"Error al extraer texto: {e}"

    # Aquí es donde llamas al LLM, ejemplo:
    # resultado = llm_model.process(text)

    # Para que te hagas una idea, algo así:
    resultado = llm_model.chat(text)  # Ajusta según tu API/modelo real

    return resultado
