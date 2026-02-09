from langchain_core.messages import HumanMessage
from app.agents.subgraphs.info_extractor import info_extract_graph
from app.deps import build_vector_service

# 1) DB 준비
vs = build_vector_service()
vs.add_documents(
    ["감기에는 휴식과 수분 섭취가 중요합니다."],
    metadatas=[{"source": "test"}],
)

# 2) 그래프 실행 (중요: config에 vector_service 주입)
cfg = {"configurable": {"vector_service": vs}}

result = info_extract_graph.invoke(
    {"messages": [HumanMessage(content="감기 걸렸을 때 어떻게 해야 해?")]},
    config=cfg,
)

print("=== MESSAGES ===")
for m in result["messages"]:
    print(type(m).__name__, ":", (m.content or "")[:300])
