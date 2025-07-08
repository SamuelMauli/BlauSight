from flask import Blueprint, request, jsonify, current_app, Response, send_from_directory
from werkzeug.utils import secure_filename
import os
import zipfile
import tempfile
import shutil
import logging
import json
import time
from groq import Groq
from flask import send_from_directory, make_response

from .extractor import get_text_from_docx, get_text_from_pdf
from .models import Deviation, db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s] - %(message)s')
bp = Blueprint('api', __name__)
ALLOWED_EXTENSIONS = {'docx', 'pdf', 'zip'}
UPLOAD_FOLDER = 'uploads'

def _get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        current_app.logger.error("GROQ_API_KEY não encontrada no ambiente.")
        raise ValueError("A chave da API da Groq não foi configurada no servidor.")
    return Groq(api_key=api_key)

def _clean_json_from_response(raw_text: str) -> dict:
    json_start = raw_text.find('{')
    json_end = raw_text.rfind('}')
    if json_start == -1 or json_end == -1:
        raise json.JSONDecodeError("Nenhum objeto JSON válido encontrado na resposta da IA.", raw_text, 0)
    json_str = raw_text[json_start : json_end + 1]
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        current_app.logger.error(f"Falha ao decodificar JSON após limpeza: {e.msg}. JSON Tentado: '{json_str}'")
        raise

def _call_groq_with_retries(messages, json_mode=True, max_retries=3):
    client = _get_groq_client()
    for attempt in range(max_retries):
        try:
            chat_completion = client.chat.completions.create(
                messages=messages, model="llama3-70b-8192", temperature=0.1, max_tokens=8000
            )
            response_text = chat_completion.choices[0].message.content
            if json_mode:
                return _clean_json_from_response(response_text)
            return response_text
        except (json.JSONDecodeError, IndexError) as e:
            current_app.logger.warning(f"Tentativa {attempt + 1} falhou. Erro de formato da IA: {e}. Retentando em {2 ** attempt}s...")
        except Exception as e:
            current_app.logger.error(f"Erro inesperado na API Groq na tentativa {attempt + 1}: {e}", exc_info=True)
        time.sleep((2 ** attempt))
    current_app.logger.critical(f"Falha CRÍTICA ao obter uma resposta válida da API Groq após {max_retries} tentativas.")
    raise Exception(f"O serviço de IA não respondeu adequadamente após {max_retries} tentativas.")


@bp.route('/upload', methods=['POST'])
def upload_file():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    if 'file' not in request.files: return jsonify({"error": "Nenhum arquivo enviado."}), 400
    
    file = request.files['file']
    original_filename = secure_filename(file.filename)
    if not ('.' in original_filename and original_filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS):
        return jsonify({"error": f"Tipo de arquivo não permitido."}), 400

    temp_dir = tempfile.mkdtemp()
    try:
        processed_deviations = []
        def process_and_save_document(doc_path, original_name):
            permanent_path = os.path.join(UPLOAD_FOLDER, original_name)
            shutil.copy(doc_path, permanent_path)
            
            text_content = get_text_from_docx(doc_path) if doc_path.lower().endswith('.docx') else get_text_from_pdf(doc_path)
            if not text_content:
                logging.warning(f"Nenhum texto extraído de {original_name}"); return

            system_prompt = "Você é um especialista em Garantia da Qualidade farmacêutica. Sua tarefa é analisar relatórios de desvio, extrair dados-chave e gerar insights analíticos."
            user_prompt = f"""
            Analise o relatório de desvio contido no texto abaixo. Extraia as informações solicitadas e gere os insights analíticos em formato JSON.

            **Texto do Relatório:**
            ---
            {text_content[:8000]}
            ---

            **Sua Tarefa (Responda APENAS com o objeto JSON):**
            1.  **Extraia os seguintes campos do texto:** "id_desvio", "data_identificacao", "descricao", "causa_raiz", "acao_corretiva", "status_acao", "classificacao_desvio".
                -   Se 'id_desvio' não estiver no texto, extraia o número do nome do arquivo: '{original_name}'.
                -   Se outros campos não forem encontrados, retorne "N/A".
            2.  **Gere Keywords Analíticas:** Crie uma lista de 5 a 7 `keywords` que capturem a essência do problema (ex: "excursão de temperatura", "falha de equipamento", "contaminação microbiológica", "erro de procedimento").
            3.  **Forneça uma Análise da Falha:** No campo `failure_analysis`, escreva uma observação técnica curta (1-2 frases) sobre a natureza da falha. Ex: "A falha parece ser de natureza mecânica, relacionada ao desgaste de componentes de vedação, e não um erro operacional."

            **Objeto JSON de Saída:**
            {{
                "id_desvio": "...",
                "data_identificacao": "...",
                "descricao": "...",
                "causa_raiz": "...",
                "acao_corretiva": "...",
                "status_acao": "...",
                "classificacao_desvio": "...",
                "keywords": ["...", "..."],
                "failure_analysis": "..."
            }}
            """
            
            try:
                extracted_data = _call_groq_with_retries([
                    {"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}
                ])
                
                desvio_id = extracted_data.get('id_desvio', f"GEN_{int(time.time())}")
                if db.session.query(Deviation.id).filter_by(id_desvio=desvio_id).first():
                    current_app.logger.info(f"Desvio {desvio_id} já existe. Pulando."); return

                keywords_list = extracted_data.get('keywords', [])
                
                new_deviation = Deviation(
                    id_desvio=desvio_id,
                    data_identificacao=extracted_data.get('data_identificacao', 'N/A'),
                    descricao=extracted_data.get('descricao', 'Descrição não extraída.'),
                    causa_raiz=extracted_data.get('causa_raiz', 'Não especificada.'),
                    acao_corretiva=extracted_data.get('acao_corretiva', 'Não especificada.'),
                    status_acao=extracted_data.get('status_acao', 'Não especificado.'),
                    classificacao_desvio=extracted_data.get('classificacao_desvio', 'Não classificado.'),
                    keywords=', '.join(keywords_list) if isinstance(keywords_list, list) else '',
                    failure_analysis=extracted_data.get('failure_analysis', 'Análise não gerada.'),
                    file_path=permanent_path
                )
                processed_deviations.append(new_deviation)
            except Exception as e:
                current_app.logger.error(f"Falha ao processar {original_name} com IA: {e}", exc_info=True)

        temp_file_path = os.path.join(temp_dir, original_filename)
        file.save(temp_file_path)

        if original_filename.lower().endswith('.zip'):
            with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
                for member in zip_ref.namelist():
                    if not member.startswith('__MACOSX') and member.rsplit('.', 1)[-1].lower() in ('docx', 'pdf'):
                        unique_filename = f"{int(time.time())}_{secure_filename(os.path.basename(member))}"
                        extracted_path = zip_ref.extract(member, temp_dir)
                        process_and_save_document(extracted_path, unique_filename)
        else:
            process_and_save_document(temp_file_path, original_filename)
        
        if processed_deviations:
            db.session.add_all(processed_deviations)
            db.session.commit()
            return jsonify({"message": f"{len(processed_deviations)} novo(s) desvio(s) processado(s) e salvo(s)."}), 200
        
        return jsonify({"message": "Nenhum desvio novo foi processado."}), 200
    except Exception as e:
        current_app.logger.error(f"Erro fatal no endpoint de upload: {e}", exc_info=True)
        return jsonify({"error": "Ocorreu um erro crítico no servidor."}), 500
    finally:
        shutil.rmtree(temp_dir)

# NOVA ROTA PARA VISUALIZAR DOCUMENTOS
@bp.route('/document/<string:desvio_id>', methods=['GET'])
def get_document(desvio_id):
    """
    Serve o arquivo original para ser exibido no navegador.
    A extensão Flask-CORS gerenciará os headers de permissão.
    """
    try:
        desvio = db.session.query(Deviation).filter_by(id_desvio=desvio_id).first_or_404()

        if not desvio.file_path:
            return jsonify({"error": "Nenhum arquivo associado a este desvio."}), 404

        directory = os.path.abspath(UPLOAD_FOLDER)
        filename = os.path.basename(desvio.file_path)

        if not os.path.exists(os.path.join(directory, filename)):
             return jsonify({"error": "Arquivo físico não encontrado no servidor."}), 404

        return send_from_directory(directory, filename)

    except Exception as e:
        current_app.logger.error(f"Erro ao servir documento para desvio {desvio_id}: {e}", exc_info=True)
        return jsonify({"error": "Erro interno do servidor."}), 500

@bp.route('/predict', methods=['POST'])
def predict_with_groq():
    data = request.get_json()
    if not data or 'description' not in data:
        return jsonify({"error": "O campo 'description' do desvio é obrigatório para a análise."}), 400

    try:
        recent_deviations = Deviation.query.order_by(Deviation.id.desc()).limit(15).all()
        context_examples = "\n\n".join([
            f"Desvio ID: {d.id_desvio}\nDescrição: {d.descricao}\nCausa Identificada: {d.causa_raiz}\nAção Corretiva Aplicada: {d.acao_corretiva}"
            for d in recent_deviations
        ])

        system_prompt = "Você é um especialista sênior em Garantia da Qualidade na indústria farmacêutica, focado em criar planos de CAPA (Ações Corretivas e Preventivas) robustos e auditáveis."
        user_prompt = f"""
        Analise o novo desvio, considerando o contexto de desvios históricos. Forneça um plano de ação CAPA completo em formato JSON.

        **Contexto (Desvios Históricos Relevantes):**
        {context_examples}

        **Novo Desvio para Análise (Reporte Atual):**
        "{data['description']}"

        **Sua Tarefa (Responda APENAS com o objeto JSON):**
        Gere um relatório JSON com a estrutura abaixo:
        {{
            "risk_assessment": {{
                "level": "Crítico, Maior ou Menor",
                "justification": "Justifique o nível de risco com base no impacto potencial no produto, paciente e conformidade regulatória."
            }},
            "root_cause_analysis": {{
                "probable_cause": "Descreva a causa raiz mais provável, de forma técnica e detalhada.",
                "evidence": "Justifique sua conclusão com base nas evidências do reporte atual e nas similaridades com o histórico."
            }},
            "proposed_solution_capa": {{
                "containment_actions": ["Liste 1-2 ações de contenção para limitar o impacto imediato. Ex: 'Segregar e colocar o lote XXX em quarentena.'"],
                "corrective_actions": ["Liste 2-3 ações corretivas para eliminar a causa raiz. Ex: 'Revisar e retreinar toda a equipe de produção no POP-123.'"],
                "preventive_actions": ["Liste 1-2 ações preventivas para evitar recorrência em processos/produtos similares. Ex: 'Implementar verificação dupla de setup em todas as linhas de compressão.'"]
            }},
            "similar_deviations_ids": ["Liste os IDs dos 2-3 desvios históricos mais relevantes que fundamentaram sua análise."]
        }}
        """
        
        prediction_data = _call_groq_with_retries([
            {"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}
        ])
        
        return jsonify(prediction_data), 200

    except Exception as e:
        current_app.logger.error(f"Falha crítica na rota /predict: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@bp.route('/chat', methods=['POST'])
def chat_request():
    data = request.get_json()
    if not data or not data.get('message'):
        return jsonify({"error": "O campo 'message' é obrigatório."}), 400
        
    try:
        recent_deviations = Deviation.query.order_by(Deviation.id.desc()).limit(50).all()
        context_dossier = "\n".join([
            f"- ID: {d.id_desvio} | Status: {d.status_acao} | Classificação: {d.classificacao_desvio} | Descrição: {d.descricao}"
            for d in recent_deviations
        ]) if recent_deviations else "Nenhum dado de desvio encontrado no sistema."

        system_prompt = "Você é o assistente BlauSight, especialista em dados de qualidade. Responda de forma concisa e direta, baseando-se estritamente nas informações do dossiê. Se a informação não estiver disponível, afirme que não encontrou dados sobre o assunto."
        user_prompt = f"""
        **Dossiê de Desvios Recentes:**
        ---
        {context_dossier}
        ---
        **Pergunta do Usuário:** "{data['message']}"
        **Sua Resposta:**
        """

        def generate_stream():
            try:
                client = _get_groq_client()
                stream = client.chat.completions.create(
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                    model="llama3-8b-8192", stream=True, temperature=0.1
                )
                for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content: yield content
            except Exception as e:
                current_app.logger.error(f"Erro durante o streaming da Groq: {e}", exc_info=True)
                yield "Desculpe, um erro interno ocorreu ao gerar a sua resposta."

        return Response(generate_stream(), mimetype='text/plain; charset=utf-8')

    except Exception as e:
        current_app.logger.error(f"Erro fatal na rota /chat: {e}", exc_info=True)
        return jsonify({"error": "Erro crítico no servidor ao processar o chat."}), 500

@bp.route('/deviations', methods=['GET'])
def get_deviations():
    try:
        deviations = Deviation.query.order_by(Deviation.id.desc()).all()
        return jsonify([d.to_dict() for d in deviations]), 200
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar desvios no banco de dados: {e}", exc_info=True)
        return jsonify({"error": "Ocorreu um erro ao acessar o banco de dados."}), 500
        
@bp.route('/analyze-dossier', methods=['POST'])
def analyze_dossier():
    if 'dossier_file' not in request.files:
        return jsonify({"error": "Nenhum arquivo de dossiê foi enviado."}), 400

    dossier_file = request.files['dossier_file']
    if not dossier_file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Formato de arquivo inválido. Por favor, envie um arquivo PDF."}), 400

    try:
        dossier_text = get_text_from_pdf(dossier_file)
        if not dossier_text or len(dossier_text) < 100:
            return jsonify({"error": "Não foi possível extrair conteúdo válido do PDF enviado."}), 400
        
        is_truncated = len(dossier_text) > 15000
        
        system_prompt = "Você é o 'CDT Expert', um especialista em assuntos regulatórios da ANVISA com 20 anos de experiência. Sua análise deve ser implacável, precisa e detalhada, focando em não-conformidades críticas e inconsistências entre módulos."
        
        # O prompt agora contém o checklist detalhado extraído do documento do usuário
        user_prompt = f"""
        Analise o Dossiê do Usuário fornecido, utilizando o checklist de validação detalhado abaixo. Foque em identificar não-conformidades e inconsistências.

        **Dossiê do Usuário (Conteúdo Parcial):**
        ---
        {dossier_text[:14000]} 
        ---

        **Checklist de Validação Detalhado (Baseado na ANVISA):**
        1.  **Módulo 1 - Administrativo e Rotulagem:**
            -   [ ] **1.2.1 Formulários de Petição (FP1/FP2):** Presença e preenchimento.
            -   [ ] **1.2.4 Certificado de Responsabilidade Técnica:** Presença e validade.
            -   [ ] **1.3.1 Rotulagem (Embalagem Primária e Secundária):** Presença e conformidade.
            -   [ ] **1.5.1 Certificado de Boas Práticas de Fabricação (CBPF):** Presença, validade e escopo correto para TODOS os locais de fabricação (IFA e produto acabado).
            -   [ ] **Validação Cruzada M1 x M3:** As 'condições de armazenamento' e 'prazo de validade' na rotulagem (M1) são idênticas às suportadas pelo estudo de estabilidade (M3)?
            -   [ ] **Validação Cruzada M1 x M5:** As 'indicações terapêuticas' na bula (M1) são exatamente as mesmas comprovadas nos estudos clínicos de eficácia (M5)?

        2.  **Módulo 3 - Qualidade (CMC):**
            -   [ ] **3.2.S.4 Controle do IFA:** Apresentação de especificações e relatórios de validação dos métodos analíticos.
            -   [ ] **3.2.P.8 Estabilidade do Produto Acabado:** Relatório completo, com dados de longa duração e acelerado, conforme RDC 318/2019. O protocolo está correto (condições, frequência)?

        3.  **Módulo 5 - Estudos Clínicos:**
            -   [ ] **5.3.1 Estudo de Bioequivalência (para Genéricos/Similares):** Relatório completo apresentado? A análise estatística (IC 90%) está dentro do intervalo de 80.00% a 125.00%?
            -   [ ] **5.3.5 Estudos de Eficácia e Segurança (para Novos/Inovadores):** Apresentação de relatórios completos para Fases I, II e III?

        **Sua Tarefa (Responda APENAS com o objeto JSON):**
        Gere um relatório JSON com a estrutura abaixo. Para cada item, avalie a conformidade (is_compliant: true/false) e forneça uma justificativa curta e direta.

        {{
          "overall_summary": {{
            "product_type_identified": "Tipo do produto (Genérico, Novo, etc.)",
            "overall_status": "Requer Atenção Crítica, Aprovado com Ressalvas, ou Conformidade Alta",
            "critical_findings": "Resuma em uma frase os 2-3 pontos de maior risco ou não-conformidades mais graves encontradas."
          }},
          "was_truncated": {str(is_truncated).lower()},
          "modules_validation": {{
            "module_1": [
                {{ "item": "Formulários Administrativos (FP1/FP2, CRT)", "is_compliant": true/false, "justification": "..." }},
                {{ "item": "Certificados de Boas Práticas de Fabricação (CBPF)", "is_compliant": true/false, "justification": "..." }},
                {{ "item": "Validação Cruzada: Rotulagem (M1) vs Estabilidade (M3)", "is_compliant": true/false, "justification": "Ex: Inconsistente. Rotulagem informa 30°C, mas estabilidade só suporta 25°C." }}
            ],
            "module_3": [
                {{ "item": "Validação de Métodos Analíticos (IFA e Produto Acabado)", "is_compliant": true/false, "justification": "..." }},
                {{ "item": "Estudos de Estabilidade (Protocolo e Dados Completos)", "is_compliant": true/false, "justification": "Ex: Não-conforme. Ausência de dados de estudo acelerado." }}
            ],
            "module_5": [
                {{ "item": "Estudo de Bioequivalência (Intervalo de Confiança 80-125%)", "is_compliant": true/false, "justification": "Ex: Não-conforme. IC 90% de 78.5%-129.0% está fora do limite aceitável." }}
            ]
          }}
        }}
        """

        analysis_data = _call_groq_with_retries([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])

        return jsonify(analysis_data), 200

    except Exception as e:
        current_app.logger.error(f"Falha crítica na rota /analyze-dossier: {e}", exc_info=True)
        return jsonify({"error": "Ocorreu um erro interno no servidor durante a análise do dossiê."}), 500