# app/service/agents/chat_filter_service.py

from typing import Dict, Any, List, Optional

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.runnables import RunnableConfig

from app.agents.subgraphs.chat_filter import chat_filter_graph
from app.agents.utils import clean_and_parse_json
from app.exceptions import AgentException

class ChatFilterService:
    def run(
        self,
        user_query: str,
        config: Optional[RunnableConfig] = None,
        history: Optional[List[BaseMessage]] = None,
    ) -> Dict[str, Any]:

        messages: List[BaseMessage] = []

        if history:
            messages.extend(history)

        messages.append(HumanMessage(content=user_query))
        
        # subgraph 실행
        result = chat_filter_graph.invoke(
            {"messages": messages}
        )

        return {
            "next": result["next"],
            "confidence": result["confidence"],
            "reason": result["reason"],
        }