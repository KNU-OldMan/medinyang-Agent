# scripts/test_answer_gen.py
from langchain_core.messages import AIMessage
from app.service.agents.answer_gen_service import AnswerGenService

def main():
    svc = AnswerGenService()

    # 1) 정상(success) 케이스 흉내
    extract_logs_success = [
        AIMessage(content="""{
          "status": "success",
          "medical_context": "감기에는 휴식과 수분 섭취가 중요하며, 고열/호흡곤란/흉통 등은 진료가 필요할 수 있습니다.",
          "key_points": ["휴식", "수분 섭취", "고열/호흡곤란 시 의료기관 상담"]
        }""")
    ]

    res1 = svc.run(
        user_query="감기 걸렸을 때 어떻게 해야 해?",
        extract_logs=extract_logs_success,
        history=[]
    )
    print("\n=== ANSWER (success) ===")
    for m in res1["answer_logs"]:
        print(m.content)

    # 2) 도메인 아님(out_of_domain) 케이스
    extract_logs_ood = [
        AIMessage(content='{"status":"out_of_domain","medical_context":"","key_points":[]}')
    ]
    res2 = svc.run(
        user_query="파이썬으로 퀵소트 구현해줘",
        extract_logs=extract_logs_ood,
        history=[]
    )
    print("\n=== ANSWER (out_of_domain) ===")
    for m in res2["answer_logs"]:
        print(m.content)

if __name__ == "__main__":
    main()
