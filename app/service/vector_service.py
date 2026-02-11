# app/service/vector_service.py
from __future__ import annotations

from typing import List, Dict, Any, Optional

from app.exceptions import KnowledgeBaseException
from app.models import MedicalQA
from app.service.embedding_service import EmbeddingService
from app.repository.vector.vector_repo import VectorRepository


class VectorService:
    def __init__(self, vector_repository: VectorRepository, embedding_service: EmbeddingService):
        self.vector_repository = vector_repository
        self.embedding_service = embedding_service

    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ):
        try:
            embeddings = self.embedding_service.create_embeddings(documents)
            self.vector_repository.add_documents(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids,
            )
        except Exception as e:
            raise KnowledgeBaseException(
                f"Failed to add documents: {str(e)}",
                details={"count": len(documents)},
            )

    def search(self, query: str, n_results: int = 5) -> List[MedicalQA]:
        try:
            query_embedding = self.embedding_service.create_embedding(query)
            results = self.vector_repository.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"],
            )

            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]
            dists = results.get("distances", [[]])[0]
            ids = results.get("ids", [[None] * len(docs)])[0]

            qa_list: List[MedicalQA] = []
            for doc, meta, dist, doc_id in zip(docs, metas, dists, ids):
                meta = meta or {}
                # 디버깅 편의용: distance를 metadata에 넣는 현재 정책 유지
                meta["distance"] = dist

                qa_list.append(
                    MedicalQA(
                        id=doc_id,
                        document=doc,
                        metadata=meta,
                    )
                )
            return qa_list

        except Exception as e:
            raise KnowledgeBaseException(
                f"Search failed: {str(e)}",
                details={"query": query, "n_results": n_results},
            )

    def delete_document(self, doc_id: str):
        try:
            self.vector_repository.delete_documents([doc_id])
        except Exception as e:
            raise KnowledgeBaseException(
                f"Failed to delete document: {str(e)}",
                details={"doc_id": doc_id},
            )

    def get_collection_info(self) -> Dict[str, Any]:
        try:
            return self.vector_repository.get_collection_info()
        except Exception as e:
            raise KnowledgeBaseException(f"Failed to get collection info: {str(e)}")


