# frontend/Dockerfile

### ESTÁGIO 1: Build ###
# Use uma imagem node oficial como base para construir o projeto React
FROM node:18-alpine as build

# Defina o diretório de trabalho dentro do container
WORKDIR /app

# Copie os arquivos de manifesto de dependências
COPY package.json ./
COPY package-lock.json ./

# Instale as dependências do projeto
RUN npm install

# Copie todo o código-fonte do frontend para o container
COPY . .

# Execute o build de produção do Vite
# Isso irá gerar os arquivos estáticos na pasta /app/dist
RUN npm run build


### ESTÁGIO 2: Serve ###
# Use uma imagem de servidor web leve como o Nginx para servir os arquivos estáticos
FROM nginx:stable-alpine

# Copie os arquivos estáticos gerados no estágio de build para a pasta padrão do Nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Copie a configuração personalizada do Nginx (vamos criar este arquivo a seguir)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponha a porta 80, que é a porta padrão do Nginx
EXPOSE 80

# O comando padrão do Nginx já é iniciar o servidor, então não precisamos de um CMD