from __future__ import annotations

from typing import Any, Dict, List, Optional

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage

from app.agents.state import InfoBuildAgentState
from app.agents.tools import google_search, add_to_medical_qa, solar_chat
from app.agents.utils import get_current_time_str, clean_and_parse_json
from app.core.logger import log_agent_step


# -----------------------------
# Prompts
# -----------------------------
instruction_augment = """
You are the 'MedicalKnowledgeAugmentor'.
Goal: Search the web for medical information and produce ONE high-quality, concise note for our internal DB.

Workflow:
1) Use google_search(query) to find relevant info.
2) From the search result, select 1~2 sources with the highest credibility (official 기관/학회/대형병원/공공).
3) Summarize the best findings into 5~12 bullet points (Korean), include warnings/when-to-see-doctor if applicable.
4) Output ONLY the final note in Korean (no JSON, no tool call), then stop.
"""

instruction_filter = """
You are a 'SourceFilter'.
Input: raw web search result text (may include multiple snippets).
Task:
- Choose 1~2 high-credibility sources, prioritizing:
  1) 정부/공공기관(.go.kr, kdca, cdc 등)
  2) 학회/가이드라인(.or.kr, society)
  3) 대학병원/상급종합병원(.ac.kr, hospital)
  4) 의학 전문 매체
- Avoid random Q&A/커뮤니티/블로그 unless no alternative exists.
- Return STRICT JSON only:
{
  "selected": [
    {"title":"...", "domain":"...", "snippet":"..."},
    {"title":"...", "domain":"...", "snippet":"..."}
  ],
  "reason":"..."
}
- If you cannot reliably detect domains, still pick 1~2 best snippets and put domain as "unknown".
"""

instruction_quality_gate = """
You are a 'QualityGate' for medical notes saved into an internal KB.
You will receive a Korean bullet-note that may contain unsafe or overly strong wording.
Rules:
- Avoid diagnosing or prescribing.
- Avoid absolute terms like "반드시", "즉시" unless it's a general safety guidance.
- Prefer "의료기관 상담/진료를 권장" style.
Return STRICT JSON only:
{
  "pass": true|false,
  "reason": "...",
  "fixed_note": "..."   // required when pass=false and you can fix it
}
If the note is fine, pass=true and fixed_note can be "".
If it is not fixable, pass=false and fixed_note="".
"""


# -----------------------------
# Helpers
# -----------------------------
def _count_tool_calls(messages: list) -> dict:
    counts = {"google_search": 0, "add_to_medical_qa": 0}
    for m in messages:
        tcs = getattr(m, "tool_calls", None)
        if not tcs:
            continue
        for tc in tcs:
            name = tc.get("name")
            if name in counts:
                counts[name] += 1
    return counts


def _latest_tool_text(messages: list) -> Optional[str]:
    for msg in reversed(messages):
        if isinstance(msg, ToolMessage):
            return msg.content
    return None


# -----------------------------
# Nodes
# -----------------------------
# ✅ IMPORTANT: LLM에 bind_tools로 주는 도구는 google_search만!
augment_tools = [google_search]
llm_augment = solar_chat.bind_tools(augment_tools)


def augment_agent(state: InfoBuildAgentState):
    """
    - 검색이 필요하면 google_search tool_call만 하도록 유도
    - tool_call이 없으면 '요약 노트'를 content로 반환 (다음 노드: quality_gate)
    """
    messages = state["messages"]

    # tool 결과 요약 로깅
    if messages and isinstance(messages[-1], ToolMessage):
        last = messages[-1].content or ""
        log_agent_step("KnowledgeAugmentor", "Tool 결과 요약", {"summary": last[:200]})

    # System 주입
    if not messages or not isinstance(messages[0], SystemMessage):
        system = SystemMessage(content=f"현재 시각: {get_current_time_str()}\n\n{instruction_augment}")
        messages = [system] + messages

    counts = _count_tool_calls(messages)

    # 루프 방지
    if counts["google_search"] > 3:
        log_agent_step("KnowledgeAugmentor", "검색 호출 제한 도달 -> 종료", {"counts": counts})
        return {"messages": [AIMessage(content="(검색 제한 도달) 요약 생성을 중단합니다.")]}

    log_agent_step("KnowledgeAugmentor", "Augment 시작", {"messages": len(messages), "counts": counts})
    resp = llm_augment.invoke(messages)

    # ✅ tool_call 있으면 content 비움 (깔끔)
    if resp.tool_calls:
        if len(resp.tool_calls) > 1:
            log_agent_step(
                "KnowledgeAugmentor",
                "Multiple tool calls detected -> keep first only",
                {"first": resp.tool_calls[0]},
            )
            resp.tool_calls = resp.tool_calls[:1]
        resp.content = ""

    log_agent_step(
        "KnowledgeAugmentor",
        "응답 수신",
        {"tool_calls": resp.tool_calls, "content": (resp.content or "")[:200]},
    )
    return {"messages": [resp]}


def filter_sources(state: InfoBuildAgentState):
    """
    google_search 결과(ToolMessage)를 받아 고신뢰 1~2개 스니펫 JSON으로 압축
    """
    messages = state["messages"]
    latest = _latest_tool_text(messages)

    if not latest:
        log_agent_step("SourceFilter", "검색 결과 없음 -> 빈 selected")
        return {"messages": [AIMessage(content='{"selected":[],"reason":"no search result"}')]}

    system = SystemMessage(content=f"현재 시각: {get_current_time_str()}\n\n{instruction_filter}")
    prompt = [
        system,
        AIMessage(content=f"RAW_SEARCH_RESULT:\n{latest[:8000]}"),
    ]
    resp = solar_chat.invoke(prompt)

    log_agent_step("SourceFilter", "필터 결과", {"content": (resp.content or "")[:400]})
    return {"messages": [resp]}


def quality_gate(state: InfoBuildAgentState):
    """
    augment_agent가 만든 최종 노트(content)를 검증해서
    pass=false면 fixed_note 생성
    """
    messages = state["messages"]

    # 가장 마지막 AIMessage의 "노트" 후보 찾기 (tool_call 없는 AIMessage)
    note = None
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and not getattr(msg, "tool_calls", None):
            if msg.content and msg.content.strip():
                note = msg.content.strip()
                break

    if not note:
        log_agent_step("QualityGate", "노트 없음 -> 실패")
        return {"messages": [AIMessage(content='{"pass": false, "reason": "no note", "fixed_note": ""}')]}  # 안전

    system = SystemMessage(content=f"현재 시각: {get_current_time_str()}\n\n{instruction_quality_gate}")
    prompt = [
        system,
        AIMessage(content=f"NOTE:\n{note}"),
    ]
    resp = solar_chat.invoke(prompt)

    parsed = clean_and_parse_json(resp.content) or {}
    log_agent_step("QualityGate", "검증 결과", {"parsed": parsed})
    return {"messages": [resp]}


def save_note(state: InfoBuildAgentState):
    """
    ✅ pass=true면 원문 note 저장
    ✅ pass=false인데 fixed_note 있으면 fixed_note 저장
    """
    messages = state["messages"]

    # QualityGate 결과(JSON) 찾기
    gate = None
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            parsed = clean_and_parse_json(msg.content)
            if isinstance(parsed, dict) and "pass" in parsed:
                gate = parsed
                break

    # 원본 노트 찾기 (QualityGate 이전에 생성된 요약)
    original_note = None
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and not getattr(msg, "tool_calls", None):
            if msg.content and msg.content.strip():
                # gate JSON도 AIMessage라서 섞일 수 있음 → JSON이면 스킵
                if clean_and_parse_json(msg.content) is None:
                    original_note = msg.content.strip()
                    break

    if not gate:
        return {"messages": [AIMessage(content='{"status":"error","saved":false,"reason":"no quality gate"}')]}

    note_to_save = None
    if gate.get("pass") is True:
        note_to_save = original_note
        reason = "pass=true"
    else:
        fixed = (gate.get("fixed_note") or "").strip()
        if fixed:
            # fixed_note에 "NOTE:\n" prefix 붙는 경우가 있어서 제거
            note_to_save = fixed.replace("NOTE:\n", "").strip()
            reason = "pass=false but fixed_note saved"
        else:
            return {"messages": [AIMessage(content='{"status":"blocked","saved":false,"reason":"pass=false and no fixed_note"}')]}

    if not note_to_save:
        return {"messages": [AIMessage(content='{"status":"error","saved":false,"reason":"empty note"}')]}

    # 메타데이터 표준화
    meta = {
        "source": "augmentor_v4",
        "fetched_at": get_current_time_str().replace(" ", "T"),
    }

    # ✅ StructuredTool은 invoke로 호출해야 함
    try:
        cfg = {"configurable": state.get("configurable", {})}
        result = add_to_medical_qa.invoke(
            {"content": note_to_save, "metadata": meta, "config": cfg}
        )
        return {"messages": [AIMessage(content=f'{{"status":"success","saved":true,"reason":"{reason}","tool_result":"{result}"}}')]}
    except Exception as e:
        return {"messages": [AIMessage(content=f'{{"status":"error","saved":false,"reason":"{str(e)}"}}')]}



# -----------------------------
# Routing
# -----------------------------
def route_after_augment_agent(state: InfoBuildAgentState):
    """
    augment_agent 출력이 tool_call이면 tools로,
    아니면 quality_gate로 (END로 떨어지지 않게 강제)
    """
    last = state["messages"][-1]
    if getattr(last, "tool_calls", None):
        return "tools"
    return "quality_gate"


def route_after_tools(state: InfoBuildAgentState):
    """
    tools 실행 후:
    - google_search 결과면 filter_sources로 가고
    - filter_sources 끝나면 augment_agent로 돌아가 요약 생성하게 함
    """
    return "filter_sources"


def route_after_quality_gate(state: InfoBuildAgentState):
    """
    QualityGate 후엔 무조건 save_note로
    """
    return "save_note"


# -----------------------------
# Graph
# -----------------------------
workflow = StateGraph(InfoBuildAgentState)

workflow.add_node("augment_agent", augment_agent)
workflow.add_node("augment_tools", ToolNode(augment_tools))  # google_search only
workflow.add_node("filter_sources", filter_sources)
workflow.add_node("quality_gate", quality_gate)
workflow.add_node("save_note", save_note)

workflow.set_entry_point("augment_agent")

# ✅ 핵심: should_continue 삭제하고 route_after_augment_agent만 사용
workflow.add_conditional_edges(
    "augment_agent",
    route_after_augment_agent,
    {
        "tools": "augment_tools",
        "quality_gate": "quality_gate",
    },
)

# tools -> filter -> augment (요약 생성)
workflow.add_conditional_edges("augment_tools", route_after_tools, {"filter_sources": "filter_sources"})
workflow.add_edge("filter_sources", "augment_agent")

# quality_gate -> save -> END
workflow.add_conditional_edges("quality_gate", route_after_quality_gate, {"save_note": "save_note"})
workflow.add_edge("save_note", END)

knowledge_augment_graph = workflow.compile()




