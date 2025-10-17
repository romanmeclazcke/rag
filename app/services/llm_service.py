from ollama import Client, ChatResponse
from schemas.llm import LlmQuestion
from fastapi import HTTPException
from core.config import CHAT_MODEL
class LlmService: 
    
    def __init__(self, ollama_client: Client):
        self.ollama_client = ollama_client


    def generate_response(self, question: LlmQuestion) -> str:
        """
        Genera una respuesta basada en la pregunta y el contexto proporcionado.
        """
        try:
            context_text = ""
            if question.context and len(question.context) > 0:
                context_text = "\n".join(
                    f"- {chunk}" for chunk in question.context
                )

            #  Prompt final
            prompt = f"""
            Usa el siguiente contexto para responder la pregunta del usuario.

            Contexto:
            {context_text if context_text else "No se proporcionó contexto."}

            Pregunta:
            {question.question}

            Si la respuesta no está claramente en el contexto, responde "No tengo suficiente información para responder".
            """

            # Mando Request al modelo
            response:ChatResponse = self.ollama_client.chat(
                model=CHAT_MODEL, 
                messages=[
                    {"role": "system", "content": "Eres un asistente útil que responde basado en el contexto."},
                    {"role": "user", "content": prompt}
                ]
            )

            return response.message.content  if response.message.content else "No tengo suficiente información para responder."

        except Exception as e:
            print(f"Error al generar respuesta del LLM: {e}")
            raise RuntimeError("No se pudo generar una respuesta del modelo.")

