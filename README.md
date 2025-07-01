
# BlauSight - Análise Inteligente de Desvios

BlauSight é uma aplicação web projetada para otimizar o processo de análise e gestão de desvios de qualidade na indústria farmacêutica. Utilizando inteligência artificial, a plataforma oferece:

- Análise preditiva da causa raiz de novos desvios
- Consulta a um histórico de ocorrências
- Validação de dossiês técnicos
- Tudo em uma interface intuitiva e responsiva

---

## Visão Geral

O sistema é composto por:

- **Backend:** Flask (Python)
- **Frontend:** React (JavaScript)
- Comunicação via **API REST**
- Integração com **Google Generative AI (Gemini)**

---

## Funcionalidades Principais

- **Análise Preditiva de Causa Raiz:** Descreva um novo desvio e obtenha diagnóstico da IA.
- **Treinamento do Modelo de IA:** Envie relatórios de desvio (.docx, .pdf ou .zip) para treinar a IA.
- **Assistente de IA (Chatbot):** Faça perguntas e consulte desvios anteriores.
- **CDT Expert:** Validação de dossiês técnicos (CTD) com base nas exigências da ANVISA.
- **Interface Moderna:** Layout responsivo com tema claro/escuro.

---

## Tecnologias Utilizadas

### Backend

- **Framework:** Flask
- **Banco de Dados:** MySQL via Docker + SQLAlchemy + Flask-Migrate
- **IA:** Google Gemini API
- **Extração de Texto:** python-docx, PyPDF2

### Frontend

- **Framework:** React (Vite)
- **Estilização:** TailwindCSS
- **Ícones:** Lucide React
- **HTTP:** Axios

---

## Infraestrutura

- **Containerização:** Docker + Docker Compose

---

## Estrutura do Projeto

```
blausight/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   ├── models.py
│   │   ├── extractor.py
│   ├── migrations/
│   ├── run.py
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── public/
│   ├── Dockerfile
│   └── vite.config.js
├── docker-compose.yml
└── .env
```

---

## Como Executar

### Pré-requisitos

- Docker e Docker Compose
- Git
- Chave API do Google Gemini

### Instalação

1. **Clone o repositório:**

```bash
git clone https://github.com/samuelmauli/blausight.git
cd blausight
```

2. **Configure o `.env`:**

```dotenv
GEMINI_API_KEY=SUA_CHAVE_API_AQUI
FRONTEND_URL=http://localhost:5173
MYSQL_ROOT_PASSWORD=sua_senha_root_segura
MYSQL_DATABASE=blausight_db
MYSQL_USER=blausight_user
MYSQL_PASSWORD=sua_senha_de_usuario_segura
```

3. **Inicie os containers:**

```bash
docker-compose up --build
```

- Frontend: http://localhost:5173
- Backend: http://localhost:8000

4. **Inicialize o banco (se necessário):**

```bash
docker-compose exec backend flask db upgrade
```

---

## Como Usar

- **Treinar Modelo:** Envie relatórios na página "Treinar Modelo"
- **Análise Preditiva:** Preencha um desvio em "Análise Preditiva"
- **Assistente IA:** Faça perguntas na seção de chat
- **CDT Expert:** Envie um dossiê técnico em PDF e receba o checklist

---

## Licença

Este projeto é mantido por Samuel Mauli. Para uso interno e pesquisa.
