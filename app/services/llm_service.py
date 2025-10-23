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
            Instrucciones:
            1. Usa la información del contexto ÚNICAMENTE si sirve para responder correctamente.
            2. Si el contexto no sirve, responde con tu conocimiento general.
            3. Nunca menciones el contexto ni digas que no hay información en él.

            Contexto (si es útil):
            {context_text if context_text else "No se proporcionó contexto."}
            Pregunta del usuario: 
            {question.question}
            """

            print("=== CONTEXTO ===")
            print(context_text[:500])

            # Mando Request al modelo
            response:ChatResponse = self.ollama_client.generate(
                model=os.getenv("CHAT_MODEL"), 
                prompt=prompt
            )

            return response["response"]

        except Exception as e:
            print(f"Error al generar respuesta del LLM: {e}")
            raise RuntimeError("No se pudo generar una respuesta del modelo.")

