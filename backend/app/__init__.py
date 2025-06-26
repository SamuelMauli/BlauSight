from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Importe o Migrate
from flask_cors import CORS
import os
import logging

db = SQLAlchemy()
migrate = Migrate() # Crie a instância do Migrate

def create_app():
    app = Flask(__name__)
    CORS(app)

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database', 'database.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db) # Inicialize o Migrate aqui

    # Pastas para uploads e modelo
    upload_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
    model_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'model')
    os.makedirs(upload_folder, exist_ok=True)
    os.makedirs(model_folder, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_folder

    from . import routes
    app.register_blueprint(routes.bp, url_prefix='/api')


    return app