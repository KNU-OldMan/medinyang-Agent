from langchain_core.messages import HumanMessage
from app.agents.subgraphs.knowledge_augmentor import knowledge_augment_graph
from app.deps import build_vector_service

def main():
    vs = build_vector_service()
    cfg = {"configurable": {"vector_service": vs}}

    query = "감기 해열제 복용 시기와 병원 방문이 필요한 경고 증상"
    res = knowledge_augment_graph.invoke({"messages": [HumanMessage(content=query)]}, config=cfg)

    print("\n=== GRAPH OUTPUT ===")
    for m in res["messages"]:
        print("\n---", type(m).__name__, "---")
        print((m.content or "")[:800])

    print("\n=== DB CHECK ===")
    print(vs.search("해열제", n_results=3))

if __name__ == "__main__":
    main()
