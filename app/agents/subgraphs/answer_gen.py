# app/agents/subgraphs/answer_gen.py
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage

from app.agents.state import AnswerGenAgentState
from app.agents.tools import solar_chat
from app.agents.utils import get_current_time_str
from app.core.logger import log_agent_step

instruction_answer_gen = """
You are an expert Medical Consultant.
Your goal is to provide a helpful, accurate, and empathetic medical consultation based on the provided context.

# Guidelines:
1. Tone: Empathetic, professional, and clear.
2. Language: Korean.
3. Constraint: Do NOT provide a definitive diagnosis. Always include a disclaimer:
   - "본 답변은 일반적인 정보 제공 목적이며, 정확한 진단/치료는 의료진 상담이 필요합니다."
4. Context: Use the provided medical QA context to support your advice.
5. Out of Domain: If the user's query is not related to medical or health topics,
   politely inform them you can only provide medical consultations.

# 🔒 Safety Guard (VERY IMPORTANT):
- Avoid absolute or commanding expressions such as "반드시", "즉시", "무조건".
  Prefer softer terms like "권장됩니다", "고려할 수 있습니다".
- If mentioning numeric values (e.g., temperature, dosage, intake amount),
  clearly state that they may vary depending on individual condition.
- Carefully check for typos or grammatical errors before answering.
"""

def answer_gen_agent(state: AnswerGenAgentState):
    messages = state["messages"]

    # System 주입
    if not messages or not isinstance(messages[0], SystemMessage):
        current_time = get_current_time_str()
        system_content = f"현재 시각: {current_time}\n\n{instruction_answer_gen}"
        messages = [SystemMessage(content=system_content)] + messages

    log_agent_step("MedicalConsultant", "답변 생성 시작", {"messages": len(messages)})
    response = solar_chat.invoke(messages)
    log_agent_step("MedicalConsultant", "답변 생성 완료", {"answer_snip": (response.content or "")[:300]})
    return {"messages": [response]}

workflow = StateGraph(AnswerGenAgentState)
workflow.add_node("answer_gen_agent", answer_gen_agent)
workflow.set_entry_point("answer_gen_agent")
workflow.add_edge("answer_gen_agent", END)

answer_gen_graph = workflow.compile()
