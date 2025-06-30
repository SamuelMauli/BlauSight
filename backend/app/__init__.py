import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

# 1. Instancie o CORS fora da função
cors = CORS()
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # --- Configuração do CORS ---
    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
    
    # 2. Use 'init_app' para aplicar a configuração ao app
    #    Isso garante que o Gunicorn e o Flask-Cors funcionem bem juntos.
    cors.init_app(app, 
                  resources={r"/api/*": {"origins": frontend_url}}, 
                  supports_credentials=True)
    
    logging.basicConfig(level=logging.INFO)
    app.logger.info(f"CORS configurado para permitir a origem: {frontend_url}")

    # --- Configuração da Aplicação ---
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key-for-dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    
    with app.app_context():
        from . import routes
        app.register_blueprint(routes.bp, url_prefix='/api')
    
    app.logger.info("Aplicação criada com sucesso.")
    return app