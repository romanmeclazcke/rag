# Chat RAG 
Asistente conversacional que responde preguntas combinando información de documentos subidos (PDF, TXT o DOCX) y conocimiento general

## Tecnologías principales
- **FastAPI** — Backend principal (API y lógica RAG)
- **Streamlit** — Interfaz web del chat
- **Qdrant** — Base vectorial para embeddings
- **Ollama** — Modelos LLM locales (Llama3)
- **PostgreSQL** — Base de datos relacional para usuarios y chats
- **Docker Compose** — Orquestación de servicios

## Requisitos previos
- **Docker** y **Docker Compose**
- **Ollama** instalado localmente

## Modelo requerido
Este proyecto usa el modelo `llama3:instruct` de Ollama.
Ejecutá este comando una vez en tu máquina local **antes de levantar los contenedores**:
```bash
ollama pull llama3:instruct
