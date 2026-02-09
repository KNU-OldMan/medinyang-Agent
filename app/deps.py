from fastapi import Depends

from app.repository.vector.vector_repo import VectorRepository, ChromaDBRepository
from app.service.embedding_service import EmbeddingService
from app.service.vector_service import VectorService
from app.service.agents.info_extractor_service import InfoExtractorService
from app.service.agents.knowledge_augmentor_service import KnowledgeAugmentorService


def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()


def get_vector_repository() -> VectorRepository:
    return ChromaDBRepository()


def get_vector_service(
    vector_repo: VectorRepository = Depends(get_vector_repository),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
) -> VectorService:
    return VectorService(vector_repository=vector_repo, embedding_service=embedding_service)

def build_vector_service() -> VectorService:
    # FastAPI Depends 없이 수동 생성 (CLI/스크립트/테스트 용)
    return VectorService(
        vector_repository=ChromaDBRepository(),
        embedding_service=EmbeddingService(),
    )

def get_info_extractor_service() -> InfoExtractorService:
    return InfoExtractorService()

def get_knowledge_augmentor_service() -> KnowledgeAugmentorService:
    return KnowledgeAugmentorService()