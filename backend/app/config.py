# app/config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("A variável de ambiente 'SECRET_KEY' não foi definida. É obrigatória para a segurança da aplicação.")

    # O banco de dados será salvo na pasta 'instance' na raiz do projeto.
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # O modelo também será salvo na pasta 'instance'.
    MODEL_PATH = 'model.pkl'