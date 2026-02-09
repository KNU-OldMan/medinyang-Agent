from app.agents.tools import search_medical_qa
from app.deps import build_vector_service

vs = build_vector_service()
vs.add_documents(
  ["감기에는 휴식과 수분 섭취가 중요합니다."],
  metadatas=[{"source":"test"}],
  ids=["test_cold_001"]
)

cfg = {"configurable": {"vector_service": vs}}

# ✅ tool.invoke 대신 tool.func로 직접 실행 (직렬화/검증을 안 타서 객체가 안 날아감)
print(search_medical_qa.func("감기", cfg))
