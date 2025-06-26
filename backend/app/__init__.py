from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import logging

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Configuração de Logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

    # Configuração do Banco de Dados
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database', 'database.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicialização do DB
    db.init_app(app)

    # Criação das pastas necessárias
    upload_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
    model_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'model')
    os.makedirs(upload_folder, exist_ok=True)
    os.makedirs(model_folder, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_folder

    from . import routes
    app.register_blueprint(routes.bp, url_prefix='/api')

    with app.app_context():
        from . import models
        db.create_all()

    return app