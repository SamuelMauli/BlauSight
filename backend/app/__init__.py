from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate # 1. Importe o Migrate
import os

from .config import Config

db = SQLAlchemy()
migrate = Migrate() # 2. Inicialize o Migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db) # 3. Conecte o Migrate ao app e ao db

    from .routes import bp as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    # 4. REMOVA a linha abaixo! Esta é a causa do erro.
    # with app.app_context():
    #     db.create_all()

    app.logger.info("Aplicação BlauSight criada e configurada com sucesso.")
    return app