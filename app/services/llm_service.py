from ollama import Client, ChatResponse
from schemas.llm import LlmQuestion
from fastapi import HTTPException
import os

class LlmService: 
    def __init__(self, ollama_client: Client):
        self.ollama_client = ollama_client

    def generate_response(self, question: LlmQuestion) -> str:
        """Genera una respuesta basada en la pregunta y el contexto proporcionado."""
        try:
            context_text = ""
            if question.context and len(question.context) > 0:
                context_text = "\n".join(
                    f"- {chunk}" for chunk in question.context
                )

            #  Prompt final
            prompt = f"""
            Responde (directamente, sin frases introductorias ni explicaciones sobre tu rol) a la siguiente pregunta usando tu propio conocimiento.
            Si el contexto adicional dado es útil o relevante, puedes usarlo; si no, ignóralo.

            Contexto (opcional):
            {context_text if context_text else "No se proporcionó contexto."}
            Pregunta:
            {question.question}
            """

            # Mando Request al modelo
            response:ChatResponse = self.ollama_client.generate(
                model=os.getenv("CHAT_MODEL"), 
                prompt=prompt
            )

            return response["response"]

        except Exception as e:
            print(f"Error al generar respuesta del LLM: {e}")
            raise RuntimeError("No se pudo generar una respuesta del modelo.")

