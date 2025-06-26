# backend/app/routes.py
from flask import Blueprint, request, jsonify, current_app
from .models import db, Deviation
from .extractor import parse_document
from .ml_engine import train_model, predict_from_text
import pandas as pd
import zipfile
import tempfile
import shutil
import os

# O nome do blueprint 'api' é mais semântico para uma API
bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route("/status", methods=['GET'])
def status():
    """Endpoint de teste para verificar se a API está online."""
    return jsonify({"status": "online"}), 200

@bp.route('/upload_zip', methods=['POST'])
def upload_zip():
    """
    Recebe um arquivo .zip, extrai os dados, salva no banco
    e treina o modelo de IA com todos os dados existentes.
    Retorna uma resposta JSON.
    """
    if 'zipfile' not in request.files:
        return jsonify({"error": "Nenhum arquivo .zip foi enviado"}), 400

    zip_file = request.files['zipfile']
    if not zip_file or not zip_file.filename.endswith('.zip'):
        return jsonify({"error": "Arquivo inválido. Por favor, envie um .zip"}), 400

    temp_dir = tempfile.mkdtemp()
    try:
        zip_path = os.path.join(temp_dir, zip_file.filename)
        zip_file.save(zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        new_records_count = 0
        for filename in os.listdir(temp_dir):
            if filename.endswith('.docx'):
                path = os.path.join(temp_dir, filename)
                parsed_data = parse_document(path)
                
                if parsed_data and parsed_data.get('id_desvio'):
                    exists = db.session.query(Deviation.id).filter_by(id_desvio=parsed_data['id_desvio']).first()
                    if not exists:
                        new_deviation = Deviation(**parsed_data)
                        db.session.add(new_deviation)
                        new_records_count += 1
        
        if new_records_count > 0:
            db.session.commit()
            
            all_deviations = Deviation.query.all()
            if len(all_deviations) > 1:
                # O Pandas cria o DataFrame a partir de uma lista de objetos do SQLAlchemy
                df = pd.DataFrame([d.__dict__ for d in all_deviations])
                train_model(df)
                message = f"{new_records_count} novos desvios salvos. Modelo treinado com sucesso!"
            else:
                message = f"{new_records_count} novos desvios salvos, mas dados insuficientes para treinar."
            
            return jsonify({"message": message}), 200
        else:
            return jsonify({"message": "Nenhum desvio novo encontrado nos arquivos."}), 200

    except Exception as e:
        # Em um ambiente de produção real, logue o erro `e`
        return jsonify({"error": "Ocorreu um erro interno no servidor ao processar o arquivo."}), 500
    finally:
        shutil.rmtree(temp_dir)


@bp.route('/analyze', methods=['POST'])
def analyze():
    """
    Recebe uma descrição de desvio em JSON, usa o modelo para
    prever a causa raiz e retorna a predição em JSON.
    """
    data = request.get_json()
    if not data or not data.get('description'):
        return jsonify({"error": "A descrição do desvio é obrigatória."}), 400

    description = data['description'].strip()
    model_path = os.path.join(current_app.instance_path, current_app.config['MODEL_PATH'])

    if not os.path.exists(model_path):
        return jsonify({"error": "O modelo ainda não foi treinado. Por favor, envie dados de treinamento primeiro."}), 409

    try:
        prediction = predict_from_text(description)
        return jsonify({
            "description": description,
            "prediction": prediction
        }), 200

    except Exception as e:
        # Em um ambiente de produção real, logue o erro `e`
        return jsonify({"error": "Ocorreu um erro interno no servidor durante a análise."}), 500