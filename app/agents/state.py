from typing import TypedDict, Annotated, List

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class InfoBuildAgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]


class InfoExtractAgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]


class AnswerGenAgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]


class MainState(TypedDict):
    user_query: str
    
    # routing
    route_next: str
    route_confidence: float
    route_reason: str

    # medical pipline logs
    answer_logs: Annotated[List[BaseMessage], add_messages]
    extract_logs: List[BaseMessage]
    augment_logs: List[BaseMessage]

    build_logs: List[BaseMessage]
    process_status: str
    loop_count: int

class ChatFilterState(TypedDict, total=False):
    message: List[BaseMessage]

    next: str
    confidence: float
    reason: str
