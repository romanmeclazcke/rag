from services.dependencies.llm_service import LlmService
from services.dependencies.qdrant_service import QDrantService
from schemas.llm import UserQuestion
from services.dependencies.embedding_service import EmbeddingService
from schemas.embedding import EmbeddingText
from schemas.llm import LlmQuestion

class RagService:
    
    def __init__(self, llm_service:LlmService, qdrant_service:QDrantService,embedding_service:EmbeddingService):
        self.llm_service = llm_service
        self.vector_store_service = qdrant_service
        self.embedding_service = embedding_service
        
        
    def answer_question(self, question: UserQuestion) -> str:
        questionEmbedding= self.embedding_service.generate_embedding(EmbeddingText(text=question.question))
        relevant_contexts = self.vector_store_service.get_similar_vectors(questionEmbedding, top_k=5)
        print(f"Contexto recuperados: {relevant_contexts}")
        
        llm_question = LlmQuestion(
            question=question.question,
            context=relevant_contexts
        )
        
        return self.llm_service.generate_response(llm_question)