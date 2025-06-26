# app/extractor.py
import docx
import re

def parse_document(doc_path):
    try:
        doc = docx.Document(doc_path)
        data = {}
        
        field_map = {
            'area': 'área:',
            'gestor': 'gestor:',
            'data_desvio': 'data do desvio:',
            'produto': 'produto:',
            'lote': 'lote:',
            'id_desvio': 'id do desvio:',
            'descricao': 'descrição do desvio:',
            'causa_raiz': 'causa raiz do desvio:'
        }

        full_text = "\n".join([para.text for para in doc.paragraphs])

        for key, keyword in field_map.items():
            # Regex mais robusto para capturar valor na mesma linha
            match = re.search(f'{re.escape(keyword)}(.*)', full_text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                data[key] = value
            else:
                data[key] = '' # Garante que todas as chaves existam

        if not data.get('descricao') or not data.get('id_desvio'):
            return None # Ignora documentos sem descrição ou ID
            
        return data
    except Exception:
        return None