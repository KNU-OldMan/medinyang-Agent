from langchain_core.runnables import RunnableConfig

from app.deps import build_vector_service
from app.service.agents.knowledge_augmentor_service import KnowledgeAugmentorService

def main():
    vs = build_vector_service()
    cfg = RunnableConfig(configurable={"vector_service": vs})

    svc = KnowledgeAugmentorService()
    out = svc.run("감기 걸렸을 때 해열제는 언제 먹어야 하나요? 병원 가야 하는 기준도 알려줘", config=cfg)

    print("=== AUGMENT LOGS ===")
    for m in out["augment_logs"]:
        print(m.content)

    print("\n=== DB SEARCH CHECK ===")
    print(vs.search("감기 해열제 복용 기준", n_results=3))

if __name__ == "__main__":
    main()
