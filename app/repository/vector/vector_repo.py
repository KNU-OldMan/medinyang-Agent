from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import uuid

from app.core.db import ChromaDBConnection


class VectorRepository(ABC):
    @abstractmethod
    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ):
        raise NotImplementedError

    @abstractmethod
    def query(
        self,
        query_embeddings: List[List[float]],
        n_results: int = 5,
        include: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def delete_documents(self, ids: List[str]):
        raise NotImplementedError

    @abstractmethod
    def get_collection_info(self) -> Dict[str, Any]:
        raise NotImplementedError


class ChromaDBRepository(VectorRepository):
    def __init__(self, collection_name: str | None = None):
        self._connection = ChromaDBConnection()
        self.collection = self._connection.get_collection(collection_name)

    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ):
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in documents]
        if metadatas is None:
            metadatas = [{"source": "manual"} for _ in documents]

        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )

    def query(self, query_embeddings, n_results=5, include=None):
        if include is None:
            include = ["documents", "metadatas", "distances"]  # ✅ ids 제거

        return self.collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            include=include,
        )

    def delete_documents(self, ids: List[str]):
        self.collection.delete(ids=ids)

    def get_collection_info(self) -> Dict[str, Any]:
        return {
            "name": self.collection.name,
            "count": self.collection.count(),
            "metadata": self.collection.metadata,
        }
