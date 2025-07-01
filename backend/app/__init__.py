# backend/app/__init__.py

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# 1. Cria as extensões FORA da função create_app
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    """
    Cria e configura uma instância da aplicação Flask.
    Este é o padrão "Application Factory".
    """
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": os.getenv("FRONTEND_URL", "http://localhost:5173")}})
    
    # 2. Configura a aplicação
    DB_USER = os.getenv('MYSQL_USER')
    DB_PASSWORD = os.getenv('MYSQL_PASSWORD')
    DB_HOST = os.getenv('MYSQL_HOST', 'db')
    DB_NAME = os.getenv('MYSQL_DATABASE')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 3. Associa as extensões com a aplicação
    db.init_app(app)
    migrate.init_app(app, db)

    # 4. Importa e registra os blueprints DEPOIS que tudo foi inicializado
    with app.app_context():
        from . import routes  # Importação local para quebrar o ciclo
        
        # Opcional: Carrega o texto do checklist aqui se necessário, 
        # mas a melhor prática é mantê-lo dentro da própria rota que o usa.
        # Vamos deixar a lógica de carregamento dentro da rota por enquanto.

        app.register_blueprint(routes.bp, url_prefix='/api')

    app.logger.info("Aplicação BlauSight criada e configurada com sucesso.")
    return app