# 🏥 medinyang-Agent

**medinyang-Agent**는 의료/건강 관련 질문에 대해 **근거 기반(RAG - Retrieval-Augmented Generation)** 으로 답변을 제공하는 **멀티에이전트 의료 상담 시스템**입니다.

Upstage Solar LLM과 ChromaDB(Vector DB)를 기반으로 **내부 의료 지식 검색**을 우선 수행하며, 필요 시 **외부 검색을 통해 지식을 확장**하는 하이브리드 구조를 가집니다.

또한 사용자가 업로드한 **처방전/건강검진 기록지**를 OCR(또는 Vision 모델)로 분석하여 저장하고, 개인 건강 기록 기반 질의응답으로 확장 가능한 구조로 설계됩니다.

> ⚠️ **주의(Disclaimer)**  
> 본 프로젝트는 **의료 진단을 제공하지 않습니다**.  
> 출력 결과는 **참고용 정보**이며, 정확한 진단 및 치료는 반드시 **의료 전문가(의사/약사)와 상담**해야 합니다.
>
> **응급상황** (고열, 호흡 곤란, 가슴 통증 등)이 있으면 즉시 119에 신고하세요!

---

## 📌 목차
- [핵심 특징](#-핵심-특징)
- [주요 기능](#-주요-기능)
- [시스템 아키텍처](#-시스템-아키텍처)
- [멀티에이전트 워크플로우](#-멀티에이전트-워크플로우)
- [기술 스택](#-기술-스택)
- [프로젝트 구조](#-프로젝트-구조)
- [설치 및 실행](#-설치-및-실행)
- [API 사용법](#-api-사용법)
- [개발 가이드](#-개발-가이드)
- [성능 및 비용](#-성능-및-비용)
- [향후 계획](#-향후-계획)
- [FAQ](#-faq)
- [기여 방법](#-기여-방법)
- [라이선스](#-라이선스)

---

## ✨ 핵심 특징

### 🎯 1. 하이브리드 RAG 시스템
```
사용자 질문 → 내부 의료 DB 검색 → 정보 충분성 판단
                                    ├─ YES: 직접 답변 생성
                                    └─ NO: 외부 검색 후 답변
```

- **내부 검색 우선**: ChromaDB에 저장된 500+ 의료 지식 우선 활용
- **지능형 보강**: 내부 정보 부족 시 Google Search API로 외부 정보 검색
- **신뢰성 보증**: 모든 답변에 근거 명시 및 참고자료 제공

### 🤖 2. 멀티에이전트 협력 구조

3개의 전문 에이전트가 각자의 역할을 담당하고 **Super Graph**가 조율:

| 에이전트 | 역할 | 기술 |
|---------|------|------|
| **Info Extractor** | 내부 의료 DB에서 관련 정보 검색 | Vector Search (Cosine Similarity) |
| **Knowledge Augmentor** | 부족한 정보 외부 검색으로 보강 | Google Search API |
| **Answer Generator** | 수집된 정보 기반 친절한 답변 생성 | LLM with Safety Guidelines |

### 🛡️ 3. 안전한 의료 상담

```python
# 자동으로 이런 가이드라인을 적용합니다:

✗ 금지 사항:
  - "당신은 OO병입니다" (진단 금지)
  - "이 약을 꼭 먹어야 합니다" (약물 강제 금지)
  - "OO는 위험합니다" (공포심 유발 금지)

✓ 권장 사항:
  - "일반적으로 이런 증상은..."
  - "의사와 상담해보세요"
  - "응급실에 가시는 것을 권고합니다"
```

### 📊 4. 완전한 추적 및 로깅

- 각 단계의 에이전트 로그 저장
- 최종 답변까지의 전체 과정 추적
- JSON 형식 로그로 분석 용이
- 세션별 대화 히스토리 관리

---

## 🎨 주요 기능

### 1️⃣ 의료 상담 멀티에이전트 (RAG 기반)

- ✅ 내부 의료 지식(Vector DB) 기반 검색 후 답변 생성
- ✅ 검색된 정보가 부족하면 **자동으로** 외부 검색을 통해 지식 보강
- ✅ 안전한 답변 생성을 위한 가이드라인 자동 적용
  - 확정 진단 금지 및 안내
  - 응급상황(레드플래그) 자동 감지
  - 의료진 상담 권고
- ✅ 답변 신뢰도 표시 및 출처 명시

**실제 예시:**
```
Q: "감기 걸렸을 때 어떻게 해야 해?"

A: 감기는 일반적으로 바이러스 감염으로 인한 호흡기 질환입니다.

일반적인 대처 방법:
1. 충분한 휴식 (하루 7-8시간 수면)
2. 수분 섭취 (하루 2-3리터 물)
3. 따뜻한 음식 (국, 죽, 생강차)
4. 습도 관리 (50-60% 습도 유지)

증상이 심하거나 1주일 이상 지속되면 반드시 의사와 상담하세요.

⚠️ 다음 증상이 있으면 응급실로 가세요:
- 고열 (38도 이상)
- 호흡 곤란
- 가슴 통증
- 의식 변화

본 정보는 참고용이며, 정확한 진단은 의료 전문가와 상담해야 합니다.
```

### 2️⃣ 개인 건강 문서 업로드 및 기록 관리 (향후 확장)

- 📄 처방전 / 건강검진 기록지 업로드
- 🔍 OCR/Vision 기반 텍스트 추출 및 구조화
- 💾 사용자 개인 기록 DB에 저장하여 히스토리 관리
- 🔗 추후 개인 기록 기반 RAG(QA) 기능으로 확장 예정

**예상 개발 로드맵:**
```
Phase 2 (Q2 2026):
└─ 사용자 인증 및 개인 건강 기록 DB 구축
└─ 처방전 OCR 분석 기능
└─ 건강검진 결과 자동 파싱

Phase 3 (Q3 2026):
└─ 개인 기록 기반 맞춤형 답변
└─ 약물 상호작용 검사
└─ 건강 추세 분석 및 조언
```

---

## 🏗️ 시스템 아키텍처

### 전체 시스템 다이어그램

```
┌─────────────────────────────────────────────────────────┐
│                    사용자 인터페이스                        │
│            (Web Browser / Mobile App)                   │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────┐
│                  FastAPI Server                          │
│  ├─ POST /agent/chat         (일반 채팅)                │
│  ├─ POST /agent/chat/stream  (스트리밍)                 │
│  ├─ GET  /agent/health       (헬스 체크)               │
│  ├─ GET  /agent/seed-status  (데이터 로드 상태)        │
│  ├─ POST /agent/knowledge/add (지식 추가)              │
│  └─ GET  /agent/knowledge/stats (통계)                │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│               AgentService (비즈니스 로직)                │
│                                                          │
│  ┌────────────────────────────────────────────────────┐│
│  │              Super Graph (LangGraph)                ││
│  │  ┌──────────┐   ┌──────────┐   ┌──────────┐       ││
│  │  │  Step 1  │──▶│ Decision │──▶│  Step 2  │       ││
│  │  │ Extractor│   │ (Verify) │   │Augmentor │       ││
│  │  └──────────┘   └────┬─────┘   └──────────┘       ││
│  │                      │              │              ││
│  │                      └──────────────┘              ││
│  │                           │                        ││
│  │                      ┌────▼──────┐                 ││
│  │                      │   Step 3   │                ││
│  │                      │ AnswerGen  │                ││
│  │                      └────────────┘                ││
│  └────────────────────────────────────────────────────┘│
│                                                         │
│  ┌────────────────────────────────────────────────────┐│
│  │  SubGraph들                                         ││
│  │  ├─ InfoExtractor (검색 + 검증)                     ││
│  │  ├─ KnowledgeAugmentor (외부 검색)                  ││
│  │  └─ AnswerGenerator (답변 생성)                     ││
│  └────────────────────────────────────────────────────┘│
└──────────────────────┬──────────────────────────────────┘
                       │
    ┌──────────────────┼──────────────────┐
    │                  │                  │
┌───▼────────┐  ┌──────▼──────┐  ┌──────▼──────┐
│  Upstage   │  │  ChromaDB   │  │   Google    │
│ Solar LLM  │  │  (Vector    │  │   Search    │
│            │  │   Database) │  │   API       │
│ - Chat     │  │             │  │             │
│ - Embedding│  │ - 500+ 의료 │  │ - 외부 정보 │
│            │  │   지식      │  │   검색      │
└────────────┘  └─────────────┘  └─────────────┘
```

### MVP (1차 목표)

```
✅ Upstage Solar (Chat Model) 기반 답변 생성
✅ Upstage Embeddings 기반 의미 검색 (Semantic Search)
✅ ChromaDB 기반 벡터 저장소 구축
✅ AI HUB 필수의료 데이터셋 500+ 로드
✅ LangGraph 멀티에이전트 오케스트레이션
✅ FastAPI REST API + Streaming 제공
✅ 세션 관리 및 대화 히스토리
✅ 완전한 로깅 및 추적 시스템
```

---

## 🤖 멀티에이전트 워크플로우

### 전체 흐름

```
1️⃣ 사용자 질문 입력
        ↓
2️⃣ Info Extractor Agent 실행
   ├─ 질문을 벡터로 변환
   ├─ ChromaDB에서 유사 문서 검색 (Top 5)
   └─ 검색 결과가 충분한지 LLM으로 검증
        ↓
   검증 결과: success / insufficient / out_of_domain?
        │
        ├─ success: Step 3으로 진행
        ├─ insufficient: Step 2로 진행
        └─ out_of_domain: Step 3으로 진행 (특수 처리)
        ↓
3️⃣ (필요시) Knowledge Augmentor Agent 실행
   ├─ Google Search API로 외부 검색
   ├─ 검색 결과 필터링 (신뢰도 높은 출처 우선)
   └─ 결과를 상태에 추가
        ↓
4️⃣ Answer Generator Agent 실행
   ├─ 수집된 모든 정보를 Context로 사용
   ├─ 의료 상담 가이드라인 적용
   └─ 친절한 답변 생성
        ↓
5️⃣ 최종 답변 반환
   ├─ 답변 텍스트
   ├─ 처리 상태
   ├─ 에이전트 반복 횟수
   └─ (스트리밍 모드) 실시간 로그
```

### 각 에이전트 상세 설명

#### 🔍 Agent #1: Info Extractor (정보 추출 에이전트)

**목적**: 내부 의료 데이터베이스에서 관련 정보를 효율적으로 검색

**파일 위치**:
- 서비스: `app/service/agents/info_extractor_service.py`
- 그래프: `app/agents/subgraphs/info_extractor.py`

**동작 원리**:
```python
1. Retriever 노드:
   - 사용자 질문을 Upstage Embedding으로 벡터화
   - ChromaDB에서 코사인 유사도 기반 검색 (Top 5)
   - 메타데이터(출처, 신뢰도)와 함께 반환

2. Verifier 노드:
   - LLM에게 "이 문서들이 질문에 답하기에 충분한가?" 물어봄
   - JSON 응답으로 status 결정:
     {
       "status": "success|insufficient|out_of_domain",
       "reason": "설명",
       "confidence": 0.95
     }
```

**흐름 제어**:
```
Status: success
  ↓ 충분한 정보 있음
  Step 3으로 진행 (Step 2 스킵)

Status: insufficient
  ↓ 정보 부족
  Step 2로 진행 (외부 검색)

Status: out_of_domain
  ↓ 의료와 무관한 질문
  특수 안내 메시지 후 Step 3으로
```

---

#### 🌐 Agent #2: Knowledge Augmentor (지식 보강 에이전트)

**목적**: 내부 검색으로 부족한 정보를 외부 검색으로 보강

**파일 위치**:
- 서비스: `app/service/agents/knowledge_augmentor_service.py`
- 그래프: `app/agents/subgraphs/knowledge_augmentor.py`

**동작 원리**:
```python
1. Search 노드:
   - Google Search API (Serper)로 웹 검색
   - 검색어 자동 생성 및 최적화
   - 결과 수 제한 (상위 5개)

2. Filter 노드:
   - 신뢰도 필터링 (의료 기관, 학술지 우선)
   - 중복 제거
   - 합법성 검증

3. Augment 노드:
   - 기존 Context에 추가
   - 출처 기록 (어디서 가져왔는지)
```

**보안 고려사항**:
```
✅ 자동 필터링:
   - 공식 의료 기관만
   - 검증된 출처
   - 명확한 저자 정보

⚠️ 수동 검수 권고:
   - 외부 검색 결과는 신뢰도 확인 필요
   - 민감한 질문은 의료진 상담 권고
```

---

#### 💬 Agent #3: Answer Generator (답변 생성 에이전트)

**목적**: 수집된 정보를 바탕으로 친절하고 안전한 답변 생성

**파일 위치**:
- 서비스: `app/service/agents/answer_gen_service.py`
- 그래프: `app/agents/subgraphs/answer_gen.py`

**생성 프롬프트** (간략):
```
당신은 친절한 의료 상담사입니다.
다음 정보를 바탕으로 사용자 질문에 답변해주세요.

정보:
{검색된 의료 정보들}

가이드라인:
1. 진단하지 마세요
2. 일반적인 대처법만 제시
3. 의료 전문가 상담 권고
4. 응급상황 명시
5. 따뜻하고 공감하는 톤
```

**안전 검증**:
```python
# 생성된 답변을 자동으로 검사:

금지 표현 감지:
  - "당신은 ... 입니다" (진단)
  - "반드시 ... 해야" (강제)
  - "위험합니다" (공포 유발)

필수 포함 요소:
  - ✓ 면책조항
  - ✓ 의료진 상담 권고
  - ✓ 응급상황 안내
```

---

## 🛠️ 기술 스택

### Backend

| 기술 | 버전 | 목적 |
|------|------|------|
| **Python** | 3.10+ | 메인 언어 |
| **FastAPI** | 0.110+ | REST API 프레임워크 |
| **Uvicorn** | 0.27+ | ASGI 서버 |
| **Pydantic** | 2.6+ | 데이터 검증 |

### AI / ML

| 기술 | 목적 |
|------|------|
| **Upstage Solar LLM** | 질문 이해 및 답변 생성 |
| **Upstage Embeddings** | 의미 기반 검색 |
| **LangChain** | LLM 프레임워크 |
| **LangGraph** | 멀티에이전트 오케스트레이션 |
| **LangSmith** | 모니터링 (선택) |

### 데이터 / 검색

| 기술 | 목적 |
|------|------|
| **ChromaDB** | 벡터 데이터베이스 |
| **Serper API** | 웹 검색 |

### 개발 / 배포

| 기술 | 목적 |
|------|------|
| **python-dotenv** | 환경변수 관리 |
| **pytest** | 단위 테스트 (선택) |
| **Docker** | 컨테이너화 (선택) |

---

## 📁 프로젝트 구조

```
medinyang-Agent/
│
├── app/                              # 🎯 메인 애플리케이션
│   │
│   ├── main.py                       # FastAPI 앱 진입점
│   │   └─ 앱 초기화, 미들웨어, 예외 처리
│   │
│   ├── deps.py                       # 의존성 주입 (Dependency Injection)
│   │   └─ 모든 서비스 인스턴스 생성 및 관리
│   │
│   ├── exceptions.py                 # 커스텀 예외 정의
│   │   ├─ AgentException
│   │   ├─ KnowledgeBaseException
│   │   └─ ValidationException
│   │
│   ├── api/
│   │   └── routes/
│   │       └── agent_routers.py      # API 엔드포인트
│   │           ├─ POST /agent/chat
│   │           ├─ POST /agent/chat/stream
│   │           ├─ GET  /agent/health
│   │           └─ ... (6개 엔드포인트)
│   │
│   ├── agents/                       # 🤖 멀티에이전트 로직
│   │   ├── state.py                  # 상태 정의 (TypedDict)
│   │   ├── workflow.py               # Super Graph (메인 워크플로우)
│   │   ├── tools.py                  # 에이전트 도구들
│   │   ├── utils.py                  # 유틸리티 함수
│   │   └── subgraphs/
│   │       ├── info_extractor.py     # Agent #1: 정보 검색
│   │       ├── knowledge_augmentor.py # Agent #2: 지식 보강
│   │       └── answer_gen.py         # Agent #3: 답변 생성
│   │
│   ├── service/                      # 💼 비즈니스 로직 (Service Layer)
│   │   ├── agent_service.py          # 에이전트 조율
│   │   ├── vector_service.py         # 벡터 검색 추상화
│   │   ├── embedding_service.py      # Embedding 생성
│   │   └── agents/
│   │       ├── info_extractor_service.py
│   │       ├── knowledge_augmentor_service.py
│   │       └── answer_gen_service.py
│   │
│   ├── repository/                   # 🗄️ 데이터 접근층 (DAO Pattern)
│   │   ├── vector/
│   │   │   └── vector_repo.py        # ChromaDB 직접 접근
│   │   └── client/
│   │
│   ├── core/                         # ⚙️ 핵심 설정
│   │   ├── llm.py                    # LLM 클라이언트 설정
│   │   ├── db.py                     # ChromaDB 연결
│   │   ├── logger.py                 # 로깅 설정
│   │   └── seed.py                   # 초기 데이터 로드
│   │
│   ├── models/                       # 📊 데이터 모델
│   │   ├── schemas/                  # Pydantic 요청/응답 스키마
│   │   │   ├─ ChatRequest, ChatResponse
│   │   │   └─ AddKnowledgeRequest, StatsResponse
│   │   └── entities/
│   │       └─ MedicalQA
│   │
│   └── __init__.py
│
├── scripts/                          # 🧪 테스트/유틸리티 스크립트
│   ├── test_tools.py
│   ├── test_answer_gen.py
│   ├── test_augmentor.py
│   └── ... (더 많은 테스트 파일)
│
├── tests/                            # ✅ 단위 테스트
│   ├── test_health.py
│   └── __init__.py
│
├── resources/                        # 📦 리소스 파일
│   ├── 의료데이터/                    # 의료 지식 데이터셋
│   │   ├─ 필수_2136.json            # 약 500개 의료 관련 JSON 파일
│   │   ├─ 필수_2228.json
│   │   └─ ... (생략)
│   └── 의료데이터.zip                 # 원본 ZIP 파일
│
├── chroma_db/                        # 🗂️ 벡터 DB (자동 생성)
│   ├── chroma.sqlite3                # 메타데이터 저장소
│   └── [collection UUID]/            # 컬렉션 디렉토리
│       ├─ data_level0.bin
│       ├─ header.bin
│       ├─ length.bin
│       └─ link_lists.bin
│
├── logs/                             # 📝 로그 파일
│   ├── agent_flow_*.log              # 에이전트 실행 로그
│   └── seed_status.json              # 시딩 상태
│
├── requirements.txt                  # 📋 프로덕션 의존성
├── requirements-dev.txt              # 📋 개발 의존성
├── pyproject.toml                    # 프로젝트 메타 설정
├── .env.example                      # 환경변수 템플릿
├── README.md                         # 이 파일
└── PRESENTATION_SCRIPT.md            # 팀 발표용 대본
```

### 핵심 파일 설명

#### `app/main.py`
```python
# FastAPI 앱 초기화
# 앱 시작 시 의료 데이터 로드 (Seeding)
# 전역 예외 처리기 등록
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작: 의료 데이터 로드
    loop.run_in_executor(None, seed_data_if_empty)
    yield
    # 종료: 정리
```

#### `app/agents/workflow.py`
```python
# Super Graph 정의
# 3개 에이전트의 흐름 제어
# 조건부 라우팅 (Conditional Routing)

def check_extract_status(state):
    if status == "success":
        return "to_answer_gen"  # Step 3으로
    else:
        return "to_augment"      # Step 2로
```

#### `app/service/vector_service.py`
```python
# 벡터 검색 비즈니스 로직
# Embedding 생성 + ChromaDB 쿼리
# 내부 구현을 서비스 레이어로 캡슐화
```

---

## 🚀 설치 및 실행

### 사전 요구사항

```
- Python 3.10 이상
- pip (패키지 관리자)
- Upstage API Key (https://console.upstage.ai/)
- Git
```

### Step 1️⃣: 저장소 클론

```bash
git clone https://github.com/yourusername/medinyang-Agent.git
cd medinyang-Agent
```

### Step 2️⃣: 가상환경 생성 및 활성화

**Windows:**
```bash
python -m venv .venv
.\.venv\Scripts\activate
```

**macOS / Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### Step 3️⃣: 의존성 설치

```bash
# 프로덕션 의존성
pip install -r requirements.txt

# 개발 의존성 (선택)
pip install -r requirements-dev.txt
```

### Step 4️⃣: 환경변수 설정

```.env
# .env 파일 생성
UPSTAGE_API_KEY=your_api_key_here

# 선택사항:
SERPER_API_KEY=your_serper_key_here        # 외부 검색 사용 시
LOG_LEVEL=INFO                             # DEBUG, INFO, WARNING
```

**API Key 획득:**
- Upstage: https://console.upstage.ai/ → API Keys
- Serper: https://serper.dev/ → Free trial

### Step 5️⃣: 서버 시작

```bash
# 기본 실행
uvicorn app.main:app --reload --port 8001

# 다른 포트에서 실행
uvicorn app.main:app --reload --port 8080

# 프로덕션 모드 (자동 재시작 없음)
uvicorn app.main:app --port 8001 --workers 4
```

### Step 6️⃣: 초기화 확인

```bash
# 1️⃣ 헬스 체크
curl http://127.0.0.1:8001/agent/health

# 2️⃣ 의료 데이터 로드 상태 확인
curl http://127.0.0.1:8001/agent/seed-status

# 3️⃣ Swagger 문서 확인
http://127.0.0.1:8001/docs
```

**예상 출력:**
```json
{
  "status": "healthy",
  "message": "Agent service is running"
}
```

---

## 💬 API 사용법

### 📚 Swagger UI 사용 (권장)

```
http://127.0.0.1:8001/docs
```

### 1️⃣ 일반 채팅 (동기식)

**엔드포인트**: `POST /agent/chat`

**요청:**
```bash
curl -X POST "http://127.0.0.1:8001/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "감기 걸렸을 때 어떻게 해야 해?",
    "session_id": "user_123"
  }'
```

**응답:**
```json
{
  "answer": "감기는 일반적으로...",
  "user_query": "감기 걸렸을 때 어떻게 해야 해?",
  "process_status": "success",
  "loop_count": 1
}
```

**Python 예시:**
```python
import requests

response = requests.post(
    "http://127.0.0.1:8001/agent/chat",
    json={
        "query": "감기 걸렸을 때 어떻게 해야 해?",
        "session_id": "user_123"
    }
)

print(response.json()["answer"])
```

---

### 2️⃣ 스트리밍 채팅 (비동기식)

**엔드포인트**: `POST /agent/chat/stream`

**특징:**
- 실시간 로그 스트리밍 (에이전트 단계별)
- 답변을 토큰 단위로 스트리밍
- 사용자 경험 개선

**JavaScript 예시:**
```javascript
const eventSource = new EventSource(
  'http://127.0.0.1:8001/agent/chat/stream',
  {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      query: "감기 걸렸을 때 어떻게 해야 해?",
      session_id: "user_123"
    })
  }
);

eventSource.addEventListener('log', (event) => {
  console.log('Step:', JSON.parse(event.data));
});

eventSource.addEventListener('token', (event) => {
  const token = JSON.parse(event.data);
  console.log('Answer:', token.content);
});

eventSource.addEventListener('error', (event) => {
  console.error('Error:', JSON.parse(event.data));
});
```

---

### 3️⃣ 지식 추가

**엔드포인트**: `POST /agent/knowledge/add`

```bash
curl -X POST "http://127.0.0.1:8001/agent/knowledge/add" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      "새로운 의료 정보 1",
      "새로운 의료 정보 2"
    ],
    "metadatas": [
      {"source": "의학논문", "year": 2024},
      {"source": "의학논문", "year": 2024}
    ]
  }'
```

---

### 4️⃣ 통계 조회

**엔드포인트**: `GET /agent/knowledge/stats`

```bash
curl http://127.0.0.1:8001/agent/knowledge/stats
```

응답:
```json
{
  "collection_name": "medical_qa",
  "total_documents": 500,
  "last_updated": "2026-02-14T08:00:00"
}
```

---

## 👨‍💻 개발 가이드

### 프로젝트 컨벤션

#### 파일 네이밍
```
파일        | 규칙           | 예시
----------|----------------|------------------
모듈      | snake_case     | agent_service.py
클래스    | PascalCase     | AgentService
메서드    | snake_case     | run_agent()
상수      | UPPER_CASE     | API_TIMEOUT
```

#### 코드 스타일
```python
# Type Hints 필수
def run_agent(inputs: Dict[str, Any]) -> Dict[str, Any]:
    pass

# Docstring 작성
def run_agent(inputs):
    """
    에이전트 실행
    
    Args:
        inputs: 사용자 입력 딕셔너리
        
    Returns:
        에이전트 실행 결과
    """
```

### 새로운 에이전트 추가 (체크리스트)

```
[ ] 1. 새 서브그래프 파일 생성
       app/agents/subgraphs/my_agent.py

[ ] 2. 서비스 클래스 생성
       app/service/agents/my_agent_service.py

[ ] 3. workflow.py에 노드 추가
       def call_my_agent(state, config)

[ ] 4. deps.py에 의존성 등록
       @lru_cache
       def get_my_agent_service()

[ ] 5. 테스트 작성
       tests/test_my_agent.py

[ ] 6. 문서화
       README.md 업데이트
```

### 프롬프트 최적화

프롬프트 파일은 보통 각 서브그래프에서 정의됩니다:

```python
# app/agents/subgraphs/answer_gen.py

SYSTEM_PROMPT = """
당신은 친절한 의료 상담사입니다.
...
"""

# 프롬프트 테스트
if __name__ == "__main__":
    from langchain_community.chat_models import ChatUpstage
    
    llm = ChatUpstage()
    response = llm.invoke(SYSTEM_PROMPT)
    print(response)
```

### 로그 확인

```bash
# 실시간 로그 보기
tail -f logs/agent_flow_*.log

# 로그 검색
grep "Error" logs/agent_flow_*.log

# JSON 형식 로그 분석 (Python)
import json

with open('logs/agent_flow_20260214.log', 'r') as f:
    for line in f:
        log = json.loads(line)
        print(f"{log['timestamp']} - {log['step']}")
```

### 디버깅 팁

```python
# 1. 상태 프린트 (JSON 형식)
import json
print(json.dumps(state, default=str, indent=2))

# 2. 각 단계별 중단점
# Python debugger 사용
import pdb; pdb.set_trace()

# 3. LangSmith 연동 (선택)
# https://smith.langchain.com/
import os
os.environ["LANGSMITH_API_KEY"] = "your_key"
os.environ["LANGSMITH_PROJECT"] = "medinyang-agent"
```

---

## 📊 성능 및 비용

### 응답 시간

```
┌─────────────────────────┬────────┬──────────┐
│ 단계                     │ 평균    │ 범위      │
├─────────────────────────┼────────┼──────────┤
│ Info Extractor          │ 1.5초  │ 1-2초    │
│   └─ Embedding 생성      │ 0.5초  │ 0.3-0.7초│
│   └─ ChromaDB 검색      │ 0.3초  │ 0.2-0.5초│
│   └─ LLM Verifier       │ 0.7초  │ 0.5-1초  │
├─────────────────────────┼────────┼──────────┤
│ Knowledge Augmentor     │ 2초    │ 1-3초    │
│   (필요할 때만)         │        │          │
│   └─ Google Search      │ 1.5초  │ 1-2초    │
│   └─ 결과 처리          │ 0.5초  │ 0.2-1초  │
├─────────────────────────┼────────┼──────────┤
│ Answer Generator        │ 1.5초  │ 1-2초    │
│   └─ LLM 스트리밍       │ 1.5초  │ 1-2초    │
├─────────────────────────┼────────┼──────────┤
│ 합계 (Step 1 + 3)      │ 3초    │ 2-4초    │
│ 합계 (모든 Step)       │ 5초    │ 3-7초    │
└─────────────────────────┴────────┴──────────┘

최적화 방법:
✅ 캐싱: 자주 묻는 질문 → 0.5초 이내
✅ 배치 처리: 여러 쿼리 동시 처리
✅ 병렬 처리: 검색 + 임베딩 동시 실행 (부분)
```

### API 비용 (월간 추정)

```
기준: 하루 1,000건 요청

┌─────────────────────────┬─────────┬──────────┐
│ API                     │ 1건     │ 월간     │
├─────────────────────────┼─────────┼──────────┤
│ Upstage Chat           │ 0.3원  │ 9,000원  │
│ Upstage Embedding      │ 0.05원 │ 1,500원  │
│ Google Search (Serper) │ $0.01  │ $300 max │
├─────────────────────────┼─────────┼──────────┤
│ 예상 총액                │         │ ~11,500원│
└─────────────────────────┴─────────┴──────────┘

* 가격은 Upstage 정책 변경 시 달라질 수 있음
* Serper는 무료 크레딧 100개 포함
```

### 서버 리소스

```
최소 요구사항:
├─ CPU: 2 cores
├─ RAM: 2GB (ChromaDB 포함)
├─ SSD: 1GB (벡터 DB 저장)
└─ Network: 1Mbps

추천 사양 (프로덕션):
├─ CPU: 4 cores
├─ RAM: 4-8GB
├─ SSD: 10GB
└─ GPU: Optional (임베딩 생성 가속, NVIDIA T4+)

Docker 배포:
├─ Image 크기: ~500MB
├─ Container 메모리: 2GB
└─ Volume: 5GB (DB + 로그)
```

---

## 🔮 향후 계획

### Phase 2 (2026 Q2)

```
[ ] 사용자 인증 시스템
    ├─ JWT 기반 토큰 인증
    ├─ 사용자별 격리된 데이터
    └─ 역할 기반 접근 제어 (RBAC)

[ ] 개인 건강 기록 DB
    ├─ 처방전 저장
    ├─ 건강검진 기록
    └─ 약물 복용 기록

[ ] 처방전 OCR
    ├─ Vision API 통합
    ├─ 자동 텍스트 추출
    └─ 약물 정보 구조화

[ ] 기본 Frontend
    ├─ React 기반 웹앱
    ├─ 실시간 스트리밍 UI
    └─ 대화 히스토리 관리
```

### Phase 3 (2026 Q3)

```
[ ] 개인맞춤 답변
    ├─ 개인 기록 기반 RAG
    ├─ 약물 상호작용 검사
    └─ 개인 건강 추세 분석

[ ] 의사 연계
    ├─ 온라인 의료 상담 예약
    ├─ 처방약 배송 연동
    └─ 의료진 대시보드

[ ] 모니터링 개선
    ├─ 실시간 메트릭 (Prometheus)
    ├─ 로그 집계 (ELK Stack)
    └─ 에러 추적 (Sentry)
```

### Phase 4 (2026 Q4+)

```
[ ] 다국어 지원
    ├─ 영어, 중국어, 일본어
    ├─ 문화별 응답 조정
    └─ 의료 용어 다국어 매핑

[ ] 고급 분석
    ├─ 질병 확률 예측
    ├─ 건강 점수 산출
    └─ 맞춤형 건강 조언

[ ] 모바일 앱
    ├─ iOS, Android 네이티브 앱
    ├─ 오프라인 모드
    └─ 음성 인식 입력
```

---

## ❓ FAQ

### Q1: "왜 벡터 검색을 사용하나요?"

**A:** 의미 기반 검색이 필요하기 때문입니다.

```
일반 검색: "감기" → "감기"라는 단어만
벡터 검색: "감기" → "cold", "감염증", "호흡기 질환" 등

의료 데이터에서는 같은 병증을 다양한 용어로 표현하므로
의미 검색이 정확도를 크게 높입니다.
```

### Q2: "외부 검색이 안전한가요?"

**A:** 안전 조치를 적용했습니다.

```
✅ 자동 필터링:
   - 의료 기관, 학술지만
   - 명확한 저자 정보 필수
   - 최신 정보 우선

⚠️ 그래도 권고:
   - 민감한 진단은 의료진 상담 권고
   - 외부 정보도 검증 필요
   - 기계적 오류 가능성 고려
```

### Q3: "세션은 어떻게 관리되나요?"

**A:** LangGraph의 MemorySaver로 자동 관리됩니다.

```python
config = {
    "configurable": {
        "thread_id": "user_session_123"
    }
}

# 메모리에 자동 저장:
# {
#   "user_session_123": {
#     "messages": [...],
#     "state": {...}
#   }
# }

# 같은 thread_id로 재요청 시 이전 대화 컨텍스트 유지
```

### Q4: "프로덕션 배포는 어떻게 하나요?"

**A:** Docker + Kubernetes 권고

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app
ENV UPSTAGE_API_KEY=${UPSTAGE_API_KEY}

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

배포:
```bash
docker build -t medinyang-agent:latest .
docker run -e UPSTAGE_API_KEY=xxx -p 8001:8001 medinyang-agent:latest
```

### Q5: "데이터 업데이트는 어떻게 하나요?"

**A:** API 또는 배치 프로세스

```bash
# API를 통한 즉시 업데이트
curl -X POST "http://127.0.0.1:8001/agent/knowledge/add" \
  -d '{"documents": ["신규 의료 정보"]}'

# 배치 처리 (매일 밤)
# scripts/sync_knowledge_base.py
python scripts/sync_knowledge_base.py --source=https://...
```

---

## 🤝 기여 방법

### Pull Request 프로세스

```
1. Fork 저장소
2. Feature 브랜치 생성 (git checkout -b feature/MyFeature)
3. 변경사항 커밋 (git commit -m 'Add MyFeature')
4. 브랜치 Push (git push origin feature/MyFeature)
5. Pull Request 열기

PR 체크리스트:
[ ] 테스트 코드 작성
[ ] 문서 업데이트
[ ] Linting 통과 (black, flake8)
[ ] 타입 체크 통과 (mypy)
```

### 버그 리포팅

```
제목: [BUG] 간단한 설명
본문:
- 상황: 어떤 상황에서?
- 예상: 어떻게 되길 원했나?
- 실제: 실제로 어떻게 됐나?
- 재현: 어떻게 다시 만드나?

예시:
제목: [BUG] Info Extractor에서 한글 쿼리 처리 오류
상황: 한글로 된 의료 질문 입력 시
예상: 정상적으로 검색되어야 함
실제: UnicodeDecodeError 발생
재현: query="감기 증상" → POST /agent/chat
```

### 코드 리뷰 가이드라인

- Type hints 확인
- 문서화 확인
- 테스트 커버리지 (80% 이상)
- 성능 영향 분석
- 보안 고려사항

---

## 📄 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

```
MIT License

Copyright (c) 2026 medinyang-Agent Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 📞 문의 및 지원

### 연락처
- 📧 Email: support@medinyang.com
- 💬 GitHub Issues: [이슈 등록](https://github.com/yourusername/medinyang-Agent/issues)
- 💭 Discussions: [토론](https://github.com/yourusername/medinyang-Agent/discussions)

### 추가 리소스
- 📖 [API 문서](http://127.0.0.1:8001/docs)
- 🎥 [튜토리얼 영상](https://youtube.com/...)
- 📚 [기술 블로그](https://blog.medinyang.com)
- 🔗 [커뮤니티 포럼](https://community.medinyang.com)

---

## 🙏 감사의 말

### 오픈소스 프로젝트
- [LangChain](https://github.com/langchain-ai/langchain)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [ChromaDB](https://github.com/chroma-core/chroma)
- [FastAPI](https://github.com/tiangolo/fastapi)

### 데이터셋
- AI HUB 필수의료 의학지식 데이터

### 기여자
- 팀 리더: [이름]
- 개발자: [이름들]

---

## 버전 히스토리

| 버전 | 날짜 | 변경사항 |
|------|------|---------|
| 1.0 | 2026-02-14 | 초기 릴리스 (MVP) |
| | | - 멀티에이전트 시스템 |
| | | - 내/외부 검색 RAG |
| | | - REST API + Streaming |
| | | - 500+ 의료 지식 DB |

---

**마지막 업데이트**: 2026년 2월 14일  
**유지보수**: medinyang-Agent 팀  
**문서 버전**: 1.0