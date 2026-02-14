# app/service/agents/answer_gen_service.py
from typing import Dict, Any, List, Optional

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.runnables import RunnableConfig

from app.agents.subgraphs.answer_gen import answer_gen_graph
from app.agents.utils import clean_and_parse_json


class AnswerGenService:
    def run(
        self,
        user_query: str,
        extract_logs: List[BaseMessage],
        config: Optional[RunnableConfig] = None,
        history: Optional[List[BaseMessage]] = None,
    ) -> Dict[str, Any]:

        if not extract_logs:
            return {
                "answer_logs": [AIMessage(content="내부 정보 추출에 실패했습니다. 잠시 후 다시 시도해 주세요.")],
                "process_status": "fail",
            }

        last_extract_msg = extract_logs[-1]
        parsed_result = clean_and_parse_json(getattr(last_extract_msg, "content", "") or "")

        status = (parsed_result.get("status") if parsed_result else "unknown") or "unknown"
        medical_context = (parsed_result.get("medical_context") if parsed_result else "") or ""
        key_points = (parsed_result.get("key_points") if parsed_result else []) or []

        if status == "out_of_domain":
            prompt = f"""User Query: "{user_query}"

Task:
- You are a medical AI assistant.
- The user's query is unrelated to medical or health topics.
- Explain politely (Korean) that you can only help with medical/health topics.
- Offer to help if they ask a health-related question.
- Keep it concise and professional.
"""
        else:
            extra_guidance = ""
            if status == "insufficient":
                extra_guidance = """
Additional Guidance:
- The context may be insufficient. Provide safe, general guidance.
- Add 3~5 follow-up questions to clarify symptoms (duration, fever, breathing, risk group).
- Avoid definitive diagnosis. Encourage medical consultation for red flags.
"""

            prompt = f"""User Query: "{user_query}"

Retrieved Medical Context:
===
{medical_context}
===

Key Points (if any):
{key_points}

Task:
- Provide a medical consultation based on the context and key points.
- Use Korean.
- Be empathetic and practical.
- Include red flags and when to seek medical care.
- Include the disclaimer that this is informational only and consult a real doctor.
{extra_guidance}
"""

        messages: List[BaseMessage] = []
        if history:
            safe_history: List[BaseMessage] = []
            for msg in history:
                if isinstance(msg, AIMessage) and getattr(msg, "tool_calls", None):
                    continue
                safe_history.append(msg)
            messages.extend(safe_history)

        messages.append(HumanMessage(content=prompt))

        sub_result = answer_gen_graph.invoke({"messages": messages}, config=config)

        history_len = len(messages)
        new_messages = [
            msg for msg in sub_result["messages"][history_len:]
            if isinstance(msg, AIMessage)
        ]

        return {
            "answer_logs": new_messages,
            "process_status": "success",
        }
