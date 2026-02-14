# 🏥 medinyang-Agent 프로젝트 설명 

**대상 청중**: 프로젝트를 처음 보는 팀원들  
**시간**: 약 20-30분  
**난이도**: 초급~중급 (기술 배경 필요)

---

## 📌 1부: 프로젝트 개요 (3분)

### 🎯 핵심 목표
안녕하세요! 지금부터 설명할 프로젝트는 **"medinyang-Agent"**라고 하는 **의료/건강 상담 AI 에이전트** 입니다.

**간단히 말하면:**
- 사용자가 "감기 걸렸을 때 어떻게 해야 해?" 라고 물으면
- AI가 근거 있는 정보를 기반으로 친절한 답변을 제공합니다

**핵심 특징 3가지:**
1. **RAG 기반 답변** (Retrieval-Augmented Generation)
   - 내부 의료 지식 데이터베이스에서 먼저 검색
   - 부족하면 외부 인터넷 검색으로 보강

2. **안전한 의료 상담**
   - "이것은 의료 진단이 아닙니다" 명시
   - 응급상황은 병원 가도록 안내
   - 의사 상담 권고

3. **멀티에이전트 시스템**
   - 3개의 전문 에이전트가 각자의 역할 수행
   - 마치 의료팀처럼 협력하는 구조

### ⚠️ 중요한 주의사항
> **이것은 의료 진단 도구가 아닙니다!**  
> 본 시스템은 정보 제공용이며, 정확한 진단과 치료는 반드시 의료 전문가와 상담해야 합니다.

---

## 📚 2부: 기술 스택 (2분)

### 사용된 주요 기술들

```
┌─────────────────────────────────────────────┐
│      Frontend / API Layer                   │
│  ├─ FastAPI (웹 서버 프레임워크)             │
│  └─ REST API (챗 인터페이스)                │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│      Business Logic (에이전트 로직)          │
│  ├─ LangChain (LLM 통합 프레임워크)          │
│  ├─ LangGraph (멀티에이전트 오케스트레이션)   │
│  └─ Python 3.10+                           │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│      AI Model (생각의 엔진)                   │
│  ├─ Upstage Solar LLM (답변 생성)            │
│  └─ Upstage Embeddings (의미 검색)          │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│      Data Layer (지식 저장소)                 │
│  ├─ ChromaDB (벡터 데이터베이스)             │
│  └─ AI HUB 의료 데이터셋                     │
└─────────────────────────────────────────────┘
```

### 왜 이 기술들을 선택했을까?

**FastAPI**
- 빠르고 현대적인 웹 프레임워크
- 자동 API 문서 생성 (Swagger UI)
- 비동기 처리 지원

**LangChain + LangGraph**
- LLM을 쉽게 연결
- 복잡한 워크플로우 구성 (에이전트 체인)
- 도구 호출(Tool Calling) 지원

**Upstage Solar**
- 한국형 LLM (한글 이해력 좋음)
- 의료 특화 모델 버전 존재
- 저렴한 API 비용

**ChromaDB**
- 가볍고 빠른 벡터 데이터베이스
- 로컬에서도 동작 가능
- 의미 기반 검색 지원

---

## 🎭 3부: 멀티에이전트 아키텍처 (8분)

### 전체 흐름도

```
사용자 질문
    ↓
┌──────────────────────────────────────┐
│  Super Graph (마스터 조율)             │
│                                       │
│  ┌─────────────────────────────────┐│
│  │ Step 1: Info Extractor Agent     ││
│  │ (내부 지식 검색)                  ││
│  └──────┬──────────────────────────┘│
│         ↓                            │
│  ├─ 충분한 정보? YES → Step 3으로   │
│  │                    SKIP Step 2   │
│  └─ 충분한 정보? NO  → Step 2로     │
│         ↓                            │
│  ┌─────────────────────────────────┐│
│  │ Step 2: Knowledge Augmentor      ││
│  │ (외부 검색으로 지식 보강)         ││
│  └──────┬──────────────────────────┘│
│         ↓                            │
│  ┌─────────────────────────────────┐│
│  │ Step 3: Answer Generator Agent   ││
│  │ (최종 답변 생성)                  ││
│  └──────┬──────────────────────────┘│
└─────────┼──────────────────────────┘
          ↓
       최종 답변
```

### 🤖 Agent #1: Info Extractor (정보 추출 에이전트)

**역할**: 내부 의료 데이터베이스에서 관련 정보 검색

**동작 과정:**
```
사용자 질문: "감기 걸렸을 때 어떻게 해야 해?"
    ↓
LLM이 질문을 분석하고 검색 쿼리 생성
    ↓
ChromaDB에서 유사한 문서 검색
    ↓
LLM이 검색된 정보가 충분한지 검증 (Verifier)
    ↓
결과: {status: "success" 또는 "insufficient"}
```

**실제 코드 구조:**
- `InfoExtractorService` (wrapper)
- `info_extractor.py` (LangGraph 서브그래프)
  - Retriever 노드: 벡터 검색 실행
  - Verifier 노드: 정보 충분성 검증

**검색 예시:**
```
질문: "감기 증상이 뭐에요?"
↓
검색어: "감기", "cold", "respiratory infection"
↓
찾은 문서들:
  1. "감기의 주요 증상: 콧물, 기침, 인후통..."
  2. "감기의 원인: 바이러스 감염..."
  3. "감기와 독감의 차이점..."
↓
Verifier: "이 정보면 충분합니다!" → success
```

---

### 🤖 Agent #2: Knowledge Augmentor (지식 보강 에이전트)

**역할**: Info Extractor의 검색 결과가 부족하면, 외부 인터넷에서 추가 정보 검색

**언제 작동하나?**
- Info Extractor가 "insufficient" 상태 반환
- 예: "희귀병에 대해 알려줘" → 내부 데이터에 없음 → 외부 검색 필요

**동작 과정:**
```
"충분한 정보가 없습니다" 신호 수신
    ↓
Google Search API (Serper) 호출
    ↓
인터넷에서 관련 논문/뉴스/블로그 검색
    ↓
신뢰할 수 있는 출처 필터링 (의료기관, 학술지 우선)
    ↓
검색 결과를 내부 DB에 임시 저장 (선택)
    ↓
다음 단계로 전달
```

**특징:**
- 외부 검색이지만 의료 신뢰성 고려
- 검색 결과를 로깅하여 추적 가능
- 사용자는 어디서 정보를 얻었는지 알 수 있음

---

### 🤖 Agent #3: Answer Generator (답변 생성 에이전트)

**역할**: 수집한 정보를 기반으로 최종 답변을 만드는 의료 상담사

**동작 과정:**
```
수집된 모든 정보 (internal + external)
    ↓
LLM에게 답변 생성 프롬프트 전달:
  "다음 정보를 기반으로 친절하고 안전한 의료 상담 답변을 만들어줘.
   - 이것은 진단이 아니라는 것을 명시
   - 응급상황이면 병원 가야한다고 강조
   - 의사 상담을 권고"
    ↓
LLM 답변 생성
    ↓
최종 답변 + 참고 출처 반환
```

**답변 안전 가이드라인:**
```
✗ 절대 금지:
  - "당신은 OO병입니다" (진단 금지)
  - "이 약을 꼭 먹어야 합니다" (약물 지시 금지)

✓ 허용:
  - "일반적으로 이런 증상은..."
  - "의사와 상담해보세요"
  - "응급실에 가시는 것이 좋습니다"
```

**실제 답변 예:**
```
Q: "감기 걸렸을 때 어떻게 해야 해?"

A: 감기는 일반적으로 바이러스 감염으로 인한 호흡기 질환입니다.

일반적인 대처 방법:
1. 충분한 휴식 (하루 7-8시간 수면)
2. 수분 섭취 (하루 2-3리터)
3. 따뜻한 음식 (국, 죽)
4. 습도 관리 (50-60% 습도)

증상이 심하거나 1주일 이상 지속되면 반드시 의사와 상담하세요.

⚠️ 다음 증상이 있으면 응급실로 가세요:
- 고열 (38도 이상)
- 호흡 곤란
- 가슴 통증

본 정보는 참고용이며, 정확한 진단은 의료 전문가와 상담해야 합니다.
```

---

### 🔄 에이전트들이 협력하는 모습

```
사용자: "감기 걸렸어. 어떻게 해야 해?"

[Info Extractor 작동]
└─ ChromaDB 검색
   └─ "감기의 증상, 치료법, 예방법" 문서 10개 검색
   └─ Verifier: "충분합니다!" (success)

[Knowledge Augmentor 스킵]
(Info Extractor가 이미 충분한 정보 찾음)

[Answer Generator 작동]
└─ 수집된 정보 기반 답변 생성
└─ "감기는 일반적으로... 의사와 상담하세요"

최종 답변 반환
```

---

## 🗄️ 4부: 데이터 구조 (5분)

### 벡터 데이터베이스 (ChromaDB) 구조

**문제: 일반 검색은 왜 안 될까?**

```
일반 검색:
검색어: "감기"
결과: 정확히 "감기"라는 단어가 들어간 문서만 검색
문제: 의미가 비슷하지만 다른 단어("cold", "감기증상")는 못 찾음

벡터 검색 (의미 기반):
검색어: "감기" → 벡터값으로 변환 → [0.2, -0.5, 0.8, ...]
DB의 모든 문서를 벡터값으로 변환
    ↓
의미적으로 가까운 문서 찾기
결과: "추운 날씨에 감기 걸렸어요", "감기증상 알아보기" 등 모두 검색
```

### Embedding(임베딩)이란?

```
텍스트 → Upstage Embedding 모델 → 수백 차원의 숫자 배열
                            
"감기"        → [0.2, -0.5, 0.8, 0.1, -0.3, ...]
"cold"        → [0.18, -0.52, 0.75, 0.12, -0.28, ...]
"독감"        → [0.3, -0.4, 0.7, 0.0, -0.2, ...]

거리 계산 (Cosine Similarity):
"감기" vs "cold" = 0.98 (매우 가까움!)
"감기" vs "독감"  = 0.95 (가까움)
"감기" vs "파스타" = 0.02 (멀음)
```

### 의료 데이터셋 (AI HUB)

**구성:**
- 필수 의료 지식 데이터: 약 500개 JSON 파일
- 각 파일: 의료 상황 + 답변 쌍
- 메타데이터: 카테고리, 출처, 신뢰도

**예시 파일:**
```json
{
  "필수_2136.json": {
    "질문": "감기에 걸리면 항생제를 먹어야 하나요?",
    "답변": "감기는 바이러스 감염이므로 항생제가 효과가 없습니다...",
    "카테고리": "감염질환",
    "신뢰도": "high",
    "출처": "대한의학협회"
  }
}
```

**시딩 과정 (초기화):**
```
프로젝트 시작
    ↓
seed.py 스크립트 실행
    ↓
resources/의료데이터/ 폴더 읽음
    ↓
각 JSON 파일 로드
    ↓
Chunking (긴 문서를 작은 단위로 나눔)
    ↓
Embedding 생성
    ↓
ChromaDB에 저장
    ↓
"Data seeding complete!" (로그)
```

---

## 🔌 5부: API 엔드포인트 (4분)

### REST API 구조

**기본 URL**: `http://127.0.0.1:8001`

### 엔드포인트 1️⃣: 헬스 체크
```
GET /agent/health

응답:
{
  "status": "healthy",
  "message": "Agent service is running"
}

용도: 서버가 정상 작동하는지 확인
```

### 엔드포인트 2️⃣: 채팅 (일반 모드)
```
POST /agent/chat

요청:
{
  "query": "감기 걸렸을 때 어떻게 해야 해?",
  "session_id": "user123"
}

응답:
{
  "answer": "감기는 일반적으로... [full answer]",
  "user_query": "감기 걸렸을 때 어떻게 해야 해?",
  "process_status": "success",
  "loop_count": 1
}

특징:
- 동기식 (sync)
- 답변을 다 만들 때까지 기다림
- 모든 과정이 끝난 후 한 번에 반환
- 테스트나 간단한 사용에 좋음
```

### 엔드포인트 3️⃣: 채팅 (스트리밍 모드)
```
POST /agent/chat/stream

요청: (동일)
{
  "query": "감기 걸렸을 때 어떻게 해야 해?",
  "session_id": "user123"
}

응답: (실시간 스트림)
event: log
data: {"step": "Step 1: Info Extractor 시작", "timestamp": "2026-02-14T10:00:00"}

event: log
data: {"step": "Step 1 완료 (충분한 정보 찾음)", "timestamp": "2026-02-14T10:00:05"}

event: token
data: {"content": "감기는", "timestamp": "2026-02-14T10:00:06"}

event: token
data: {"content": " 바이러스", "timestamp": "2026-02-14T10:00:07"}
...

특징:
- 비동기식 (async)
- 과정을 실시간으로 볼 수 있음 (로그)
- 답변을 토큰 단위로 스트리밍 (실시간 타이핑 효과)
- 사용자 경험 좋음
```

### 엔드포인트 4️⃣: 시딩 상태 확인
```
GET /agent/seed-status

응답:
{
  "status": "complete",
  "total_documents": 500,
  "indexed_documents": 500,
  "last_update": "2026-02-14T08:00:00"
}

용도: 의료 데이터가 얼마나 로드되었는지 확인
```

### 엔드포인트 5️⃣: 지식 추가
```
POST /agent/knowledge/add

요청:
{
  "documents": ["감기의 새로운 치료법...", "독감과의 차이..."],
  "metadatas": [
    {"source": "의학논문", "year": 2024},
    {"source": "의학논문", "year": 2024}
  ]
}

응답:
{
  "status": "success",
  "message": "Added 2 documents to knowledge base"
}

용도: 실시간으로 의료 지식 추가
```

### 엔드포인트 6️⃣: 통계 조회
```
GET /agent/knowledge/stats

응답:
{
  "collection_name": "medical_qa",
  "total_documents": 500,
  "last_updated": "2026-02-14T08:00:00"
}

용도: 현재 저장된 의료 지식 규모 확인
```

---

## 📁 6부: 프로젝트 파일 구조 (4분)

### 전체 디렉토리 트리

```
medinyang-Agent/
├── app/                          # 메인 애플리케이션
│   ├── main.py                   # FastAPI 앱 진입점
│   │   └─ 앱 시작/종료, 예외 처리, 미들웨어
│   │
│   ├── deps.py                   # 의존성 주입 (DI)
│   │   └─ VectorService, AgentService 등 인스턴스 생성
│   │
│   ├── exceptions.py             # 커스텀 예외
│   │   └─ AgentException, KnowledgeBaseException, ValidationException
│   │
│   ├── api/
│   │   └── routes/
│   │       └── agent_routers.py  # API 엔드포인트 정의
│   │           └─ /agent/chat, /agent/chat/stream, /agent/health 등
│   │
│   ├── agents/                   # 멀티에이전트 로직
│   │   ├── state.py              # 상태 정의 (StateGraph용)
│   │   ├── workflow.py           # Super Graph (메인 워크플로우)
│   │   ├── tools.py              # 에이전트가 사용할 도구들
│   │   ├── utils.py              # 유틸리티 함수
│   │   └── subgraphs/
│   │       ├── info_extractor.py     # Agent #1: 정보 검색
│   │       ├── knowledge_augmentor.py # Agent #2: 지식 보강
│   │       └── answer_gen.py         # Agent #3: 답변 생성
│   │
│   ├── service/                  # 비즈니스 로직 (서비스층)
│   │   ├── agent_service.py      # 에이전트 조율
│   │   ├── vector_service.py     # 벡터 DB 작업
│   │   ├── embedding_service.py  # Embedding 생성
│   │   └── agents/
│   │       ├── info_extractor_service.py
│   │       ├── knowledge_augmentor_service.py
│   │       └── answer_gen_service.py
│   │
│   ├── repository/               # 데이터 접근층 (DAO)
│   │   ├── vector/
│   │   │   └── vector_repo.py    # ChromaDB 직접 접근
│   │   └── client/
│   │
│   ├── core/                     # 핵심 설정
│   │   ├── llm.py                # LLM 클라이언트 설정
│   │   ├── db.py                 # ChromaDB 연결
│   │   ├── logger.py             # 로깅 설정
│   │   └── seed.py               # 초기 데이터 로드
│   │
│   ├── models/                   # 데이터 모델
│   │   ├── schemas/              # Pydantic 요청/응답 스키마
│   │   │   └─ ChatRequest, ChatResponse 등
│   │   └── entities/             # DB 엔티티
│   │       └─ MedicalQA 등
│   │
│   └── __init__.py
│
├── scripts/                      # 테스트/유틸리티 스크립트
│   ├── test_tools.py
│   ├── test_answer_gen.py
│   ├── test_augmentor.py
│   └── ...
│
├── resources/                    # 리소스 파일
│   ├── 의료데이터/
│   │   ├── 필수_2136.json
│   │   ├── 필수_2228.json
│   │   └── ... (약 500개 파일)
│   └── 의료데이터.zip
│
├── chroma_db/                    # 벡터 데이터베이스 저장소 (자동 생성)
│   ├── chroma.sqlite3
│   └── [collection 디렉토리]/
│       ├── data_level0.bin
│       └── header.bin
│
├── logs/                         # 로그 파일
│   ├── agent_flow_20260214.log
│   └── seed_status.json
│
├── tests/                        # 단위 테스트
│   └── test_health.py
│
├── requirements.txt              # 패키지 의존성
├── requirements-dev.txt          # 개발용 의존성
├── pyproject.toml                # 프로젝트 설정
└── README.md                     # 문서
```

### 핵심 파일별 역할 설명

#### 🔴 `app/main.py` (진입점)
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    앱 시작할 때: 의료 데이터 로드 (seed)
    앱 종료할 때: 정리 작업
    """
    loop.run_in_executor(None, seed_data_if_empty)
    yield
    # cleanup
```
역할: FastAPI 앱 생성, 전역 예외 처리, 데이터 로드

#### 🔵 `app/service/agent_service.py` (에이전트 조율)
```python
class AgentService:
    def run_agent(inputs, session_id):
        # 1. 입력 검증
        # 2. 초기 상태 준비
        # 3. Super Graph 실행
        # 4. 결과 반환
```
역할: 3개 에이전트를 조율하고, workflow 실행

#### 🟢 `app/agents/workflow.py` (Super Graph)
```python
# Step 1: Info Extractor 호출
def call_info_extractor(state, config):
    # 내부 검색 실행
    # 결과 상태 업데이트

# Step 2: Knowledge Augmentor 호출
def call_knowledge_augmentor(state, config):
    # 외부 검색 실행

# Step 3: Answer Generator 호출
def call_answer_gen(state, config):
    # 최종 답변 생성

# 조건부 라우팅
def check_extract_status(state):
    # "충분"하면 Step 3으로 스킵
    # "부족"하면 Step 2로 이동
```
역할: 3개 에이전트 간 흐름 제어, 상태 관리

#### 🟡 `app/service/vector_service.py` (벡터 DB 추상화)
```python
class VectorService:
    def add_documents(documents, metadatas):
        # 1. Embedding 생성
        # 2. ChromaDB에 저장
    
    def search(query, n_results=5):
        # 1. Query embedding 생성
        # 2. ChromaDB에서 유사 문서 검색
```
역할: 임베딩 생성, 벡터 검색 (내부 구현 숨김)

---

## 🔄 7부: 실제 요청 흐름 (6분)

### 사용자가 "감기 걸렸어"라고 입력했을 때 일어나는 일

#### 1️⃣ API 요청
```
User:
POST /agent/chat
{
  "query": "감기 걸렸을 때 어떻게 해야 해?",
  "session_id": "user123"
}
```

#### 2️⃣ FastAPI 라우터
```python
@router.post("/agent/chat")
async def chat(request: ChatRequest, agent_service: AgentService = Depends(get_agent_service)):
    # 요청 검증
    # AgentService 주입 (DI)
    # agent_service.run_agent() 호출
```

#### 3️⃣ AgentService
```python
def run_agent(inputs, session_id="user123"):
    full_inputs = {
        "user_query": "감기 걸렸을 때 어떻게 해야 해?",
        "answer_logs": [],
        "build_logs": [],
        "augment_logs": [],
        "extract_logs": [],
        "loop_count": 0
    }
    
    config = {
        "configurable": {
            "vector_service": vector_service,
            "info_extractor_service": info_extractor,
            "knowledge_augmentor_service": augmentor,
            "answer_gen_service": answer_gen,
            "thread_id": "user123"  # 세션 추적
        }
    }
    
    return super_graph.invoke(full_inputs, config=config)
```

#### 4️⃣ Super Graph 실행

**Phase 1: Info Extractor**
```
workflow.py의 call_info_extractor() 함수 호출
    ↓
info_extractor_service.run() 호출
    ↓
info_extractor 서브그래프 호출
    ├─ Retriever 노드: ChromaDB 검색
    │  └─ Query: "감기 걸렸을 때 어떻게..."
    │  └─ Embedding 생성: [0.2, -0.5, 0.8, ...]
    │  └─ 유사 문서 5개 검색:
    │     1. "감기의 증상" (similarity: 0.95)
    │     2. "감기 치료법" (similarity: 0.92)
    │     3. "감기 예방법" (similarity: 0.88)
    │     4. "감기와 독감 구분" (similarity: 0.85)
    │     5. "감기 응급상황" (similarity: 0.82)
    │
    └─ Verifier 노드: 검색 결과 검증
       └─ LLM 프롬프트:
          "다음 문서들이 '감기 걸렸을 때 어떻게...'라는 질문에
           충분한 답변인가?"
       └─ LLM 응답:
          {
            "status": "success",
            "reason": "증상, 치료법, 예방법이 모두 포함됨"
          }

상태 업데이트:
{
  "extract_logs": [AIMessage(content='{"status": "success", ...}')],
  "process_status": "success"
}
```

**Conditional Routing (라우팅 결정)**
```python
def check_extract_status(state):
    last_msg = state["extract_logs"][-1].content
    parsed = json.loads(last_msg)
    status = parsed.get("status")
    
    if status == "success" or status == "out_of_domain":
        return "to_answer_gen"  # Step 3으로 스킵
    else:
        return "to_augment"     # Step 2로 이동
```

결정: **"success" → Step 3으로 직진!**

**Phase 2: Knowledge Augmentor (스킵됨)**
- 이미 충분한 정보가 있으므로 실행 안 됨

**Phase 3: Answer Generator**
```
workflow.py의 call_answer_gen() 함수 호출
    ↓
answer_gen_service.run() 호출
    ↓
answer_gen 서브그래프 호출
    ├─ Generator 노드: 답변 생성
    │  └─ LLM 프롬프트:
    │     """
    │     당신은 친절한 의료 상담사입니다.
    │     
    │     사용자 질문: "감기 걸렸을 때 어떻게 해야 해?"
    │     
    │     다음 정보를 기반으로 답변하세요:
    │     - 감기의 증상: 콧물, 기침, 인후통...
    │     - 감기 치료법: 휴식, 수분, 따뜻한 음식...
    │     - 감기 예방법: 손 씻기, 마스크...
    │     - 응급상황: 고열, 호흡 곤란...
    │     
    │     주의사항:
    │     1. 이것은 의료 진단이 아닙니다
    │     2. 응급상황은 병원 가라고 안내
    │     3. 의사 상담 권고
    │     """
    │  └─ LLM 응답 (생성 중...):
    │     "감기는 일반적으로 바이러스 감염..."
    │
    └─ (검증 노드 선택적)
       └─ 답변 안전성 체크

상태 업데이트:
{
  "answer_logs": [
    HumanMessage("감기 걸렸을 때 어떻게 해야 해?"),
    AIMessage("감기는 일반적으로... [full answer]")
  ]
}
```

#### 5️⃣ 결과 반환
```python
# AgentService에서 최종 상태 추출
result = super_graph.invoke(...)

answer = ""
if result.get("answer_logs"):
    last_msg = result["answer_logs"][-1]
    answer = last_msg.content

response = ChatResponse(
    answer=answer,
    user_query=result.get("user_query"),
    process_status=result.get("process_status"),
    loop_count=result.get("loop_count", 0)
)
```

#### 6️⃣ API 응답
```json
{
  "answer": "감기는 일반적으로 바이러스 감염으로 인한 호흡기 질환입니다.\n\n일반적인 대처 방법:\n1. 충분한 휴식\n2. 수분 섭취\n3. 따뜻한 음식\n4. 습도 관리\n\n증상이 심하면 의사와 상담하세요.\n\n⚠️ 응급상황:\n- 고열 (38도 이상)\n- 호흡 곤란\n- 가슴 통증\n\n본 정보는 참고용이며, 정확한 진단은 의료 전문가와 상담해야 합니다.",
  "user_query": "감기 걸렸을 때 어떻게 해야 해?",
  "process_status": "success",
  "loop_count": 1
}
```

#### 7️⃣ 사용자 화면
```
Q: 감기 걸렸을 때 어떻게 해야 해?

A: 감기는 일반적으로 바이러스 감염으로 인한...
   [답변 표시]
   
✅ 처리 상태: success
📊 에이전트 반복 횟수: 1회
```

---

## 🚀 8부: 개발자들이 알아야 할 것들 (5분)

### 의존성 주입 (DI) 패턴

```python
# deps.py - 중앙에서 인스턴스 생성
@lru_cache
def get_vector_service() -> VectorService:
    vector_repo = VectorRepository()
    embedding_service = EmbeddingService()
    return VectorService(vector_repo, embedding_service)

@lru_cache
def get_agent_service() -> AgentService:
    vector_service = get_vector_service()
    info_extractor = InfoExtractorService()
    # ... 다른 서비스들
    return AgentService(
        vector_service,
        info_extractor,
        knowledge_augmentor,
        answer_gen
    )

# agent_routers.py - 라우터에서 주입
@router.post("/agent/chat")
async def chat(
    request: ChatRequest,
    agent_service: AgentService = Depends(get_agent_service)  # 자동 주입!
):
    return agent_service.run_agent(inputs)
```

**장점:**
- 테스트할 때 mock 객체로 교체 쉬움
- 전체 앱에서 서비스가 한 곳에서 생성됨
- 싱글톤 패턴 자동 적용 (@lru_cache)

### 상태 관리 (State Graph)

```python
# state.py
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage

class MainState(TypedDict):
    user_query: str                    # 원본 사용자 질문
    answer_logs: list[BaseMessage]    # 대화 히스토리
    extract_logs: list[BaseMessage]   # Info Extractor 결과
    augment_logs: list[BaseMessage]   # Knowledge Augmentor 결과
    build_logs: list[BaseMessage]     # 빌드 로그
    loop_count: int                   # 반복 횟수
    process_status: str               # 상태
```

**왜 이렇게 설계했을까?**
- 각 에이전트의 로그를 분리하여 추적 가능
- 대화 히스토리(answer_logs)로 context window 관리
- loop_count로 무한 루프 방지
- 전체 상태를 JSON으로 직렬화 가능 (로깅, 세션 저장)

### 에러 처리

```python
# exceptions.py
class AgentException(Exception):
    def __init__(self, message, details=None, status_code=500):
        self.message = message
        self.details = details or {}
        self.status_code = status_code

class KnowledgeBaseException(Exception):
    # 벡터 DB 관련 에러

class ValidationException(Exception):
    # 입력 검증 에러

# main.py - 전역 예외 처리
@app.exception_handler(AgentException)
async def agent_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "AgentException",
            "message": exc.message,
            "details": exc.details
        }
    )
```

### 세션 관리 (Conversation History)

```python
# 각 사용자마다 thread_id로 구분
config = {
    "configurable": {
        "thread_id": "user123"  # 이 사용자의 대화 히스토리를 따로 관리
    }
}

# LangGraph의 MemorySaver가 자동으로 히스토리 저장
# 재요청 시 이전 대화를 기반으로 이어나감
```

### 로깅 시스템

```python
# core/logger.py
def log_agent_step(agent_name, step_description, details=None):
    logger.info(f"[{agent_name}] {step_description}", extra={"details": details})
    
    # JSON 로그로 저장 (추후 분석용)
    with open("logs/agent_flow.log", "a") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "step": step_description,
            "details": details
        }, f)
        f.write("\n")

# workflow.py - 각 단계에서 호출
log_agent_step("Workflow", "Step 1: MedicalInfoExtractor 시작", {"query": user_query})
```

---

## 🛠️ 9부: 로컬 환경 설정 및 실행 (3분)

### 설치 및 실행

```bash
# 1. 가상환경 생성
python -m venv .venv

# 2. 활성화
# Windows:
.\.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 환경변수 설정 (.env 파일)
UPSTAGE_API_KEY=your_key_here

# 5. 서버 시작
uvicorn app.main:app --reload --port 8001

# 6. Swagger 문서 확인
http://127.0.0.1:8001/docs
```

### 테스트 방법

#### cURL로 테스트
```bash
curl -X POST "http://127.0.0.1:8001/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "감기 걸렸을 때 어떻게 해야 해?",
    "session_id": "test_user"
  }'
```

#### Python으로 테스트
```python
import requests

response = requests.post(
    "http://127.0.0.1:8001/agent/chat",
    json={
        "query": "감기 걸렸을 때 어떻게 해야 해?",
        "session_id": "test_user"
    }
)

print(response.json()["answer"])
```

#### Swagger UI 사용
1. `http://127.0.0.1:8001/docs` 접속
2. `POST /agent/chat` 클릭
3. "Try it out" 클릭
4. 요청 작성 후 "Execute"

---

## 🔮 10부: 향후 계획 및 확장 가능성 (2분)

### 현재 상태 (MVP)
```
✅ 멀티에이전트 시스템 구축
✅ 내부/외부 검색 기반 답변
✅ 안전성 가이드라인 적용
✅ REST API + Streaming 제공
✅ 의료 데이터셋 500개 로드
```

### 향후 계획

#### Phase 2: 개인화
```
[ ] 사용자 건강 기록 저장
   - 처방전 업로드
   - 건강검진 결과 저장
   - 복용 중인 약 기록

[ ] OCR/Vision 기능
   - 처방전 이미지 인식
   - 건강검진지 자동 분석
   - 약 패키지 인식

[ ] 개인 맞춤 답변
   - "내 혈압이 높은데 감기 약 먹어도 괜찮아?"
   - 개인 기록 기반 조언
```

#### Phase 3: 고급 기능
```
[ ] 의사 연계
   - 온라인 의료 상담 연결
   - 처방약 배송 연동

[ ] 질병 예측
   - 증상 패턴 분석
   - "이 패턴은 독감일 가능성이 높습니다"

[ ] 의료비 추정
   - 진단에 따른 예상 비용
   - 보험 적용 가능 항목

[ ] 다국어 지원
   - 한국어, 영어, 중국어 등
```

### 기술 개선 사항
```
[ ] 성능 최적화
   - 캐싱 (자주 묻는 질문)
   - 배치 임베딩

[ ] 평가 시스템
   - 답변 품질 평가
   - 의료 전문가 검수

[ ] 모니터링
   - 사용 통계
   - 에러 추적 (Sentry)
   - 비용 모니터링
```

---

## ❓ 11부: Q&A 예상 질문 (3분)

### Q1: "왜 3개의 에이전트가 필요한가?"

**A:** 역할 분담으로 각 단계를 명확하게 만들기 위함
- Info Extractor: "내부에 있는 정보로 충분한가?" 판단
- Knowledge Augmentor: 부족하면 외부에서 추가 정보
- Answer Generator: 수집된 정보를 바탕으로 친절한 답변

만약 한 개의 에이전트만 사용하면:
- 각 단계의 로그가 섞여서 추적 어려움
- 왜 외부 검색을 했는지 이유 파악 안 됨
- 답변 생성 실패 시 어느 단계에서 문제인지 모름

### Q2: "벡터 검색과 일반 검색의 차이는?"

**A:** 이미 설명했지만, 한 번 더:

```
일반 검색 (Keyword-based):
"감기" 검색 → 정확히 "감기"라는 단어만 매칭
결과: "감기", "감기약", "감기걸렸을 때"만 나옴
문제: "cold", "감염증", "respiratory"는 못 찾음

벡터 검색 (Semantic):
"감기" 검색 → 의미적으로 비슷한 모든 문서 찾기
결과: "감기", "cold", "감염증", "호흡기질환", "바이러스 감염" 등
장점: 의미가 같으면 다른 표현도 찾을 수 있음
```

### Q3: "외부 검색(Knowledge Augmentor)이 보안 문제는 없나?"

**A:** 좋은 질문! 현재:

```
✅ 안전한 부분:
- 의료 신뢰도 높은 출처만 필터링
- 개인 정보 미포함 (공개 정보만 검색)
- 검색 결과 로깅 (추적 가능)

⚠️ 고려사항:
- 인터넷 정보의 정확성은 보장 불가
- 외부 API 비용 발생
- 응답 시간 증가

향후 개선:
- 화이트리스트 출처만 검색
- 사용자별 검색 제한
- 의료진 사전 검수 후 DB 등록
```

### Q4: "세션 관리는 어떻게 되나?"

**A:** LangGraph의 MemorySaver로 자동 관리

```
사용자 A: session_id = "user_a_session_123"
사용자 B: session_id = "user_b_session_456"

메모리에 따로 관리:
{
  "user_a_session_123": {
    "messages": [HumanMessage(...), AIMessage(...)],
    "state": {...}
  },
  "user_b_session_456": {
    "messages": [HumanMessage(...), AIMessage(...)],
    "state": {...}
  }
}

장점: 각 사용자의 대화가 섞이지 않음
단점: 서버 재시작 시 메모리 초기화 (나중에 DB 저장으로 개선)
```

### Q5: "에러가 나면 어떻게 되나?"

**A:** 3단계 에러 처리

```
1. 서비스 레이어에서 catch:
   vector_service.search() 실패
   → KnowledgeBaseException 발생

2. AgentService에서 catch:
   agent_service.run_agent() 실패
   → AgentException 발생 (상세 정보 포함)

3. FastAPI 라우터에서 catch:
   @app.exception_handler(AgentException)
   → JSON 응답으로 변환

최종 응답:
{
  "error": "AgentException",
  "message": "Agent execution failed: ...",
  "details": {"user_query": "...", "session_id": "..."}
}
```

---

## 📊 12부: 성능 및 비용 고려사항 (2분)

### 응답 시간 예상

```
평균 응답 시간 분석:

┌─────────────────────────┬───────┐
│ 단계                     │ 시간   │
├─────────────────────────┼───────┤
│ 1. Info Extractor       │ 1-2초  │
│   - Embedding 생성       │ 0.5초  │
│   - ChromaDB 검색        │ 0.3초  │
│   - LLM Verifier 호출    │ 0.5-1초│
├─────────────────────────┼───────┤
│ 2. Knowledge Augmentor  │ 0-3초  │
│   (필요할 때만)          │        │
│   - Google Search 호출   │ 1-2초  │
│   - 결과 처리            │ 0.5초  │
├─────────────────────────┼───────┤
│ 3. Answer Generator     │ 1-2초  │
│   - LLM 스트리밍 답변    │ 1-2초  │
├─────────────────────────┼───────┤
│ 합계 (Step 1+3)         │ 2-4초  │
│ 합계 (모든 Step)        │ 3-7초  │
└─────────────────────────┴───────┘

최적화 방법:
- 자주 묻는 질문 캐싱 → 0.5초 이내
- 배치 임베딩 → 시작 시간 단축
- 병렬 처리 → 구조상 어려움 (순차 실행 필요)
```

### API 비용 추정 (월간)

```
기준: 하루 1000건 요청, 한국형 Upstage 가격

┌──────────────────────────┬──────┬────────┐
│ API                      │ 가격 │ 월간   │
├──────────────────────────┼──────┼────────┤
│ Chat (Solar)            │ 0.3원│ 9,000원│
│ Embedding               │ 0.05원 │ 1,500원│
│ External Search (Serper)│ 0.01$ │ 10$(if used)
├──────────────────────────┼──────┼────────┤
│ 합계                      │  │ ~11,500원│
└──────────────────────────┴──────┴────────┘

* 실제 가격은 Upstage 정책 변경 시 달라질 수 있음
* 외부 검색 사용 빈도에 따라 변동
```

### 서버 리소스

```
최소 요구사항:
- CPU: 2 cores
- RAM: 2GB (ChromaDB 포함)
- SSD: 1GB (데이터)

추천 사양 (프로덕션):
- CPU: 4 cores
- RAM: 4-8GB
- SSD: 5GB
- GPU: Optional (임베딩 생성 가속)
```

---

## 🎓 13부: 개발자 가이드 (코드 수정 방법)

### 새로운 에이전트 추가하기

```python
# 1. 새 서브그래프 파일 생성
# app/agents/subgraphs/my_agent.py

from langgraph.graph import StateGraph, END
from app.agents.state import MainState

def my_agent_node(state, config):
    """새로운 에이전트 로직"""
    # ... 구현
    return {"my_agent_logs": [...]}

my_agent_graph = StateGraph(MainState)
my_agent_graph.add_node("my_agent", my_agent_node)
my_agent_graph.set_entry_point("my_agent")
my_agent_graph.add_edge("my_agent", END)
my_agent_graph = my_agent_graph.compile()

# 2. 서비스 클래스 생성
# app/service/agents/my_agent_service.py

class MyAgentService:
    def run(self, ...):
        # ... 구현
        return {"my_agent_logs": [...]}

# 3. workflow.py에 통합
# app/agents/workflow.py

def call_my_agent(state, config):
    my_agent_service = _get_service(config, "my_agent_service")
    result = my_agent_service.run(...)
    return result

# Super Graph에 노드 추가
graph.add_node("my_agent", call_my_agent)
graph.add_edge("previous_node", "my_agent")
graph.add_edge("my_agent", "next_node")

# 4. deps.py에 의존성 추가
@lru_cache
def get_my_agent_service():
    return MyAgentService()
```

### 프롬프트 수정하기

```python
# app/service/agents/answer_gen_service.py

# 기존 프롬프트:
ANSWER_GEN_PROMPT = """
당신은 친절한 의료 상담사입니다.
...
"""

# 수정 예시:
ANSWER_GEN_PROMPT = """
당신은 친절한 의료 상담사입니다.
당신의 이름은 '의료봇'입니다.
사용자의 감정을 이해하고 공감해주세요.

사용자 질문: {user_query}
관련 정보: {context}

다음을 반드시 포함하세요:
1. 질문에 대한 정확한 답변
2. 일반적인 대처 방법
3. 주의사항 및 응급상황
4. "의료 진단이 아닙니다" 면책조항

친절하고 온따뜻한 톤으로 답변하세요.
"""

# 프롬프트 적용:
response = llm.invoke(ANSWER_GEN_PROMPT.format(...))
```

### 벡터 검색 결과 수 조정하기

```python
# app/service/vector_service.py

def search(self, query, n_results=5):  # ← 기본값 5
    # n_results를 더 늘리면 더 많은 문서 검색
    # 장점: 더 많은 정보 활용
    # 단점: 응답 시간 증가, 정보 과다
    
    query_embedding = self.embedding_service.create_embedding(query)
    results = self.vector_repository.query(
        query_embeddings=[query_embedding],
        n_results=n_results,  # ← 여기를 조정
        include=["documents", "metadatas", "distances"]
    )
```

### 로그 레벨 조정하기

```python
# app/core/logger.py

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # 모든 레벨 로그

# 또는 프로덕션에서:
logger.setLevel(logging.INFO)   # INFO 이상만 로그
```

---

## 🧪 14부: 테스트 및 디버깅

### 유닛 테스트 예시

```python
# tests/test_vector_service.py

import pytest
from app.service.vector_service import VectorService
from app.service.embedding_service import EmbeddingService
from app.repository.vector.vector_repo import VectorRepository

@pytest.fixture
def vector_service():
    # Mock 객체 사용
    vector_repo = MagicMock(spec=VectorRepository)
    embedding_service = MagicMock(spec=EmbeddingService)
    embedding_service.create_embedding.return_value = [0.1, 0.2, ...]
    return VectorService(vector_repo, embedding_service)

def test_search_returns_results(vector_service):
    # Arrange
    query = "감기"
    expected = [
        MedicalQA(id="1", question="감기 증상?", answer="콧물..."),
        MedicalQA(id="2", question="감기 치료?", answer="휴식...")
    ]
    vector_service.vector_repository.query.return_value = expected
    
    # Act
    result = vector_service.search(query)
    
    # Assert
    assert len(result) == 2
    assert result[0].question == "감기 증상?"
```

### 디버깅 팁

```python
# 1. 로그 확인
# logs/agent_flow.log 파일 확인
tail -f logs/agent_flow.log

# 2. 각 단계별 출력
# workflow.py의 print() 문으로 디버깅
print(f"[Debug] Extract status: {status}")
print(f"[Debug] Found documents: {len(documents)}")

# 3. 상태 직렬화
# 각 단계의 상태를 JSON으로 저장
import json
print(json.dumps(state, default=str))

# 4. 프롬프트 확인
# LLM에 어떤 프롬프트를 보냈는지 확인
print(f"Prompt: {prompt}")
```

---

## 📞 마무리

### 핵심 요점 정리

```
1. medinyang-Agent는 멀티에이전트 의료 상담 시스템
2. 3개의 에이전트가 역할 분담하여 협력
3. 내부 지식 + 외부 검색 기반의 하이브리드 RAG
4. 안전한 의료 상담을 위한 가이드라인 적용
5. FastAPI + LangGraph 기반 현대적인 구조
6. 벡터 검색(의미 기반)으로 정확한 정보 추출
7. 세션 관리로 사용자별 독립적인 대화 가능
```

### 팀원들에게 할 조언

```
✅ 처음 기여하는 분들을 위한 팁:

1. 먼저 deps.py와 main.py로 전체 구조 파악
2. workflow.py로 에이전트들의 흐름 이해
3. 각 서브그래프 파일로 세부 구현 학습
4. 테스트부터 시작하기 (tests/ 폴더)
5. 정기적으로 로그 확인 (logs/ 폴더)

❌ 주의사항:

- 프롬프트 수정 시 항상 테스트 후 병합
- 벡터 DB는 재시딩이 느리니 주의
- API 키 노출 금지 (.env 파일 사용)
- 외부 검색 비용 모니터링
```

### 추가 리소스

```
학습 자료:
- LangChain 공식 문서: https://python.langchain.com/
- LangGraph 튜토리얼: https://langchain-ai.github.io/langgraph/
- ChromaDB 가이드: https://docs.trychroma.com/
- Upstage API 문서: https://upstage.ai/docs

커뮤니티:
- LangChain Discord
- Upstage 개발자 포럼
- Stack Overflow
```

---

**작성일**: 2026년 2월 14일  
**버전**: 1.0  
**관리자**: [프로젝트 리더 이름]

이 문서는 정기적으로 업데이트됩니다. 질문이나 추가 사항이 있으면 이슈 등록하세요! 🙋‍♂️
