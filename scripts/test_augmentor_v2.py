from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from app.deps import build_vector_service
from app.agents.subgraphs.knowledge_augmentor import knowledge_augment_graph


def main():
    # VectorService를 config로 주입 (add_to_medical_qa / search_medical_qa가 이걸 씀)
    vs = build_vector_service()
    cfg = RunnableConfig(configurable={"vector_service": vs})

    query = "감기 해열제 복용 시기와 병원 방문이 필요한 경고 증상"

    # 그래프 입력
    state = {
        "messages": [HumanMessage(content=query)]
    }

    result = knowledge_augment_graph.invoke(state, config=cfg)

    print("\n=== GRAPH OUTPUT MESSAGES ===")
    for m in result["messages"]:
        role = m.__class__.__name__
        content = (m.content or "").strip()
        if content:
            print(f"\n[{role}]\n{content[:800]}")
        else:
            # tool calls도 같이 확인
            tcs = getattr(m, "tool_calls", None)
            if tcs:
                print(f"\n[{role}] tool_calls={tcs}")

    # DB 반영 확인
    print("\n=== DB SEARCH CHECK ===")
    print(vs.search("감기 해열제", n_results=3))


if __name__ == "__main__":
    main()
