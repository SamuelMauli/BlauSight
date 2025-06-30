# Estágio 1: Construção
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
# Opcional: Se você fosse para produção, você rodaria 'npm run build' aqui

# Estágio 2: Desenvolvimento
FROM node:18-alpine
WORKDIR /app
COPY --from=build /app ./

# Expõe a porta que o Vite irá usar
EXPOSE 5173

# Comando para iniciar o servidor de desenvolvimento usando o novo script
CMD ["npm", "run", "dev:docker"]