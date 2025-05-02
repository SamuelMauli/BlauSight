from flask import Flask
from app.routes import bp as main_routes
from app.models import db
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Adiciona esta linha:
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

# Inicializa o banco e rotas
db.init_app(app)
app.register_blueprint(main_routes)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
