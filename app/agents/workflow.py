from __future__ import annotations

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig

from app.agents.state import MainState
from app.core.logger import log_agent_step
from app.agents.utils import clean_and_parse_json


def _get_service(config: RunnableConfig, key: str):
    """
    config["configurable"] 안에서 서비스를 꺼냄.
    (DI 누락 시 빠르게 에러를 내서 디버깅 쉽게)
    """
    cfg = (config or {}).get("configurable", {})
    svc = cfg.get(key)
    if svc is None:
        raise ValueError(f"{key} not found in config['configurable']")
    return svc


# 1) Info Extractor 호출 노드
def call_info_extractor(state: MainState, config: RunnableConfig):
    log_agent_step("Workflow", "Step 1: MedicalInfoExtractor 시작 (RAG)")
    print(f"\n[Workflow] Step 1: MedicalInfoExtractor 시작 (Query: {state['user_query']})")

    info_extractor_service = _get_service(config, "info_extractor_service")

    current_count = state.get("loop_count", 0) + 1

    result = info_extractor_service.run(
        user_query=state["user_query"],
        build_logs=state.get("augment_logs", []),     # Augment에서 쌓인 로그를 참고 컨텍스트로
        config=config,
        history=state.get("answer_logs", []),         # Answer 히스토리(체크포인터로 누적)
    )

    result["loop_count"] = current_count

    # 상태 요약 로깅
    if result.get("extract_logs"):
        last_msg = result["extract_logs"][-1].content
        parsed = clean_and_parse_json(last_msg)
        status = parsed.get("status") if parsed else "unknown"
        log_agent_step("Workflow", f"Step 1 완료 (반복: {current_count})", {"status": status})
        print(f"[Workflow] Step 1 완료. Status: {status}, Iteration: {current_count}")

    return result


# 2) Knowledge Augmentor 호출 노드
def call_knowledge_augmentor(state: MainState, config: RunnableConfig):
    log_agent_step("Workflow", "Step 2: MedicalKnowledgeAugmentor 시작 (Google Search)")
    print("\n[Workflow] Step 2: MedicalKnowledgeAugmentor 시작")

    knowledge_augmentor_service = _get_service(config, "knowledge_augmentor_service")

    result = knowledge_augmentor_service.run(
        query=state["user_query"],
        config=config,
        history=state.get("answer_logs", []),
    )

    log_agent_step("Workflow", "Step 2 완료")
    print("[Workflow] Step 2 완료. 지식 보강됨.")
    return result


# 3) Answer Generator 호출 노드
def call_answer_gen(state: MainState, config: RunnableConfig):
    log_agent_step("Workflow", "Step 3: MedicalConsultant 시작")
    print("\n[Workflow] Step 3: MedicalConsultant (AnswerGen) 시작")

    answer_gen_service = _get_service(config, "answer_gen_service")

    result = answer_gen_service.run(
        user_query=state["user_query"],
        extract_logs=state.get("extract_logs", []),
        config=config,
        history=state.get("answer_logs", []),
    )

    log_agent_step("Workflow", "Step 3 완료")
    if result.get("answer_logs"):
        print("[Workflow] Step 3 완료. 답변 생성됨.")
    return result


def check_extract_status(state: MainState):
    """
    Extractor의 마지막 Verifier(JSON) status로 다음 흐름을 결정
    - success / out_of_domain -> answer_gen
    - insufficient -> augment (단, loop_count 제한)
    """
    if not state.get("extract_logs"):
        return "augment"

    last_msg = state["extract_logs"][-1].content
    parsed = clean_and_parse_json(last_msg)
    status = parsed.get("status") if parsed else "unknown"

    loop_count = state.get("loop_count", 1)

    if status == "out_of_domain":
        log_agent_step("Workflow", "도메인 외 질문 -> 답변 생성 이동")
        return "continue"

    if status == "success":
        return "continue"

    # 최대 반복 제한 (여기 값은 원하는대로 조정)
    if loop_count >= 2:
        log_agent_step("Workflow", f"최대 반복({loop_count}) 도달 -> 답변 생성 이동", {"reason": "iteration limit"})
        return "continue"

    log_agent_step("Workflow", "내부 지식 부족 -> Google 검색 이동", {
        "reason": parsed.get("reason") if parsed else "parse error",
        "iteration": loop_count,
    })
    return "augment"


def router_node(state: MainState):
    # 지금은 무조건 medical 라우팅 (추후 router 추가 가능)
    return "medical"


# --- Super Graph ---
super_workflow = StateGraph(MainState)

super_workflow.add_node("info_extract_agent_workflow", call_info_extractor)
super_workflow.add_node("knowledge_augment_workflow", call_knowledge_augmentor)
super_workflow.add_node("answer_gen_agent_workflow", call_answer_gen)

super_workflow.set_conditional_entry_point(
    router_node,
    {"medical": "info_extract_agent_workflow"},
)

super_workflow.add_conditional_edges(
    "info_extract_agent_workflow",
    check_extract_status,
    {
        "continue": "answer_gen_agent_workflow",
        "augment": "knowledge_augment_workflow",
    },
)

super_workflow.add_edge("knowledge_augment_workflow", "info_extract_agent_workflow")
super_workflow.add_edge("answer_gen_agent_workflow", END)

# 체크포인터(메모리)
memory = MemorySaver()
super_graph = super_workflow.compile(checkpointer=memory)
