# Use uma imagem oficial do Python como imagem base
FROM python:3.11-slim

# Define o diretório de trabalho no contêiner
WORKDIR /app

# Instala o cliente SQLite
# Adicione estas duas linhas:
RUN apt-get update && apt-get install -y sqlite3

# Copia o arquivo de requisitos e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código da sua aplicação
COPY . .

# Expõe a porta que o Gunicorn irá rodar
EXPOSE 8000

# O comando para rodar a aplicação será definido no docker-compose.yml