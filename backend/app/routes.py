from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import zipfile
import tempfile
import shutil
import logging
import io

# Importações que estavam faltando ou foram perdidas
from .extractor import extract_data_from_docx, extract_data_from_pdf
from .models import Deviation, db
from .ml_engine import train_model, predict_deviation, explain_prediction
from .utils import generate_pdf_report
from groq import Groq


logging.basicConfig(level=logging.INFO)


bp = Blueprint('api', __name__)

ALLOWED_EXTENSIONS = {'docx', 'pdf', 'zip'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_document(doc_path):
    """Processa um único documento (docx ou pdf) e o adiciona ao banco."""
    try:
        if doc_path.lower().endswith('.docx'):
            data = extract_data_from_docx(doc_path)
        elif doc_path.lower().endswith('.pdf'):
            data = extract_data_from_pdf(doc_path)
        else:
            return None

        if data and data.get('id_desvio'):
            exists = db.session.query(Deviation.id).filter_by(id_desvio=data['id_desvio']).first()
            if not exists:
                new_deviation = Deviation(**data)
                db.session.add(new_deviation)
                return data
    except Exception as e:
        logging.error(f"Erro ao processar o documento {os.path.basename(doc_path)}: {e}")
    return None

@bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nome de arquivo vazio"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        temp_dir = tempfile.mkdtemp()
        saved_path = os.path.join(temp_dir, filename)
        file.save(saved_path)

        processed_files_count = 0
        
        try:
            if filename.lower().endswith('.zip'):
                with zipfile.ZipFile(saved_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                for item in os.listdir(temp_dir):
                    item_path = os.path.join(temp_dir, item)
                    if os.path.isfile(item_path) and (item.lower().endswith('.docx') or item.lower().endswith('.pdf')):
                        if process_document(item_path):
                            processed_files_count += 1
            else:
                if process_document(saved_path):
                    processed_files_count = 1
            
            if processed_files_count > 0:
                db.session.commit()
                message = f"{processed_files_count} novo(s) desvio(s) salvo(s) com sucesso."
                return jsonify({"message": message}), 200
            else:
                return jsonify({"message": "Nenhum desvio novo encontrado ou os desvios já existem no banco."}), 200

        except zipfile.BadZipFile:
            return jsonify({"error": "Arquivo ZIP inválido ou corrompido"}), 400
        except Exception as e:
            logging.error(f"Erro inesperado no upload: {e}")
            return jsonify({"error": "Ocorreu um erro inesperado no servidor"}), 500
        finally:
            shutil.rmtree(temp_dir)
    else:
        return jsonify({"error": "Tipo de arquivo não permitido. Use .docx, .pdf ou .zip"}), 400

@bp.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    if not data or 'description' not in data:
        return jsonify({"error": "Descrição do desvio não fornecida"}), 400
    description = data['description']
    try:
        prediction, probability = predict_deviation(description)
        # O modelo retorna 'Procedente' ou 'Improcedente'
        return jsonify({"prediction": prediction, "probability": float(probability)}), 200
    except FileNotFoundError as e:
        logging.error(f"Erro na predição: {e}")
        return jsonify({"error": "Modelo de IA ainda não foi treinado. Por favor, envie arquivos para treinamento primeiro."}), 500
    except Exception as e:
        logging.error(f"Erro na predição: {e}")
        return jsonify({"error": "Erro ao realizar a predição"}), 500

@bp.route('/train', methods=['POST'])
def train():
    try:
        result = train_model()
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"Erro no treinamento: {e}")
        return jsonify({"error": f"Erro durante o treinamento: {str(e)}"}), 500

@bp.route('/report/<int:deviation_id>', methods=['GET'])
def get_report(deviation_id):
    try:
        deviation = Deviation.query.get_or_404(deviation_id)
        pdf_bytes = generate_pdf_report(deviation)
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'relatorio_desvio_{deviation.id_desvio}.pdf'
        )
    except Exception as e:
        logging.error(f"Erro ao gerar relatório para o desvio {deviation_id}: {e}")
        return jsonify({"error": "Não foi possível gerar o relatório"}), 500

@bp.route('/explain/<int:deviation_id>', methods=['GET'])
def get_explanation(deviation_id):
    try:
        deviation = Deviation.query.get_or_404(deviation_id)
        explanation = explain_prediction(deviation.descricao)
        return jsonify({"explanation": explanation}), 200
    except Exception as e:
        logging.error(f"Erro ao gerar explicação para o desvio {deviation_id}: {e}")
        return jsonify({"error": "Não foi possível gerar a explicação"}), 500

bp.route('/chat', methods=['POST'])
def chat_request():
    api_key = os.environ.get("GROQ_API_KEY")
    # Agora o log vai funcionar corretamente
    current_app.logger.info(f"Tentando acessar /chat. Valor da GROQ_API_KEY: '{'...' if api_key else 'None'}'")

    if not api_key:
        current_app.logger.error("A chave da API da Groq não foi encontrada nas variáveis de ambiente.")
        return jsonify({"error": "A chave da API da Groq não está configurada no servidor."}), 500

    try:
        client = Groq(api_key=api_key)
        
        data = request.get_json()
        user_message = data.get('message')

        if not user_message:
            return jsonify({"error": "Nenhuma mensagem fornecida."}), 400

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente prestativo."
                },
                {
                    "role": "user",
                    "content": user_message,
                }
            ],
            model="llama3-8b-8192",
        )

        reply = chat_completion.choices[0].message.content
        return jsonify({"reply": reply})

    except Exception as e:
        current_app.logger.error(f"Ocorreu um erro na API do Groq: {e}")
        return jsonify({"error": str(e)}), 500
    
@bp.route('/deviations', methods=['GET'])
def get_deviations():
    try:
        deviations = Deviation.query.order_by(Deviation.id.desc()).all()
        return jsonify([d.to_dict() for d in deviations]), 200
    except Exception as e:
        logging.error(f"Erro ao buscar desvios: {e}")
        return jsonify({"error": "Erro ao buscar desvios"}), 500