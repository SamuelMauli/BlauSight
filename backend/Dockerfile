# Use uma imagem base do Python
FROM python:3.11-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo de dependências primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instala as dependências, incluindo o conector do MySQL
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código da sua aplicação para o diretório de trabalho
COPY . .

# Expõe a porta que o Gunicorn irá rodar
EXPOSE 8000

# Comando para rodar a aplicação com Gunicorn
# Aponta para o objeto 'app' criado por 'create_app()' dentro do módulo 'run'
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "run:app"]