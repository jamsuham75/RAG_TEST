# ============================================================
# Retriever의 주요 검색 기능을 실습합니다.
# Similarity와 MMR을 비교하고, k값에 따른 점수를 확인합니다.
# 마지막으로 metadata를 이용하여 검색 범위를 제한합니다.
# ============================================================

import os
import sys
import warnings


# ------------------------------------------------------------
# 10차시의 indexer.py를 불러오기 위한 경로를 추가합니다.
# ------------------------------------------------------------
CURRENT_DIR = os.path.dirname(__file__)
INDEXER_DIR = os.path.join(CURRENT_DIR, "..", "10")

sys.path.insert(0, INDEXER_DIR)


# ------------------------------------------------------------
# 10차시에서 만든 Vector Store를 불러옵니다.
# ------------------------------------------------------------
from indexer import get_store


# 관련성 점수가 0~1 범위를 벗어날 때 발생하는 경고를 숨깁니다.
warnings.filterwarnings(
    "ignore",
    message="Relevance scores must be between 0 and 1"
)


# ------------------------------------------------------------
# 기본 설정
# ------------------------------------------------------------

# Vector Store를 불러옵니다.
store = get_store()

# 검색 방식 비교에 사용할 질문입니다.
QUESTION = "환불과 교환은 어떻게 다른가요?"

# 관련성이 낮다고 판단할 기준 점수입니다.
MIN_SCORE = 0.1


# ============================================================
# 검색 결과 출력 함수
# Retriever로 검색한 문서의 페이지와 내용을 출력합니다.
# ============================================================
def show_result(name, retriever):

    # 질문과 관련된 문서를 검색합니다.
    docs = retriever.invoke(QUESTION)

    # 검색 방식과 검색된 문서 개수를 출력합니다.
    print(f"■ {name} ({len(docs)}개)")

    # 검색된 문서를 하나씩 출력합니다.
    for doc in docs:

        # 문서 내용을 55자까지만 가져옵니다.
        preview = doc.page_content[:55]

        # 줄바꿈을 공백으로 변경합니다.
        preview = preview.replace("\n", " ")

        # 문서의 페이지 번호를 가져옵니다.
        page_no = doc.metadata["page_no"]

        # 페이지 번호와 내용을 출력합니다.
        print(f"   p.{page_no} {preview}...")

    print()


# ============================================================
# k값에 따른 점수 비교 함수
# k를 늘렸을 때 낮은 점수의 문서가 얼마나 추가되는지 봅니다.
# ============================================================
def compare_k(question, ks=(1, 3, 5)):

    print(f"질문: {question}")
    print("=" * 58)

    # 여러 k값을 차례대로 테스트합니다.
    for k in ks:

        # 문서와 관련성 점수를 함께 검색합니다.
        pairs = store.similarity_search_with_relevance_scores(
            question,
            k=k
        )

        # 점수를 저장할 리스트입니다.
        scores = []

        # 기준보다 낮은 문서 개수를 저장합니다.
        low_count = 0

        # 검색 결과의 점수를 하나씩 확인합니다.
        for doc, score in pairs:

            # 점수를 리스트에 저장합니다.
            scores.append(score)

            # 기준 점수보다 낮으면 개수를 증가시킵니다.
            if score < MIN_SCORE:
                low_count = low_count + 1

        # 화면 출력용 점수 리스트를 만듭니다.
        rounded_scores = []

        for score in scores:
            rounded_score = round(float(score), 3)
            rounded_scores.append(rounded_score)

        # k값과 검색 점수를 출력합니다.
        print(f"k={k:<3} 점수={rounded_scores}")

        # 기준 점수보다 낮은 문서 개수를 출력합니다.
        print(
            f"     기준 미달({MIN_SCORE}) 조각: "
            f"{low_count}개"
        )

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
# 후보 10개 중 다양성을 고려하여 최종 3개를 선택합니다.
# ============================================================

mmr_retriever = store.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 3,
        "fetch_k": 10
    }
)

show_result(
    "MMR k=3 fetch_k=10",
    mmr_retriever
)


# ============================================================
# 3. k값에 따른 유사도 점수 비교
# k를 늘렸을 때 낮은 점수 문서가 추가되는지 확인합니다.
# ============================================================

print("=" * 58)
print("k값에 따른 유사도 점수 비교")
print("=" * 58)
print()


# 단순한 사실 질문을 테스트합니다.
compare_k(
    "환불은 며칠 이내인가요?"
)


# 여러 내용을 함께 묻는 비교 질문을 테스트합니다.
compare_k(
    "환불과 교환은 어떻게 다른가요?"
)


# ============================================================
# 4. Metadata 필터링
# 특정 파일에 속한 문서만 대상으로 검색합니다.
# ============================================================

print("=" * 58)
print("메타데이터 필터링")
print("=" * 58)
print()


# manual.pdf 안에서만 검색하도록 Retriever를 만듭니다.
manual_retriever = store.as_retriever(
    search_type="similarity",
    search_kwargs={
        "k": 3,
        "filter": {
            "filename": "manual.pdf"
        }
    }
)


# 필터가 적용된 검색 결과를 확인합니다.
show_result(
    "filename 필터 - manual.pdf만",
    manual_retriever
)