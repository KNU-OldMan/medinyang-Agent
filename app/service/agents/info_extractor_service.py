from __future__ import annotations

from typing import Any, Dict, List, Optional

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from app.agents.subgraphs.info_extractor import info_extract_graph


class InfoExtractorService:
    def run(
        self,
        user_query: str,
        build_logs: Optional[List[BaseMessage]] = None,
        config: Optional[RunnableConfig] = None,
        history: Optional[List[BaseMessage]] = None,
    ) -> Dict[str, Any]:
        handoff_msg = (
            f'Original User Query: "{user_query}"\n\n'
            "Please search the internal database first. "
            "Refer to the previous conversation history if it helps."
        )

        if build_logs:
            handoff_msg += f"\nPrevious context: {build_logs[-1].content}"

        messages: List[BaseMessage] = []
        if history:
            messages.extend(history)
        messages.append(HumanMessage(content=handoff_msg))

        sub_result = info_extract_graph.invoke({"messages": messages}, config=config)

        history_len = len(messages)
        new_messages = [
            msg
            for msg in sub_result["messages"][history_len:]
            if isinstance(msg, AIMessage)
        ]

        return {"extract_logs": new_messages, "process_status": "success"}
