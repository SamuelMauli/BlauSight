from docx import Document

def parse_desvio_docx(path):
    doc = Document(path)
    lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    data = {
        "area": "",
        "descricao": "",
        "classificacao": "",
        "causa_raiz": "",
        "CAPA": "",
    }

    for line in lines:
        if line.lower().startswith("área:"):
            data['area'] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("descrição:"):
            data['descricao'] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("classificação:"):
            data['classificacao'] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("causa raiz:"):
            data['causa_raiz'] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("capa:"):
            data['CAPA'] = line.split(":", 1)[1].strip()

    return data
