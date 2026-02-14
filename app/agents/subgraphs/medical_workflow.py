# app/agents/subgraphs/medical_workflow.py
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig

from app.agents.state import MainState
from app.agents.utils import clean_and_parse_json
from app.core.logger import log_agent_step


def _get_service(config: RunnableConfig, key: str):
    cfg = (config or {}).get("configurable", {})
    svc = cfg.get(key)
    if svc is None:
        raise ValueError(f"{key} not found in config['configurable']")
    return svc


# -------------------------
# Nodes
# -------------------------

def call_info_extractor(state: MainState, config: RunnableConfig):
    log_agent_step("MedicalWorkflow", "Step 1: InfoExtractor 시작")

    info_extractor_service = _get_service(config, "info_extractor_service")

    current_count = state.get("loop_count", 0) + 1

    result = info_extractor_service.run(
        user_query=state["user_query"],
        build_logs=state.get("augment_logs", []),
        config=config,
        history=state.get("answer_logs", []),
    )

    result["loop_count"] = current_count
    return result


def call_knowledge_augmentor(state: MainState, config: RunnableConfig):
    log_agent_step("MedicalWorkflow", "Step 2: KnowledgeAugmentor 시작")

    svc = _get_service(config, "knowledge_augmentor_service")

    return svc.run(
        query=state["user_query"],
        config=config,
        history=state.get("answer_logs", []),
    )


def call_answer_gen(state: MainState, config: RunnableConfig):
    log_agent_step("MedicalWorkflow", "Step 3: AnswerGen 시작")

    svc = _get_service(config, "answer_gen_service")

    return svc.run(
        user_query=state["user_query"],
        extract_logs=state.get("extract_logs", []),
        config=config,
        history=state.get("answer_logs", []),
    )


# -------------------------
# Router inside medical
# -------------------------

def check_extract_status(state: MainState):

    if not state.get("extract_logs"):
        return "augment"

    last_msg = state["extract_logs"][-1].content
    parsed = clean_and_parse_json(last_msg)
    status = parsed.get("status") if parsed else "unknown"

    loop_count = state.get("loop_count", 1)

    if status in ("success", "out_of_domain"):
        return "continue"

    if loop_count >= 2:
        return "continue"

    return "augment"


# -------------------------
# Graph Build
# -------------------------

medical_workflow = StateGraph(MainState)

medical_workflow.add_node("info_extract", call_info_extractor)
medical_workflow.add_node("augment", call_knowledge_augmentor)
medical_workflow.add_node("answer_gen", call_answer_gen)

medical_workflow.set_entry_point("info_extract")

medical_workflow.add_conditional_edges(
    "info_extract",
    check_extract_status,
    {
        "continue": "answer_gen",
        "augment": "augment",
    },
)

medical_workflow.add_edge("augment", "info_extract")
medical_workflow.add_edge("answer_gen", END)

medical_subgraph = medical_workflow.compile()
