import os
from dotenv import load_dotenv
from langchain_community.utilities import GoogleSerperAPIWrapper

from app.repository.client.base import BaseSearchClient

# 로컬에서만 .env 로드
if os.getenv("KUBERNETES_SERVICE_HOST") is None:
    load_dotenv()


class SerperSearchClient(BaseSearchClient):
    def __init__(self):
        # SERPER_API_KEY는 GoogleSerperAPIWrapper가 환경변수에서 자동으로 읽음
        self._search = GoogleSerperAPIWrapper()

    def search(self, query: str) -> str:
        return self._search.run(query)
