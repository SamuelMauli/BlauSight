import os
from dotenv import load_dotenv

# Carrega o .env. Esta linha é útil para desenvolvimento local.
# No Docker, as variáveis já terão sido carregadas pelo docker-compose, mas não há problema em deixá-la.
load_dotenv() 

# Importa a função create_app DEPOIS de carregar as variáveis
from app import create_app

# Cria a instância da aplicação para que o Gunicorn possa encontrá-la
app = create_app()

if __name__ == '__main__':
    # Esta parte só é executada quando você roda 'python run.py' diretamente
    app.run(host='0.0.0.0', port=8000, debug=True)