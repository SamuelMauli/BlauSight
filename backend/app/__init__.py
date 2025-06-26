import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS  # <-- CORREÇÃO: Importação adicionada
from .config import Config

db = SQLAlchemy()

def create_app():
    """
    Cria e configura a instância da aplicação Flask (Application Factory).
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # Garante que a pasta 'instance' exista.
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
        
    # Configura o CORS para permitir requisições do seu frontend
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Inicialize o db com a aplicação.
    db.init_app(app)

    with app.app_context():
        # Importe as rotas e modelos aqui, dentro do contexto da aplicação,
        # para evitar importações circulares.
        from . import routes
        from . import models

        app.register_blueprint(routes.bp)

        # Crie as tabelas do banco de dados, se não existirem.
        db.create_all()

    return app
