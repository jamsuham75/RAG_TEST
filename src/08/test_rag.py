# ============================================================
# 기본 RAG 시스템에 여러 질문을 넣어 테스트합니다.
# 답변과 검색된 문서를 출력하고 사람이 결과를 확인합니다.
# ============================================================

import os
import sys

sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "07")
)

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from prepare import prepare_chunks


# ------------------------------------------------------------
# 1. RAG 준비
# ------------------------------------------------------------

load_dotenv()

# PDF를 읽고 작은 조각으로 나눕니다.
chunks = prepare_chunks("../../data/manual.pdf")

# 문서를 벡터로 변환하여 FAISS에 저장합니다.
print("임베딩 중...")

emb = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

store = FAISS.from_documents(chunks, emb)

# 답변 생성용 LLM을 준비합니다.
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

print("✓ 준비 완료\n")


# ------------------------------------------------------------
# 2. 질문 → 검색 → 답변
# ------------------------------------------------------------

def ask(question):

    # 관련 문서 3개를 검색합니다.
    found = store.similarity_search(question, k=3)

    # 검색된 문서를 하나의 문자열로 합칩니다.
    context = ""

    for i, doc in enumerate(found, 1):
        context += f"[{i}] {doc.page_content}\n"

    # 검색된 자료를 근거로 답변하도록 지시합니다.
    prompt = (
        "아래 자료만 근거로 답하세요.\n"
        "자료에 없으면 '자료에서 확인할 수 없습니다'라고 하세요.\n\n"
        f"[자료]\n{context}\n"
        f"[질문] {question}"
    )

    # LLM에게 질문합니다.
    answer = llm.invoke(prompt).content

    return answer, found


# ------------------------------------------------------------
# 3. 테스트 질문
# ------------------------------------------------------------

TESTS = [
    "환불은 며칠 이내에 신청해야 하나요?",
    "우리 회사 대표이사 이름이 뭔가요?",
    "반품 절차를 알려주세요",
    "환불과 교환은 어떻게 다른가요?",
]


# ------------------------------------------------------------
# 4. 테스트 실행
# ------------------------------------------------------------

for i, question in enumerate(TESTS, 1):

    print("=" * 60)
    print(f"[질문 {i}] {question}")

    # RAG를 실행합니다.
    answer, found = ask(question)

    # 답변을 출력합니다.
    print(f"\n[답변]")
    print(answer)

    # 검색된 문서를 출력합니다.
    print("\n[검색 결과]")

    for j, doc in enumerate(found, 1):
        print(f"{j}. {doc.page_content[:100]}...")

    # 사람이 결과를 평가합니다.
    result = input("\n답변이 정확한가요? (Y/N): ")

    if result.upper() == "Y":
        print("✓ 정상")
    else:
        print("✗ 실패")

    print()