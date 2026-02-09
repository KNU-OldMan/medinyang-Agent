from abc import ABC, abstractmethod


class BaseLLMClient(ABC):
    @abstractmethod
    def get_chat_model(self):
        raise NotImplementedError

    @abstractmethod
    def get_embedding_model(self):
        raise NotImplementedError


class BaseSearchClient(ABC):
    @abstractmethod
    def search(self, query: str) -> str:
        """검색 쿼리를 받아 문자열 형태의 결과를 반환"""
        raise NotImplementedError
