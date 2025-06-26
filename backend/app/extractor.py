import docx
import pypdf
import re
import os

def parse_text_with_keywords(full_text_lines):
    """Função genérica para extrair dados de uma lista de linhas de texto usando palavras-chave."""
    data = {}
    keywords = {
        'area': 'Área:',
        'gestor': 'Gestor:',
        'data_desvio': 'Data do Desvio:',
        'produto': 'Produto:',
        'lote': 'Lote:',
        'id_desvio': 'ID do Desvio:',
        'descricao': 'Descrição do Desvio:',
        'causa_raiz': 'Causa Raiz do Desvio:'
    }
    
    keyword_map = {v: k for k, v in keywords.items()}
    current_key = None
    content_buffer = []

    for line in full_text_lines:
        found_keyword = False
        for keyword_text in keyword_map.keys():
            # Procura a palavra-chave no início da linha, ignorando espaços em branco
            if line.strip().startswith(keyword_text):
                if current_key:
                    data[current_key] = "\n".join(content_buffer).strip()

                current_key = keyword_map[keyword_text]
                content_buffer = [line.strip().split(keyword_text, 1)[1].strip()]
                found_keyword = True
                break
        
        if not found_keyword and current_key:
            content_buffer.append(line.strip())

    if current_key and content_buffer:
        data[current_key] = "\n".join(content_buffer).strip()
    
    return data

def extract_data_from_docx(doc_path):
    """Extrai dados de um arquivo .docx."""
    try:
        doc = docx.Document(doc_path)
        lines = [p.text for p in doc.paragraphs if p.text.strip()]
        return parse_text_with_keywords(lines)
    except Exception as e:
        print(f"Erro ao ler o DOCX {os.path.basename(doc_path)}: {e}")
        return None

def extract_data_from_pdf(pdf_path):
    """Extrai dados de um arquivo .pdf."""
    try:
        with open(pdf_path, 'rb') as f:
            reader = pypdf.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        
        lines = text.split('\n')
        return parse_text_with_keywords(lines)
    except Exception as e:
        print(f"Erro ao ler o PDF {os.path.basename(pdf_path)}: {e}")
        return None