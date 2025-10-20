from ollama import Client, ResponseError
from fastapi import Depends
import os

def get_ollama_client():
    """
    Devuelve una instancia inicializada del cliente de Ollama.
    Si el modelo no está disponible localmente, lo descarga.
    """
    client = Client(host=os.getenv("OLLAMA_HOST"))
    try:
        client.show(os.getenv("CHAT_MODEL"))
    except ResponseError as e:  # type: ignore
        if e.status_code == 404:
            print(f"Model '{os.getenv('EMBEDDING_MODEL')}' not found, pulling it. This may take a moment...")
            client.pull(os.getenv("EMBEDDING_MODEL"))
            print(f"Model '{os.getenv('EMBEDDING_MODEL')}' pulled successfully.")
    return client