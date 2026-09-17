# ===================================================
# 30차시 - Rewrite Node
# src/30/rewriter.py
# ===================================================

import os
import sys
import warnings


# ===================================================
# 경로 설정
# ===================================================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

warnings.filterwarnings("ignore")

# src/config.py 등을 사용하기 위한 경로
sys.path.insert(0, SRC_DIR)

# 이전 차시에서 만든 모듈 재사용
sys.path.insert(0, os.path.join(CURRENT_DIR, "..", "25"))
sys.path.insert(0, os.path.join(CURRENT_DIR, "..", "13"))
sys.path.insert(0, os.path.join(CURRENT_DIR, "..", "24"))
sys.path.insert(0, os.path.join(CURRENT_DIR, "..", "18"))


# ===================================================
# Import
# ===================================================

import config

from prompts import REWRITE_PROMPT
from generator import _llm
from langchain_core.output_parsers import StrOutputParser


# ===================================================
# Rewrite Chain
# ===================================================
# REWRITE_PROMPT
#       ↓
#      LLM
#       ↓
# 문자열 결과
# ===================================================

_rewrite = REWRITE_PROMPT | _llm | StrOutputParser()


# config.py에 MAX_REWRITE가 있으면 그 값을 사용하고,
# 없으면 기본값 2를 사용한다.
MAX_REWRITE = getattr(config, "MAX_REWRITE", 2)


# ===================================================
# Rewriter Node
# ===================================================
# 책임:
#   검색 실패 시 사용자 질문을
#   검색에 더 적합한 질의로 재작성한다.
#
# 주의:
#   - 직접 문서를 검색하지 않는다.
#   - 새로운 query만 만든다.
#   - 원본 question은 변경하지 않는다.
#
# [입력 - State에서 읽음]
#
#   question
#       원본 사용자 질문
#
#   tried_queries
#       지금까지 검색에 사용한 질의 목록
#
#   reason
#       Verifier에서 전달된 실패 이유
#
#   fail_reason
#       Retriever에서 전달된 검색 실패 이유
#
#   rewrites
#       지금까지 질의를 재작성한 횟수
#
#
# [출력 - State에 씀]
#
#   query
#       새롭게 작성된 검색 질의
#
#   rewrites
#       재작성 횟수
#
#   tried_queries
#       새롭게 시도할 질의
#       Reducer(operator.add)에 의해 기존 목록에 누적
#
#   retrieval_ok
#       새로운 검색을 하기 전 False로 초기화
#
#   log
#       실행 기록
# ===================================================

def rewrite_node(state) -> dict:

    # -------------------------------------------------
    # 1. State 값 읽기
    # -------------------------------------------------

    # 사용자가 처음 입력한 원본 질문
    question = state.get("question", "")

    # 지금까지 검색에 사용했던 질의
    tried = state.get("tried_queries", [])

    # 실패 이유
    # reason이 있으면 먼저 사용하고,
    # 없으면 fail_reason을 사용한다.
    reason = (
        state.get("reason")
        or state.get("fail_reason")
        or "관련 자료를 찾지 못함"
    )

    # 지금까지 Rewrite한 횟수
    n = state.get("rewrites", 0)


    # -------------------------------------------------
    # 2. Rewrite 상한 검사
    # -------------------------------------------------

    if n >= MAX_REWRITE:
        return {
            "rewrites": n,
            "log": [
                f"재작성 상한({MAX_REWRITE}) 도달"
            ],
        }


    # -------------------------------------------------
    # 3. LLM으로 새로운 검색 질의 생성
    # -------------------------------------------------

    try:

        new_query = _rewrite.invoke({

            # 원본 질문
            "question": question,

            # 이미 사용한 검색 질의
            # list를 문자열로 변환하여 Prompt에 전달
            "tried": (
                ", ".join(tried)
                if tried
                else "(없음)"
            ),

            # 이전 검색/검증 단계의 실패 이유
            "reason": reason,
        })

        # LLM이 다음과 같이 반환할 수도 있음
        #
        #   "환불 신청 기한"
        #   '환불 신청 기한'
        #
        # 불필요한 공백과 따옴표 제거
        new_query = (
            new_query
            .strip()
            .strip('"')
            .strip("'")
        )

    except Exception as e:

        # LLM 호출 오류가 발생하더라도
        # 그래프 전체를 중단시키지 않는다.
        return {
            "rewrites": n + 1,
            "log": [
                f"재작성 오류({type(e).__name__})"
            ],
        }


    # -------------------------------------------------
    # 4. 빈 결과 검사
    # -------------------------------------------------

    if not new_query:
        return {
            "rewrites": n + 1,
            "log": [
                "재작성 실패(빈값)"
            ],
        }


    # -------------------------------------------------
    # 5. 중복 질의 검사
    # -------------------------------------------------

    # 이미 검색했던 질의와 같으면
    # 다시 검색해도 같은 결과가 나올 가능성이 높다.
    if new_query in tried:
        return {
            "rewrites": n + 1,
            "log": [
                f"재작성 실패(중복): {new_query}"
            ],
        }


    # -------------------------------------------------
    # 6. 정상적으로 Rewrite 성공
    # -------------------------------------------------

    return {

        # Retriever가 다음 검색에서 사용할 질의
        "query": new_query,

        # Rewrite 횟수 증가
        "rewrites": n + 1,

        # 새 질의를 검색 이력에 추가
        #
        # State에서
        #
        # tried_queries:
        #     Annotated[List[str], operator.add]
        #
        # 로 선언했으므로 기존 목록에 자동 누적된다.
        "tried_queries": [new_query],

        # 새로운 query로 아직 검색하지 않았으므로
        # 검색 성공 여부를 False로 초기화
        "retrieval_ok": False,

        # 실행 과정 기록
        "log": [
            f"재작성 {n + 1}회: "
            f"'{question[:20]}...' "
            f"-> '{new_query}'"
        ],
    }