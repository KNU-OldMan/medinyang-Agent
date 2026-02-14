# app/agents/subgraphs/chat_filter.py
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage

from app.agents.state import ChatFilterState
from app.agents.tools import solar_chat
from app.agents.utils import clean_and_parse_json
from app.exceptions import AgentException

system_prompt = """
You are a routing filter that selects the most appropriate response engine based on the user's message.

Your task is to analyze the user's conversation content and decide which engine should generate the next response.

# ROLE

You classify user messages into one of the following engines:

1. MEDICAL_ENGINE
2. MEDICAL_CHAT
3. DAILY_CHAT


# ENGINE DEFINITIONS

## MEDICAL_ENGINE
Select this when the user requires:
- Professional or factual medical knowledge
- Evidence-based medical explanations
- Diagnosis-related or clinical interpretation
- Drug, treatment, pathology, or medical guideline information
- Situations where accurate medical knowledge is more important than conversational empathy
- Queries requiring external medical knowledge retrieval or search


## MEDICAL_CHAT
Select this when:
- The conversation includes medical or health-related topics
- Emotional support, symptom sharing, or light medical consultation is the main intent
- Conversational context and empathy are more important than professional medical accuracy


## DAILY_CHAT
Select this when:
- No medical or health-related content is present
- The conversation is general, casual, or unrelated to healthcare


# DECISION GUIDELINES

1. If professional medical knowledge or accuracy is clearly required → MEDICAL_ENGINE
2. If medical context exists but conversational support is more important → MEDICAL_CHAT
3. If no medical context exists → DAILY_CHAT

If the user message contains both medical and non-medical content:
- Prioritize medical classification.

If uncertainty exists:
- Choose the safest medical classification.
- MEDICAL_CHAT is preferred over DAILY_CHAT when health context is present.


# CONFIDENCE SCORING

Return a floating point value between 0 and 1.


# OUTPUT FORMAT (STRICT)

Return ONLY valid JSON.

{{
  "next": "MEDICAL_ENGINE | MEDICAL_CHAT | DAILY_CHAT",
  "confidence": float,
  "reason": "Brief explanation of classification decision"
}}
"""

def chat_filter_agent(state: ChatFilterState):
    messages = state["messages"]

    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=system_prompt)] + messages

    response = solar_chat.invoke(messages)

    parsed = clean_and_parse_json(response.content or "")

    if not parsed:
        raise AgentException("Filter parsing failed")

    return {
        "messages": [response],
        "next": parsed.get("next", "MEDICAL_CHAT"),
        "confidence": parsed.get("confidence", 0.0),
        "reason": parsed.get("reason", "")
    }

workflow = StateGraph(ChatFilterState)

workflow.add_node("chat_filter_agent", chat_filter_agent)
workflow.set_entry_point("chat_filter_agent")
workflow.add_edge("chat_filter_agent", END)

chat_filter_graph = workflow.compile()
