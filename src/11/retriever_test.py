# ============================================================
# Retriever 검색 방식 비교
# 같은 질문을 similarity와 MMR 방식으로 검색하여 결과를 비교합니다.
# similarity는 관련성을, MMR은 관련성과 다양성을 함께 고려합니다.
# ============================================================

import os
import sys


# ------------------------------------------------------------
# 10차시의 indexer.py를 사용할 수 있도록 경로를 추가합니다.
# ------------------------------------------------------------
CURRENT_DIR = os.path.dirname(__file__)
INDEXER_DIR = os.path.join(CURRENT_DIR, "..", "10")

sys.path.insert(0, INDEXER_DIR)


# ------------------------------------------------------------
# 10차시에서 만든 Vector Store 불러오기
# ------------------------------------------------------------
from indexer import get_store

store = get_store()


# ------------------------------------------------------------
# 두 검색 방식에 동일하게 사용할 질문입니다.
# ------------------------------------------------------------
QUESTION = "환불과 교환은 어떻게 다른가요?"


# ============================================================
# 검색 결과 출력 함수
# Retriever로 질문을 검색하고 결과를 간단하게 출력합니다.
# ============================================================
def show_result(name, retriever):

    # Retriever를 이용하여 관련 문서를 검색합니다.
    docs = retriever.invoke(QUESTION)

    # 검색 방식과 검색된 문서 개수를 출력합니다.
    print(f"■ {name} ({len(docs)}개)")

    # 검색된 문서를 하나씩 출력합니다.
    for doc in docs:

        # 문서 내용을 55자까지만 잘라서 보여줍니다.
        preview = doc.page_content[:55]

        # 줄바꿈을 공백으로 바꿔 한 줄로 출력합니다.
        preview = preview.replace("\n", " ")

        # 페이지 번호와 문서 내용을 출력합니다.
        page_no = doc.metadata["page_no"]

        print(f"   p.{page_no} {preview}...")

    print()


# ============================================================
# 1. Similarity 검색
# 질문과 가장 비슷한 문서 3개를 가져옵니다.
# ============================================================
similarity_retriever = store.as_retriever(
    search_type="similarity",
    search_kwargs={
        "k": 3
    }
)

show_result(
    "Similarity k=3",
    similarity_retriever
)


# ============================================================
# 2. MMR 검색
# 후보 10개 중 관련성과 다양성을 고려하여 3개를 선택합니다.
# ============================================================
mmr_retriever = store.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 3,
        "fetch_k": 10,
        "lambda_mult": 0.5
    }
)

show_result(
    "MMR k=3 fetch_k=10",
    mmr_retriever
)