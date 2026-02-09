from __future__ import annotations

from typing import Any, Dict, List

from langchain_core.messages import AIMessage, BaseMessage, SystemMessage, ToolMessage
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from app.agents.state import InfoExtractAgentState
from app.agents.tools import search_medical_qa, solar_chat
from app.agents.utils import clean_and_parse_json, get_current_time_str
from app.core.logger import log_agent_step

# ---------------------------
# Prompts
# ---------------------------

instruction_info_extract = """
You are the 'MedicalInfoExtractor'. Your goal is to gather medical context for
the user's query from our internal Korean-language medical knowledge base.

# Workflow
1. **Internal Search**: Use `search_medical_qa(query)` to find relevant information.
2. **Review**: Look at the results and decide if more search is needed.
3. **Finish**: When you have enough raw information, stop and let the 'MedicalInfoVerifier' evaluate it.
"""

instruction_info_verify = """
You are the 'MedicalInfoVerifier'. Your goal is to evaluate the medical information
gathered by the extractor and determine if it's sufficient to answer the user's query.

# Input
- User's original query.
- Retrieved documents from the internal database.

# Evaluation Criteria
1. **Domain Check**: Is the user's query related to medical or health topics?
   - If NOT medical-related, set "status" to "out_of_domain".
2. **Sufficiency Check**: If it IS a medical query, does the information directly address it?
   - If sufficient, set "status" to "success".
   - If insufficient, set "status" to "insufficient".

# Output Format (STRICT)
Return JSON only:
{
  "status": "success" | "insufficient" | "out_of_domain",
  "medical_context": "...",
  "key_points": ["point1", "point2", ...]
}
Do NOT output anything else.
"""

# ---------------------------
# Tool binding
# ---------------------------

info_extract_tools = [search_medical_qa]
llm_info_extract = solar_chat.bind_tools(info_extract_tools)


# ---------------------------
# Nodes
# ---------------------------

def info_extractor(state: InfoExtractAgentState) -> Dict[str, List[BaseMessage]]:
    messages = state["messages"]

    # 1) last tool result logging
    if messages and isinstance(messages[-1], ToolMessage):
        content = messages[-1].content or ""
        if "Source 1" in content:
            sources = content.split("Source ")[1:]
            summary = {
                "count": len(sources),
                "snippets": [
                    (s.split("\n", 1)[1][:30].strip() if "\n" in s else s[:30].strip())
                    for s in sources
                ],
            }
            log_agent_step("MedicalInfoExtractor", "VectorDB 검색 결과 요약", summary)

    # 2) inject system prompt on first run
    if not messages or not isinstance(messages[0], SystemMessage):
        current_time = get_current_time_str()
        system_content = f"현재 시각: {current_time}\n\n{instruction_info_extract}"
        messages = [SystemMessage(content=system_content)] + messages

    # 3) invoke LLM (may call tool)
    log_agent_step("MedicalInfoExtractor", "검색 에이전트 시작", {"messages": len(messages)})
    response = llm_info_extract.invoke(messages)

    # 4) safety: keep only first tool call
    if getattr(response, "tool_calls", None) and len(response.tool_calls) > 1:
        response.tool_calls = response.tool_calls[:1]
        log_agent_step("MedicalInfoExtractor", "다중 도구 호출 감지 -> 첫 호출만 유지")

    # 5) log
    if getattr(response, "tool_calls", None):
        log_agent_step("MedicalInfoExtractor", "도구 호출 응답 수신", {"tool_calls": response.tool_calls})
    else:
        log_agent_step(
            "MedicalInfoExtractor",
            "검색 및 추출 완료",
            {"content": (response.content or "")[:120]},
        )

    return {"messages": [response]}


def info_verifier(state: InfoExtractAgentState) -> Dict[str, List[BaseMessage]]:
    messages = state["messages"]

    current_time = get_current_time_str()
    system_content = f"현재 시각: {current_time}\n\n{instruction_info_verify}"
    verify_messages = [SystemMessage(content=system_content)] + messages

    log_agent_step("MedicalInfoVerifier", "검증 시작")
    response = solar_chat.invoke(verify_messages)

    parsed = clean_and_parse_json(response.content or "")
    if parsed:
        log_agent_step("MedicalInfoVerifier", "검증 완료", {"status": parsed.get("status")})
    else:
        log_agent_step("MedicalInfoVerifier", "검증 완료 (파싱 실패)", {"raw": (response.content or "")[:200]})

    return {"messages": [response]}


def no_results_handler(state: InfoExtractAgentState) -> Dict[str, List[BaseMessage]]:
    log_agent_step("MedicalInfoExtractor", "내부 검색 결과 없음 -> 도메인 확인 시작")
    current_time = get_current_time_str()

    # 가장 최근 HumanMessage(사용자 질문) 찾기
    user_query = ""
    for msg in reversed(state["messages"]):
        if isinstance(msg, BaseMessage) and getattr(msg, "type", None) == "human":
            user_query = msg.content
            break

    domain_check_prompt = f"""현재 시각: {current_time}

Evaluate if the following user query is related to medical or health topics.

Query: {user_query}

Output strictly in JSON:
{{"status": "out_of_domain" | "insufficient"}}

If it IS medical but no info was found, use "insufficient".
If it is NOT medical, use "out_of_domain".
"""

    response = solar_chat.invoke(domain_check_prompt)
    parsed = clean_and_parse_json(response.content or "")
    if parsed:
        log_agent_step("MedicalInfoExtractor", "도구 결과 없음 - 도메인 확인 결과", {"status": parsed.get("status")})

    return {"messages": [response]}


# ---------------------------
# Conditional edge
# ---------------------------

def should_continue(state: InfoExtractAgentState) -> str:
    messages = state["messages"]
    last_message = messages[-1]

    # loop breaker
    tool_call_count = sum(1 for m in messages if getattr(m, "tool_calls", None))
    if tool_call_count > 3:
        log_agent_step("MedicalInfoExtractor", "도구 호출 횟수 초과 -> verify로 강제 종료")
        return "verify"

    # tool call -> tools
    if getattr(last_message, "tool_calls", None):
        return "tools"

    # detect empty tool results / error
    for msg in reversed(messages):
        if isinstance(msg, ToolMessage):
            content = (msg.content or "").strip()
            if content == "" or content.startswith("Search Error") or content.startswith("Error"):
                return "no_results"
            break

    return "verify"


# ---------------------------
# Graph compile
# ---------------------------

workflow = StateGraph(InfoExtractAgentState)
workflow.add_node("info_extractor", info_extractor)
workflow.add_node("info_extract_tools", ToolNode(info_extract_tools))
workflow.add_node("info_verifier", info_verifier)
workflow.add_node("no_results_handler", no_results_handler)

workflow.set_entry_point("info_extractor")

workflow.add_conditional_edges(
    "info_extractor",
    should_continue,
    {
        "tools": "info_extract_tools",
        "verify": "info_verifier",
        "no_results": "no_results_handler",
    },
)

workflow.add_edge("info_extract_tools", "info_extractor")
workflow.add_edge("info_verifier", END)
workflow.add_edge("no_results_handler", END)

info_extract_graph = workflow.compile()
