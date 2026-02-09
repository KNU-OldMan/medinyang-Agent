import os
from dotenv import load_dotenv
from langchain_upstage import ChatUpstage, UpstageEmbeddings

from app.repository.client.base import BaseLLMClient

# 로컬 개발 환경에서만 .env 로드
if os.getenv("KUBERNETES_SERVICE_HOST") is None:
    load_dotenv()


class UpstageClient(BaseLLMClient):
    def __init__(self):
        self.api_key = os.getenv("UPSTAGE_API_KEY")
        if not self.api_key:
            raise ValueError("UPSTAGE_API_KEY is required. Please set it in .env or env vars.")

        self.chat_model_name = os.getenv("UPSTAGE_CHAT_MODEL", "solar-pro2")
        self.embedding_model_name = os.getenv("UPSTAGE_EMBEDDING_MODEL", "solar-embedding-1-large")

        self._chat_instance: ChatUpstage | None = None
        self._embedding_instance: UpstageEmbeddings | None = None

    def get_chat_model(self) -> ChatUpstage:
        if self._chat_instance is None:
            self._chat_instance = ChatUpstage(
                api_key=self.api_key,
                model=self.chat_model_name,
            )
        return self._chat_instance

    def get_embedding_model(self) -> UpstageEmbeddings:
        if self._embedding_instance is None:
            self._embedding_instance = UpstageEmbeddings(
                api_key=self.api_key,
                model=self.embedding_model_name,
            )
        return self._embedding_instance
