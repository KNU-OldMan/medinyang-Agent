import os
from typing import Optional

import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv


# 로컬 개발 환경에서만 .env 로드
if os.getenv("KUBERNETES_SERVICE_HOST") is None:
    load_dotenv()


class ChromaDBConfig:
    def __init__(self):
        self.mode = os.getenv("CHROMA_MODE", "local")  # "local" or "server"
        self.host = os.getenv("CHROMA_HOST", "localhost")
        self.port = int(os.getenv("CHROMA_PORT", "8000"))
        self.persist_path = os.getenv("CHROMA_PERSIST_PATH", "./chroma_db")
        self.collection_name = os.getenv("CHROMA_COLLECTION_NAME", "medinyang_medical_knowledge")


class ChromaDBConnection:
    _instance: Optional["ChromaDBConnection"] = None
    _client: Optional[chromadb.ClientAPI] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            config = ChromaDBConfig()
            if config.mode == "server":
                self._client = chromadb.HttpClient(host=config.host, port=config.port)
            else:
                self._client = chromadb.PersistentClient(
                    path=config.persist_path,
                    settings=Settings(anonymized_telemetry=False),
                )

    @property
    def client(self) -> chromadb.ClientAPI:
        return self._client

    def get_collection(self, collection_name: str | None = None):
        config = ChromaDBConfig()
        name = collection_name or config.collection_name
        return self._client.get_or_create_collection(
            name=name,
            metadata={"description": "medinyang-Agent knowledge base (Upstage embeddings)"},
        )


def get_chroma_client() -> chromadb.ClientAPI:
    connection = ChromaDBConnection()
    return connection.client


def get_chroma_collection(collection_name: str | None = None):
    connection = ChromaDBConnection()
    return connection.get_collection(collection_name)
