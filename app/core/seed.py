from __future__ import annotations

import os
import json
import logging
import zipfile
import unicodedata
from pathlib import Path
from typing import Iterator, Dict, Any, List, Optional

import gdown

from app.models import MedicalQA
from app.repository.vector.vector_repo import ChromaDBRepository
from app.service.embedding_service import EmbeddingService
from app.service.vector_service import VectorService
from app.exceptions import KnowledgeBaseException

logger = logging.getLogger("seed")


class SeedManager:
    """
    의료 데이터 다운로드 및 벡터 DB 시딩을 담당하는 매니저 클래스

    - SEED_URL: gdown으로 받을 수 있는 URL(구글 드라이브 share 링크 또는 파일 id 기반 url)
    - resources/의료데이터.zip 을 다운로드 후 resources/의료데이터/ 아래에 json들 존재한다고 가정
    - logs/seed_status.json 으로 진행률 노출
    """

    def __init__(
        self,
        seed_status_file: Path = Path("logs/seed_status.json"),
        resource_dir: Path = Path("resources"),
        data_dir_name: str = "의료데이터",
        zip_name: str = "의료데이터.zip",
        batch_size: int = 100,
    ):
        self.seed_status_file = seed_status_file
        self.resource_dir = resource_dir
        self.data_dir = self.resource_dir / data_dir_name
        self.zip_path = self.resource_dir / zip_name
        self.seed_url = os.getenv("SEED_URL")
        self.batch_size = batch_size

        # 서비스 초기화 (VectorService + ChromaDB + Embedding)
        # FastAPI Depends 없이 "직접 생성" (seed는 서버 부팅/CLI에서도 돌아야 함)
        self.vector_service = VectorService(
            vector_repository=ChromaDBRepository(),
            embedding_service=EmbeddingService(),
        )

        # 상태 파일 디렉토리 보장
        self.seed_status_file.parent.mkdir(parents=True, exist_ok=True)
        self.resource_dir.mkdir(parents=True, exist_ok=True)

    def get_status(self) -> Dict[str, Any]:
        """현재 시딩 상태를 반환합니다 (UI 표시용)."""
        if not self.seed_status_file.exists():
            return {"status": "not_started", "current": 0, "total": 0, "message": "Ready"}

        try:
            with open(self.seed_status_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            return {"status": "error", "current": 0, "total": 0, "message": str(e)}

    def _update_status(self, status: str, current: int = 0, total: int = 0, message: str = ""):
        """상태 파일 업데이트 (내부용)"""
        try:
            payload = {"status": status, "current": current, "total": total, "message": message}
            with open(self.seed_status_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to update status: {e}")

    def _download_and_extract(self):
        """데이터 다운로드 및 압축 해제 + 한글 파일명 인코딩 보정"""
        # 1) 다운로드
        if not self.zip_path.exists():
            if not self.seed_url:
                raise ValueError("SEED_URL environment variable is not set.")
            logger.info("Downloading seed zip...")
            self._update_status("in_progress", 0, 0, "Downloading seed zip...")
            gdown.download(self.seed_url, str(self.zip_path), quiet=False)

        # 2) 압축 해제 (한글 파일명 보정)
        logger.info(f"Extracting {self.zip_path}...")
        self._update_status("in_progress", 0, 0, "Extracting seed zip...")

        with zipfile.ZipFile(self.zip_path, "r") as zip_ref:
            for file_info in zip_ref.infolist():
                # cp437 -> cp949 -> NFC 정규화
                try:
                    filename = file_info.filename.encode("cp437").decode("cp949")
                except Exception:
                    filename = file_info.filename
                filename = unicodedata.normalize("NFC", filename)

                target_path = self.resource_dir / filename
                if file_info.is_dir():
                    target_path.mkdir(parents=True, exist_ok=True)
                    continue

                target_path.parent.mkdir(parents=True, exist_ok=True)
                with zip_ref.open(file_info) as source, open(target_path, "wb") as target:
                    target.write(source.read())

        # 3) 폴더명 후처리 (압축 구조가 의료데이터/가 아닐 수도 있어서 1차 보정)
        if not self.data_dir.exists():
            extracted_dirs = [d for d in self.resource_dir.iterdir() if d.is_dir() and d.name != "__MACOSX"]
            if extracted_dirs:
                candidate = extracted_dirs[0]
                logger.info(f"Renaming {candidate.name} -> {self.data_dir.name}")
                candidate.rename(self.data_dir)

        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory not found after extraction: {self.data_dir}")

    def _iter_json_files(self) -> Iterator[Path]:
        if not self.data_dir.exists():
            self._download_and_extract()
        yield from self.data_dir.rglob("*.json")

    def _count_total_docs(self) -> int:
        """총 문서 수를 '파일 수'로 계산 (메모리 아끼기)"""
        return sum(1 for _ in self._iter_json_files())

    def _load_documents_generator(self) -> Iterator[MedicalQA]:
        """JSON 파일을 읽어 MedicalQA를 하나씩 반환 (메모리 절약)"""
        for file_path in self._iter_json_files():
            try:
                with open(file_path, "r", encoding="utf-8-sig") as f:
                    data = json.load(f)

                # 문서 포맷(Q/A)
                question = (data.get("question") or "").strip()
                answer = (data.get("answer") or "").strip()
                document = f"Q: {question}\nA: {answer}"

                # 메타데이터
                domain = data.get("domain", "N/A")
                q_type = data.get("q_type", "N/A")

                qa_id = data.get("qa_id") or file_path.stem
                doc_id = f"medical_{qa_id}"

                yield MedicalQA(
                    id=doc_id,
                    document=document,
                    metadata={
                        "source": "seed",
                        "domain": domain,
                        "q_type": q_type,
                        "file": str(file_path),
                    },
                )

            except Exception as e:
                logger.error(f"Error parsing {file_path}: {e}")
                continue

    def run(self):
        """
        시딩 메인 실행
        - DB 문서 수 >= 파일 수면 스킵
        - 배치(batch_size) 단위로 스트리밍 적재
        """
        try:
            self._update_status("in_progress", 0, 0, "Checking seed files...")

            total_docs = self._count_total_docs()
            if total_docs == 0:
                self._update_status("completed", 0, 0, "No data files found.")
                return

            # DB 상태 확인
            info = self.vector_service.get_collection_info()
            current_db_count = int(info.get("count", 0))

            if current_db_count >= total_docs:
                logger.info(f"Skipping seeding (DB: {current_db_count} >= Files: {total_docs})")
                self._update_status("completed", current_db_count, total_docs, "Already seeded.")
                return

            self._update_status("in_progress", current_db_count, total_docs, "Seeding vectors...")

            batch_docs: List[str] = []
            batch_metas: List[Dict[str, Any]] = []
            batch_ids: List[str] = []

            current = 0
            for qa in self._load_documents_generator():
                batch_docs.append(qa.document)
                batch_metas.append(qa.metadata)
                batch_ids.append(qa.id or "")

                if len(batch_docs) >= self.batch_size:
                    self.vector_service.add_documents(
                        documents=batch_docs,
                        metadatas=batch_metas,
                        ids=batch_ids,
                    )
                    current += len(batch_docs)
                    pct = int((current / total_docs) * 100)
                    self._update_status("in_progress", current, total_docs, f"Seeding... {pct}%")
                    logger.info(f"Seeded {current}/{total_docs}")

                    batch_docs, batch_metas, batch_ids = [], [], []

            # 마지막 잔여 배치
            if batch_docs:
                self.vector_service.add_documents(
                    documents=batch_docs,
                    metadatas=batch_metas,
                    ids=batch_ids,
                )
                current += len(batch_docs)

            self._update_status("completed", current, total_docs, "Seeding completed.")
            logger.info("Seeding completed.")

        except KnowledgeBaseException as e:
            logger.exception("Seeding failed (KnowledgeBaseException)")
            self._update_status("error", 0, 0, f"{e.message}")
            raise
        except Exception as e:
            logger.exception("Seeding failed")
            self._update_status("error", 0, 0, str(e))
            raise


# 싱글톤 인스턴스
seed_manager = SeedManager()


def get_seed_status() -> Dict[str, Any]:
    return seed_manager.get_status()


def seed_data_if_empty():
    seed_manager.run()
