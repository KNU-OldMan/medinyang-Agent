from app.deps import (
    build_vector_service,
    get_info_extractor_service,
    get_knowledge_augmentor_service,
    get_answer_gen_service,
)
from app.service.agent_service import AgentService


def main():
    vs = build_vector_service()

    agent = AgentService(
        vector_service=vs,
        info_extractor_service=get_info_extractor_service(),
        knowledge_augmentor_service=get_knowledge_augmentor_service(),
        answer_gen_service=get_answer_gen_service(),
    )

    session_id = "demo-session-1"

    print("\n=== RUN 1 ===")
    r1 = agent.run_agent({"user_query": "감기 걸렸을 때 어떻게 해야 해?"}, session_id=session_id)
    print(r1.get("answer_logs", [])[-1].content if r1.get("answer_logs") else r1)

    print("\n=== RUN 2 (same session) ===")
    r2 = agent.run_agent({"user_query": "열이 계속 나면 언제 병원 가야 해?"}, session_id=session_id)
    print(r2.get("answer_logs", [])[-1].content if r2.get("answer_logs") else r2)


if __name__ == "__main__":
    main()
