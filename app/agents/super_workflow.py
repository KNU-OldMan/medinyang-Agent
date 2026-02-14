# app/agents/super_workflow.py
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig

from app.agents.state import MainState
from app.core.logger import log_agent_step

from app.agents.subgraphs.medical_workflow import medical_subgraph


# -------------------------
# Service Helper
# -------------------------

def _get_service(config: RunnableConfig, key: str):
    cfg = (config or {}).get("configurable", {})
    svc = cfg.get(key)
    if svc is None:
        raise ValueError(f"{key} not found in config['configurable']")
    return svc


# -------------------------
# Filter Node
# -------------------------

def chat_filter_node(state: MainState, config: RunnableConfig):

    log_agent_step("SuperWorkflow", "Chat Filter 시작")

    svc = _get_service(config, "chat_filter_service")

    result = svc.run(
        user_query=state["user_query"],
        config=config,
        history=state.get("answer_logs", []),
    )

    # routing 결과 state에 저장
    return {
        "route_engine": result["next"],
        "route_confidence": result["confidence"],
        "route_reason": result["reason"],
    }


# -------------------------
# Router
# -------------------------

def router_node(state: MainState):

    engine = state.get("route_engine", "MEDICAL_CHAT")

    if engine == "MEDICAL_ENGINE":
        return "medical"

    if engine == "MEDICAL_CHAT":
        return "medical_chat"

    return "daily_chat"


# -------------------------
# Placeholder Chat Nodes
# -------------------------

def medical_chat_node(state: MainState, config: RunnableConfig):
    # TODO: 실제 medical_chat_subgraph 붙이기
    return {
        "answer_logs": [],
        "process_status": "medical_chat_placeholder",
    }


def daily_chat_node(state: MainState, config: RunnableConfig):
    # TODO: 실제 daily_chat_subgraph 붙이기
    return {
        "answer_logs": [],
        "process_status": "daily_chat_placeholder",
    }


# -------------------------
# Graph Build
# -------------------------

super_workflow = StateGraph(MainState)

super_workflow.add_node("chat_filter", chat_filter_node)

# subgraph도 node처럼 사용 가능
super_workflow.add_node("medical_workflow", medical_subgraph)
super_workflow.add_node("medical_chat_workflow", medical_chat_node)
super_workflow.add_node("daily_chat_workflow", daily_chat_node)

super_workflow.set_entry_point("chat_filter")

super_workflow.add_conditional_edges(
    "chat_filter",
    router_node,
    {
        "medical": "medical_workflow",
        "medical_chat": "medical_chat_workflow",
        "daily_chat": "daily_chat_workflow",
    },
)

super_workflow.add_edge("medical_workflow", END)
super_workflow.add_edge("medical_chat_workflow", END)
super_workflow.add_edge("daily_chat_workflow", END)

memory = MemorySaver()

super_graph = super_workflow.compile(checkpointer=memory)
