from fastapi import Depends
from dependencies.ollama_client import get_ollama_client
from services.llm_service import LlmService

def get_llm_service(ollama_client=Depends(get_ollama_client)):
    return LlmService(ollama_client)