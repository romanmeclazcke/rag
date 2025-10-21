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
            context_text = "\n".join(f"- {chunk}" for chunk in question.context) if question.context else "No se proporcionó contexto."
            conversation_text = "\n".join(f"{role}: {content}" for role, content in zip(["User", "Assistant"] * (len(question.conversation)//2 + 1), question.conversation))

            #  Prompt final
            prompt = f"""
            Eres un asistente experto y tus respuestas deben basarse *principalmente* en el contexto proporcionado abajo.
            Si la información relevante se encuentra en el contexto, úsala textualmente. 
            Solo si el contexto no contiene la respuesta, puedes usar tu conocimiento general.

            ### HISTORIAL DE CONVERSACIÓN ###
            {conversation_text or "No hay mensajes previos."}
            ### CONTEXTO RELEVANTE ###  
            {context_text if context_text else "No se proporcionó contexto."}
            ### NUEVA PREGUNTA ###
            {question.question}

            Responde en el idioma del usuario, de manera clara, concisa y precisa.
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

