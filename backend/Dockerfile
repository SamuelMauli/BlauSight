FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de dependências primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código da aplicação
COPY . .

# Expõe a porta que o Gunicorn vai usar
EXPOSE 8000

# CORREÇÃO: Comando para iniciar a aplicação em modo de desenvolvimento com Gunicorn.
# O Gunicorn agora irá monitorar as mudanças nos arquivos e reiniciar automaticamente.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--reload", "run:app"]