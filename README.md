# medinyang-Agent

**medinyang-Agent**는 의료/건강 관련 질문에 대해 **근거 기반(RAG)** 으로 답변을 제공하는 **멀티에이전트 의료 상담 시스템**입니다.  
Upstage Solar LLM과 ChromaDB(Vector DB)를 기반으로 내부 지식 검색을 우선 수행하며, 필요 시 외부 검색을 통해 지식을 확장하는 구조를 가집니다.

또한 사용자가 업로드한 **처방전/건강검진 기록지**를 OCR(또는 Vision 모델)로 분석하여 저장하고, 개인 건강 기록 기반 질의응답으로 확장 가능한 구조로 설계됩니다.

> ⚠️ **주의(Disclaimer)**  
> 본 프로젝트는 의료 진단을 제공하지 않습니다.  
> 출력 결과는 참고용 정보이며, 정확한 진단 및 치료는 반드시 의료 전문가(의사/약사)와 상담해야 합니다.

---

## 주요 기능 (Key Features)

### 1) 의료 상담 멀티에이전트 (RAG 기반)
- 내부 의료 지식(Vector DB) 기반 검색 후 답변 생성
- 검색된 정보가 부족하면 외부 검색을 통해 지식 보강 가능
- 안전한 답변 생성을 위한 가이드라인 포함
  - 확정 진단 금지
  - 응급상황(레드플래그) 안내
  - 의료진 상담 권고

### 2) 개인 건강 문서 업로드 및 기록 관리 (향후 확장)
- 처방전 / 건강검진 기록지 업로드
- OCR/Vision 기반 텍스트 추출 및 구조화
- 사용자 개인 기록 DB에 저장하여 히스토리 관리
- 추후 개인 기록 기반 RAG(QA) 기능으로 확장 예정

---

## 시스템 아키텍처 개요

### MVP(1차 목표)
- Upstage Solar(Chat Model) 기반 답변 생성
- Upstage Embedding 기반 임베딩 생성
- ChromaDB 기반 의료 지식 벡터 저장소 구축
- AI HUB 필수의료 의학지식 데이터를 기반으로 Knowledge Base 구축
- LangGraph 기반 멀티에이전트 오케스트레이션

---

## 멀티에이전트 구조 (Multi-Agent Workflow)

본 프로젝트는 역할 기반으로 분리된 3개의 하위 에이전트(Sub-Agent)와 이를 조율하는 Super Graph 구조를 가집니다.

### 1) Info Extractor Agent (내부 검색 담당)
- 내부 Vector DB에서 관련 의료 정보를 검색
- 검색된 정보가 질문에 충분한지 검증(Verify)

### 2) Knowledge Augmentor Agent (외부 검색 및 지식 확장 담당)
- 내부 지식이 부족하면 외부 검색(Serper/Google Search) 수행
- 유용한 정보를 내부 Vector DB에 저장(옵션)

### 3) Answer Generator Agent (최종 답변 생성 담당)
- 검색된 context를 기반으로 사용자에게 친절한 의료 상담 답변 생성
- 공감(Empathy) + 안전 가이드라인 포함

---

## 기술 스택 (Tech Stack)
- Python 3.10+
- FastAPI
- LangChain / LangGraph
- ChromaDB (Vector Database)
- Upstage Solar LLM (Chat)
- Upstage Embeddings (Embedding Model)
- OCR/Vision (추후 적용 예정)

---

## 지식 데이터셋 (Knowledge Base)
- **AI HUB 필수의료 의학지식 데이터**
- 처리 방식(MVP)
  - 데이터 정제 → Chunking → Embedding → ChromaDB 저장
  - metadata 기반 카테고리/출처/태그 관리

---

## 실행 방법 (Getting Started)

### 1) 가상환경 생성 및 설치
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
