# backend/app.py
from app import create_app, db
from app.models import Deviation

# Cria a instância da aplicação para que o Flask possa encontrá-la.
app = create_app()

# Permite que você acesse o 'db' e seus modelos no terminal do Flask.
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Deviation': Deviation}