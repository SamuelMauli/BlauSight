# backend/app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS  # 1. Importe a extensão CORS
from flask_migrate import Migrate
import os

from .config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 2. Inicialize o CORS para toda a aplicação.
    # Isso permite que seu frontend acesse todas as rotas da API.
    CORS(app)

    db.init_app(app)
    migrate.init_app(app, db)

    # Registro do blueprint
    from .routes import bp as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    app.logger.info("Aplicação BlauSight criada e configurada com sucesso.")
    return app