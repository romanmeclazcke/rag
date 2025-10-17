from ollama import Client, ResponseError
from fastapi import Depends
from core.config import OLLAMA_HOST, CHAT_MODEL, EMBEDDING_MODEL

def get_ollama_client():
    """
    Devuelve una instancia inicializada del cliente de Ollama.
    Si el modelo no está disponible localmente, lo descarga.
    """
    client = Client(host=OLLAMA_HOST)
    try:
        client.show(CHAT_MODEL)
    except ResponseError as e:  # type: ignore
        if e.status_code == 404:
            print(f"Model '{EMBEDDING_MODEL}' not found, pulling it. This may take a moment...")
            client.pull(EMBEDDING_MODEL)
            print(f"Model '{EMBEDDING_MODEL}' pulled successfully.")
    return client