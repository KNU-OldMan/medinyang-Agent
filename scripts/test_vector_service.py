# scripts/test_vector_service.py
from app.deps import build_vector_service

def main():
    vector_service = build_vector_service()

    qas = vector_service.search("감기", n_results=3)

    print("search result type:", type(qas))
    print("search result:", qas)

if __name__ == "__main__":
    main()

