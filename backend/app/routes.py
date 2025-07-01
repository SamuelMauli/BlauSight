from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import zipfile
import tempfile
import shutil
import logging
import json
import google.generativeai as genai

from .extractor import get_text_from_docx, get_text_from_pdf
from .models import Deviation, db

logging.basicConfig(level=logging.INFO)
bp = Blueprint('api', __name__)
ALLOWED_EXTENSIONS = {'docx', 'pdf', 'zip'}

ANVISA_CHECKLIST_TEXT = ""
try:
    ANVISA_CHECKLIST_TEXT = """
    Resumo do Dossiê Técnico da ANVISA:
    - Módulo 1: Informações Administrativas. Exige: Formulários FP1/FP2, Taxas, Licença, Certificado de Responsabilidade Técnica, GTIN, Bula e Rotulagem, Certificados de BPF. Validação cruzada da bula/rotulagem com os Módulos 3 e 5 é CRÍTICA.
    - Módulo 2: Resumos do CTD. Deve resumir fielmente os Módulos 3, 4 e 5. Recomenda-se português.
    - Módulo 3: Qualidade (CMC). Detalhes do IFA (fabricação, caracterização, controle, estabilidade) e do Produto Acabado (desenvolvimento, fabricação, controle, estabilidade). Os dados de estabilidade (RDC 318/2019) são um ponto crítico.
    - Módulo 4: Relatórios Não Clínicos. Estudos de Farmacologia, Farmacocinética e Toxicologia, conforme guias da ANVISA.
    - Módulo 5: Relatórios Clínicos. Para genéricos/similares, o estudo de bioequivalência (BE) é o pilar. Para novos/inovadores, são necessários estudos completos de Fase I, II e III que comprovem eficácia e segurança.
    - O tipo de produto (novo, genérico, biológico, fitoterápico) define os requisitos específicos de cada módulo.
    """
    current_app.logger.info("Blueprint do Dossiê Técnico da ANVISA carregado com sucesso.")
except Exception as e:
    current_app.logger.error(f"Não foi possível carregar o arquivo de checklist da ANVISA: {e}")


def get_gemini_model():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("A chave da API do Gemini (GEMINI_API_KEY) não foi encontrada.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

@bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400
    
    file = request.files['file']
    if file.filename == '' or not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS):
        return jsonify({"error": "Arquivo inválido ou tipo não permitido"}), 400

    filename = secure_filename(file.filename)
    temp_dir = tempfile.mkdtemp()
    
    try:
        model = get_gemini_model()
        processed_files_count = 0
        
        def process_document_with_gemini(doc_path):
            text = ""
            if doc_path.lower().endswith('.docx'):
                text = get_text_from_docx(doc_path)
            elif doc_path.lower().endswith('.pdf'):
                text = get_text_from_pdf(doc_path)

            if not text:
                logging.warning(f"Não foi possível extrair texto do documento: {doc_path}")
                return False

            prompt = f"""
            Você é um assistente de compliance e análise de qualidade farmacêutica.
            Analise o seguinte texto de um relatório de desvio e extraia as informações em formato JSON.
            O JSON deve ter as seguintes chaves: "id_desvio", "data_identificacao", "descricao", "causa_raiz", "acao_corretiva", "status_acao", "classificacao_desvio", "keywords".

            - "id_desvio": O número de identificação único do desvio. Se não encontrar, coloque "N/A".
            - "descricao": Um resumo detalhado do que aconteceu.
            - "causa_raiz": A causa fundamental do problema.
            - "acao_corretiva": As ações tomadas para corrigir.
            - "status_acao": O status atual (ex: 'Concluída', 'Em Andamento').
            - "classificacao_desvio": Classifique o desvio (ex: 'Crítico', 'Maior', 'Menor').
            - "keywords": Gere uma lista de 5 a 10 palavras-chave relevantes que resumem o desvio para facilitar buscas futuras. Ex: ["contaminação", "lote 123", "procedimento X", "falha de equipamento"].

            Texto do Documento:
            ---
            {text}
            ---

            Responda APENAS com o objeto JSON.
            """
            
            response = model.generate_content(prompt)
            cleaned_response = response.text.strip().replace('```json', '').replace('```', '')
            
            try:
                data = json.loads(cleaned_response)
                
                if data.get('id_desvio') and data['id_desvio'] != "N/A":
                    exists = db.session.query(Deviation.id).filter_by(id_desvio=data['id_desvio']).first()
                    if exists:
                        logging.info(f"Desvio {data['id_desvio']} já existe. Pulando.")
                        return False

                if 'keywords' in data and isinstance(data['keywords'], list):
                    data['keywords'] = ', '.join(data['keywords'])
                    
                new_deviation = Deviation(**data)
                db.session.add(new_deviation)
                return True
            except (json.JSONDecodeError, TypeError) as e:
                logging.error(f"Erro ao decodificar JSON do Gemini: {e}\\nResposta recebida: {response.text}")
                return False

        saved_path = os.path.join(temp_dir, filename)
        file.save(saved_path)

        if filename.lower().endswith('.zip'):
            with zipfile.ZipFile(saved_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            for item in os.listdir(temp_dir):
                item_path = os.path.join(temp_dir, item)
                if os.path.isfile(item_path) and (item.lower().endswith('.docx') or item.lower().endswith('.pdf')):
                    if process_document_with_gemini(item_path):
                        processed_files_count += 1
        else:
            if process_document_with_gemini(saved_path):
                processed_files_count = 1
        
        if processed_files_count > 0:
            db.session.commit()
            return jsonify({"message": f"{processed_files_count} novo(s) desvio(s) processado(s) pelo Gemini e salvo(s)."}), 200
        else:
            return jsonify({"message": "Nenhum desvio novo foi processado. Eles podem já existir no banco."}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logging.error(f"Erro inesperado no upload: {e}")
        return jsonify({"error": "Ocorreu um erro inesperado no servidor durante o processamento com IA."}), 500
    finally:
        shutil.rmtree(temp_dir)

@bp.route('/predict', methods=['POST'])
def predict_with_gemini():
    data = request.get_json()
    if not data or 'description' not in data:
        return jsonify({"error": "Descrição do novo desvio não fornecida."}), 400

    new_description = data['description']

    try:
        model = get_gemini_model()

        # Busca desvios no banco para dar contexto à IA
        recent_deviations = Deviation.query.order_by(Deviation.id.desc()).limit(20).all()
        # Formata o contexto para o prompt
        context_examples = "\n\n".join([
            f"--- Exemplo de Desvio Anterior ---\n"
            f"ID: {d.id_desvio}\n"
            f"Descrição: {d.descricao}\n"
            f"Causa Raiz Identificada: {d.causa_raiz}\n"
            f"Ação Corretiva Aplicada: {d.acao_corretiva}\n"
            f"Status: {d.status_acao}\n"
            f"---------------------------------"
            for d in recent_deviations
        ])

        # ✅ NOVO PROMPT INTELIGENTE
        prompt = f"""
        Você é um especialista sênior em garantia de qualidade e análise de causa raiz na indústria farmacêutica.
        Sua tarefa é analisar um novo relatório de desvio, compará-lo com exemplos históricos e fornecer uma análise completa e acionável.

        **Contexto de Desvios Históricos:**
        {context_examples}

        **Novo Desvio para Análise:**
        "{new_description}"

        **Sua Tarefa (Responda APENAS com o objeto JSON):**
        Analise o novo desvio e o contexto histórico para gerar um relatório em formato JSON com a seguinte estrutura:
        {{
            "prediction": "Procedente" ou "Improcedente",
            "probability": um float entre 0.0 e 1.0 representando sua confiança,
            "root_cause_analysis": {{
                "probable_cause": "Descreva a causa raiz mais provável para o novo desvio. Seja específico. Ex: 'Falha no procedimento de limpeza da sala X', 'Desgaste não detectado no equipamento Y'.",
                "evidence": "Justifique sua conclusão com base nos exemplos históricos. Cite os IDs dos desvios mais parecidos e explique a semelhança. Ex: 'Esta análise é baseada no desvio DEV-2025-001, que também envolveu contaminação cruzada após uma limpeza inadequada.'"
            }},
            "proposed_solution": {{
                "immediate_actions": [
                    "Liste 2-3 ações imediatas e críticas a serem tomadas. Ex: 'Segregar e colocar o lote em quarentena', 'Interditar a linha de produção para investigação'."
                ],
                "corrective_actions": [
                    "Liste 2-3 ações corretivas de longo prazo baseadas nas soluções de desvios passados. Ex: 'Revisar e reforçar o treinamento no POP de limpeza XYZ', 'Implementar checklist de dupla verificação para liberação de salas'."
                ]
            }},
            "similar_deviations": [
                "Liste os IDs (ex: 'DEV-2025-001') dos 2 ou 3 desvios históricos mais relevantes usados em sua análise."
            ]
        }}
        """

        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '')
        
        prediction_data = json.loads(cleaned_response)
        return jsonify(prediction_data), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logging.error(f"Erro na predição com Gemini: {e}")
        return jsonify({"error": "Erro ao realizar a predição com a IA"}), 500
    
@bp.route('/deviations', methods=['GET'])
def get_deviations():
    try:
        deviations = Deviation.query.order_by(Deviation.id.desc()).all()
        return jsonify([d.to_dict() for d in deviations]), 200
    except Exception as e:
        logging.error(f"Erro ao buscar desvios: {e}")
        return jsonify({"error": "Erro ao buscar desvios"}), 500
        
@bp.route('/chat', methods=['POST'])
def chat_request():
    data = request.get_json()
    user_message = data.get('message')

    if not user_message:
        return jsonify({"error": "Nenhuma mensagem fornecida."}), 400
        
    try:
        model = get_gemini_model()
        all_deviations = Deviation.query.all()

        context_dossier = "\n\n".join([
            f"ID do Desvio: {d.id_desvio}\n"
            f"Classificação: {d.classificacao_desvio}\n"
            f"Data: {d.data_identificacao}\n"
            f"Descrição: {d.descricao}\n"
            f"Causa Raiz: {d.causa_raiz}\n"
            f"Ação Corretiva: {d.acao_corretiva}\n"
            f"Status: {d.status_acao}\n"
            f"Palavras-chave: {d.keywords}"
            for d in all_deviations
        ])

        prompt = f"""
        Você é o assistente virtual da BlauSight, um especialista em análise de desvios de qualidade.
        Sua tarefa é responder à pergunta do usuário baseando-se ESTritamente nas informações fornecidas no "Dossiê de Desvios" abaixo.
        Não invente informações nem use conhecimento externo. Se a resposta não estiver no dossiê, informe que não encontrou dados sobre o assunto.

        --- INÍCIO DO DOSSIÊ DE DESVIOS ---
        {context_dossier}
        --- FIM DO DOSSIÊ DE DESVIOS ---

        Pergunta do Usuário: "{user_message}"

        Sua Resposta:
        """

        response = model.generate_content(prompt)
        
        return jsonify({"reply": response.text})

    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        current_app.logger.error(f"Ocorreu um erro na API do Gemini durante o chat: {e}")
        return jsonify({"error": f"Erro no servidor ao processar chat: {str(e)}"}), 500
    
@bp.route('/analyze-dossier', methods=['POST'])
def analyze_dossier():
    if 'dossier_file' not in request.files:
        return jsonify({"error": "Nenhum arquivo de dossiê enviado"}), 400

    dossier_file = request.files['dossier_file']
    if dossier_file.filename == '' or not dossier_file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Arquivo inválido. Envie um PDF."}), 400

    try:
        dossier_text = get_text_from_pdf(dossier_file)
        if not dossier_text or len(dossier_text) < 100:
            return jsonify({"error": "Não foi possível extrair conteúdo válido do PDF enviado."}), 400

        model = get_gemini_model()

        prompt = f"""
        Você é o "CDT Expert", um especialista em assuntos regulatórios da ANVISA.
        Sua tarefa é analisar o "Dossiê do Usuário" fornecido e compará-lo com as regras do "Checklist Regulatório da ANVISA".

        **Checklist Regulatório da ANVISA (Fonte da Verdade):**
        ---
        {ANVISA_CHECKLIST_TEXT}
        ---

        **Dossiê do Usuário (Texto para Análise):**
        ---
        {dossier_text[:15000]} # Limita o tamanho para caber no prompt
        ---

        **Sua Análise:**
        Com base no Dossiê do Usuário, identifique o tipo de produto (ex: Genérico, Novo, Biossimilar).
        Em seguida, crie um relatório de validação em formato JSON.
        Para cada módulo principal (Módulo 1, 3, 4, 5), crie um checklist.
        Para cada item do checklist, determine se ele está "compliant" (verdadeiro) ou "non-compliant" (falso) com base no conteúdo do Dossiê do Usuário.
        Forneça uma "justification" curta e direta para cada ponto, explicando sua conclusão. Se uma informação não foi encontrada, marque como "non-compliant" e justifique a ausência.

        O JSON de saída deve ter a seguinte estrutura:
        {{
        "product_type": "Tipo do Produto Identificado",
        "modules": {{
            "Módulo 1": {{
            "title": "Informações Administrativas e de Prescrição",
            "checklist": [
                {{"item": "Formulários de Petição (FP1/FP2)", "compliant": true/false, "justification": "..."}},
                {{"item": "Certificados de Boas Práticas de Fabricação (CBPF)", "compliant": true/false, "justification": "..."}},
                {{"item": "Consistência entre Rotulagem (M1) e Estabilidade (M3)", "compliant": true/false, "justification": "..."}}
            ]
            }},
            "Módulo 3": {{
            "title": "Qualidade (CMC)",
            "checklist": [
                {{"item": "Dados de estabilidade (longa duração e acelerado)", "compliant": true/false, "justification": "..."}},
                {{"item": "Validação dos métodos analíticos", "compliant": true/false, "justification": "..."}}
            ]
            }},
            "Módulo 5": {{
            "title": "Relatórios de Estudos Clínicos",
            "checklist": [
                {{"item": "Apresentação do estudo principal (ex: Bioequivalência ou Fase III)", "compliant": true/false, "justification": "..."}}
            ]
            }}
        }}
        }}
        Responda APENAS com o objeto JSON.
        """

        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '')

        analysis_data = json.loads(cleaned_response)
        return jsonify(analysis_data), 200

    except Exception as e:
        current_app.logger.error(f"Erro na análise do dossiê: {e}")
        return jsonify({"error": f"Erro no servidor ao analisar o dossiê: {str(e)}"}), 500
