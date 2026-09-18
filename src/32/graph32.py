# ===================================================
# graph32.py
# 32차시 - Modular RAG 종합
# ===================================================

import os
import sys
import warnings
import time

warnings.filterwarnings("ignore")


# ===================================================
# 모듈 경로 설정
# ===================================================

BASE_DIR = os.path.dirname(__file__)

sys.path.insert(0, os.path.join(BASE_DIR, "..", "18"))
sys.path.insert(0, os.path.join(BASE_DIR, "..", "19"))
sys.path.insert(0, os.path.join(BASE_DIR, "..", "24"))
sys.path.insert(0, os.path.join(BASE_DIR, "..", "25"))
sys.path.insert(0, os.path.join(BASE_DIR, "..", "26"))
sys.path.insert(0, os.path.join(BASE_DIR, "..", "29"))
sys.path.insert(0, os.path.join(BASE_DIR, "..", "30"))
sys.path.insert(0, os.path.join(BASE_DIR, "..", "31"))

# 현재 32차시
sys.path.insert(0, BASE_DIR)


# ===================================================
# Import
# ===================================================

from langgraph.graph import StateGraph, START, END

from graph_state2 import RAGState
from graph_state2 import make_initial_state

from retriever import retriever_node
from generator import generator_node
from verifier import verifier_node
from fallback import fallback_node

from classifier import classifier_node

from intents import (
    greeting_node,
    calc_node,
    scope_node,
)

from rewriter import rewrite_node

# 31차시에서 만든 방어적 코딩 / 운영 로그
from safe import safe_node
from logger import log_query

import config


# ===================================================
# 실행 제한 설정
# ===================================================

MAX_RETRY = getattr(
    config,
    "MAX_RETRY",
    2
)

MAX_REWRITE = getattr(
    config,
    "MAX_REWRITE",
    2
)

# 32차시 추가
# 전체 그래프 실행 제한 시간
MAX_TOTAL_SEC = getattr(
    config,
    "MAX_TOTAL_SEC",
    60
)


# ===================================================
# 경로 상수
# ===================================================
# 문자열을 여러 곳에서 직접 사용하지 않고
# 상수로 관리하여 오타를 방지합니다.
# ===================================================

OK = "ok"
RESEARCH = "research"
REGEN = "regenerate"
DONE = "done"
GIVEUP = "giveup"

GREETING = "greeting"
CALC = "calc"
SCOPE = "scope"
DOCUMENT = "document"


# ===================================================
# 31차시: 기존 노드에 안전장치 적용
# ===================================================

# Retriever에서 예외 발생
# → 검색 실패 상태로 변환
safe_retriever_node = safe_node({
    "documents": [],
    "retrieval_ok": False,
    "fail_reason": "search_error",
})(retriever_node)


# Generator에서 예외 발생
# → 생성 실패 상태로 변환
safe_generator_node = safe_node({
    "answer": "",
    "insufficient": True,
    "gen_error": "unknown",
})(generator_node)


# Verifier에서 예외 발생
# → 검증기 장애 때문에 전체 서비스를 막지 않음
safe_verifier_node = safe_node({
    "grade": "pass",
    "reason": "검증 불가 - 통과 처리",
    "verified": False,
})(verifier_node)


# ===================================================
# 재생성 횟수 증가 노드
# ===================================================

def bump_node(state: RAGState) -> dict:

    n = state.get("retries", 0) + 1

    return {
        "retries": n,
        "log": [f"재생성 {n}회차 진입"],
    }


# ===================================================
# 전체 실행 시간 확인
# ===================================================

def _out_of_time(state: RAGState) -> bool:
    """
    그래프의 전체 실행 제한 시간을 초과했는지 확인합니다.

    deadline이 없는 경우에는 무한대로 간주하여
    기존 코드와도 호환되도록 합니다.
    """

    return time.time() > state.get(
        "deadline",
        float("inf")
    )


# ===================================================
# 분류 이후 라우팅
# ===================================================

def route_by_intent(state: RAGState) -> str:
    """
    질문 유형에 따라 다음 노드를 결정합니다.

    greeting → greeting
    calc     → calc
    scope    → scope
    document → retrieve
    """

    intent = state.get(
        "intent",
        DOCUMENT
    )

    if intent in (
        GREETING,
        CALC,
        SCOPE,
    ):
        return intent

    return DOCUMENT


# ===================================================
# Retriever 이후 라우팅
# ===================================================

def route_after_retrieve(state: RAGState) -> str:
    """
    검색 성공
        → generate

    검색 품질 부족
        → rewrite

    검색 시스템 오류
        → fallback

    재작성 상한 도달
        → fallback

    전체 시간 초과
        → fallback
    """

    # -----------------------------------------------
    # 전체 시간 제한
    # -----------------------------------------------

    if _out_of_time(state):
        return GIVEUP


    # -----------------------------------------------
    # 검색 성공
    # -----------------------------------------------

    if state.get("retrieval_ok"):
        return OK


    # -----------------------------------------------
    # 재작성 상한
    # -----------------------------------------------

    if state.get("rewrites", 0) >= MAX_REWRITE:
        return GIVEUP


    # -----------------------------------------------
    # 검색 실패 원인
    # -----------------------------------------------

    fail_reason = state.get(
        "fail_reason",
        ""
    )


    # 검색 자체는 성공했지만
    # 좋은 문서를 찾지 못한 경우
    #
    # → 질문을 재작성하여 다시 검색
    if fail_reason in (
        "low_score",
        "",
    ):
        return RESEARCH


    # search_error
    # no_result
    # empty_query
    #
    # 재작성해도 해결될 가능성이 낮으므로 포기
    return GIVEUP


# ===================================================
# Verifier 이후 라우팅
# ===================================================

def route_after_verify(state: RAGState) -> str:
    """
    pass
        → END

    retry
        → 같은 근거로 다시 생성

    research
        → rewrite → retrieve

    giveup
        → fallback

    전체 시간 초과
        → fallback
    """

    # -----------------------------------------------
    # 전체 시간 제한
    # -----------------------------------------------

    if _out_of_time(state):
        return GIVEUP


    # -----------------------------------------------
    # 검증 결과
    # -----------------------------------------------

    grade = state.get(
        "grade",
        "retry"
    )


    # -----------------------------------------------
    # 검증 성공
    # -----------------------------------------------
    # MAX_RETRY보다 먼저 검사합니다.
    #
    # 마지막 재생성에서 pass가 나왔다면
    # 정상적으로 종료되어야 하기 때문입니다.
    # -----------------------------------------------

    if grade == "pass":
        return DONE


    # -----------------------------------------------
    # 명시적 포기
    # -----------------------------------------------

    if grade == "giveup":
        return GIVEUP


    # -----------------------------------------------
    # 근거 부족
    # → 질문 재작성 후 재검색
    # -----------------------------------------------

    if grade == "research":

        if state.get("rewrites", 0) >= MAX_REWRITE:
            return GIVEUP

        return RESEARCH


    # -----------------------------------------------
    # 같은 근거로 다시 생성
    #
    # retry인 경우에만
    # MAX_RETRY를 검사합니다.
    # -----------------------------------------------

    if state.get("retries", 0) >= MAX_RETRY:
        return GIVEUP

    return REGEN


# ===================================================
# Rewrite 이후 라우팅
# ===================================================

def route_after_rewrite(state: RAGState) -> str:
    """
    정상적인 새로운 검색 질의
        → retrieve

    재작성 실패
        → fallback

    전체 시간 초과
        → fallback
    """

    # -----------------------------------------------
    # 전체 시간 제한
    # -----------------------------------------------

    if _out_of_time(state):
        return GIVEUP


    # -----------------------------------------------
    # 재작성된 검색 질의 확인
    # -----------------------------------------------

    query = state.get(
        "query",
        ""
    )

    if query:
        return "retry_search"

    return GIVEUP


# ===================================================
# 그래프 조립
# ===================================================

def build_graph():

    g = StateGraph(RAGState)


    # =================================================
    # ① 노드 등록
    # =================================================
    #
    # 31차시에서는 add_node()를 하나씩 작성했지만
    # 32차시에서는 딕셔너리로 한 번에 관리합니다.
    #
    # Retriever / Generator / Verifier는
    # 31차시에서 만든 safe_node를 적용합니다.
    # =================================================

    NODES = {

        "classify":
            classifier_node,

        "greeting":
            greeting_node,

        "calc":
            calc_node,

        "scope":
            scope_node,

        "retrieve":
            safe_retriever_node,

        "generate":
            safe_generator_node,

        "verify":
            safe_verifier_node,

        "bump":
            bump_node,

        "rewrite":
            rewrite_node,

        "fallback":
            fallback_node,
    }


    # -----------------------------------------------
    # 노드 일괄 등록
    # -----------------------------------------------

    for name, fn in NODES.items():

        g.add_node(
            name,
            fn
        )


    # =================================================
    # ② START → classify
    # =================================================

    g.add_edge(
        START,
        "classify"
    )


    # =================================================
    # ③ classify → 질문 유형별 분기
    # =================================================
    #
    # greeting → greeting
    # calc     → calc
    # scope    → scope
    # document → retrieve
    # =================================================

    g.add_conditional_edges(

        "classify",

        route_by_intent,

        {
            GREETING: "greeting",
            CALC: "calc",
            SCOPE: "scope",
            DOCUMENT: "retrieve",
        },
    )


    # =================================================
    # ④ 단축 경로
    # =================================================
    #
    # 인사 / 계산 / 범위 밖 질문은
    # RAG를 실행하지 않고 바로 종료합니다.
    # =================================================

    for node_name in (
        "greeting",
        "calc",
        "scope",
    ):

        g.add_edge(
            node_name,
            END
        )


    # =================================================
    # ⑤ retrieve 이후 분기
    # =================================================
    #
    #                  ┌─ OK ────────→ generate
    #                  │
    # retrieve ────────┼─ RESEARCH ──→ rewrite
    #                  │
    #                  └─ GIVEUP ─────→ fallback
    #
    # =================================================

    g.add_conditional_edges(

        "retrieve",

        route_after_retrieve,

        {
            OK: "generate",
            RESEARCH: "rewrite",
            GIVEUP: "fallback",
        },
    )


    # =================================================
    # ⑥ generate → verify
    # =================================================

    g.add_edge(
        "generate",
        "verify"
    )


    # =================================================
    # ⑦ verify 이후 분기
    # =================================================
    #
    #                ┌─ DONE ────────→ END
    #                │
    # verify ────────┼─ REGEN ───────→ bump
    #                │
    #                ├─ RESEARCH ─────→ rewrite
    #                │
    #                └─ GIVEUP ───────→ fallback
    #
    # =================================================

    g.add_conditional_edges(

        "verify",

        route_after_verify,

        {
            DONE: END,
            REGEN: "bump",
            RESEARCH: "rewrite",
            GIVEUP: "fallback",
        },
    )


    # =================================================
    # ⑧ 재생성 루프
    # =================================================
    #
    # bump
    #   ↓
    # generate
    #   ↓
    # verify
    #
    # 같은 검색 근거를 사용하여 답변만 다시 생성합니다.
    # =================================================

    g.add_edge(
        "bump",
        "generate"
    )


    # =================================================
    # ⑨ 재검색 루프
    # =================================================
    #
    # rewrite
    #   ↓
    # retrieve
    #
    # 질문을 다시 작성한 뒤
    # 새로운 검색을 수행합니다.
    # =================================================

    g.add_conditional_edges(

        "rewrite",

        route_after_rewrite,

        {
            "retry_search": "retrieve",
            GIVEUP: "fallback",
        },
    )


    # =================================================
    # ⑩ fallback → END
    # =================================================

    g.add_edge(
        "fallback",
        END
    )


    # =================================================
    # 그래프 컴파일
    # =================================================

    return g.compile()


# ===================================================
# 실행 객체
# ===================================================

app = build_graph()


# ===================================================
# 외부 호출 함수
# ===================================================

def ask(
    question: str,
    verbose: bool = False
) -> dict:

    # -----------------------------------------------
    # 시작 시간
    # -----------------------------------------------

    t0 = time.time()


    # -----------------------------------------------
    # 초기 State 생성
    #
    # 교재의 init_state() 대신
    # 현재 프로젝트의 make_initial_state() 사용
    # -----------------------------------------------

    state = make_initial_state(
        question
    )


    # -----------------------------------------------
    # 전체 실행 제한 시간 설정
    # -----------------------------------------------

    state["deadline"] = (
        t0 + MAX_TOTAL_SEC
    )


    # -----------------------------------------------
    # 그래프 실행
    # -----------------------------------------------

    final = app.invoke(

        state,

        {
            "recursion_limit": 40
        },
    )


    # -----------------------------------------------
    # 실행 시간 계산
    # -----------------------------------------------

    elapsed = (
        time.time() - t0
    )


    # -----------------------------------------------
    # 31차시 운영 로그 유지
    # -----------------------------------------------

    log_query(
        question,
        final,
        elapsed
    )


    # -----------------------------------------------
    # 실행 과정 출력
    # -----------------------------------------------

    if verbose:

        print(
            f"\nQ: {question}"
        )

        for line in final.get(
            "log",
            []
        ):

            print(
                f"   · {line}"
            )


    # -----------------------------------------------
    # 외부 반환값
    # -----------------------------------------------

    return {

        "answer":
            final.get(
                "answer",
                ""
            ),

        "sources": [
            {
                "file":
                    d.metadata.get(
                        "filename"
                    ),

                "page":
                    d.metadata.get(
                        "page_no"
                    ),
            }

            for d in final.get(
                "documents",
                []
            )
        ],

        "intent":
            final.get(
                "intent",
                ""
            ),

        "grade":
            final.get(
                "grade",
                ""
            ),

        "reason":
            final.get(
                "reason",
                ""
            ),

        "retries":
            final.get(
                "retries",
                0
            ),

        "rewrites":
            final.get(
                "rewrites",
                0
            ),

        "tried_queries":
            final.get(
                "tried_queries",
                []
            ),

        # -------------------------------------------
        # 검증 여부
        #
        # verifier가 정상적으로 pass한 경우에만 True
        # verifier 자체 오류 발생 시 False
        # -------------------------------------------

        "verified": (
            final.get("grade") == "pass"
            and not final.get("node_error")
        ),

        # -------------------------------------------
        # 실행 시간
        # -------------------------------------------

        "elapsed":
            round(
                elapsed,
                2
            ),

        # -------------------------------------------
        # 장애 / fallback 정보
        # -------------------------------------------

        "node_error":
            final.get(
                "node_error",
                ""
            ),

        "fail_reason":
            final.get(
                "fail_reason",
                ""
            ),

        "fallback_kind":
            final.get(
                "fallback_kind",
                ""
            ),

        # -------------------------------------------
        # 실행 로그
        # -------------------------------------------

        "log":
            final.get(
                "log",
                []
            ),

        # -------------------------------------------
        # 전체 State
        #
        # 32차시 실습/디버깅용
        # -------------------------------------------

        "_state":
            final,

        "ok":
            True,
    }


# ===================================================
# 직접 실행 테스트
# ===================================================

if __name__ == "__main__":

    # -----------------------------------------------
    # 그래프 구조 출력
    # -----------------------------------------------

    print(
        app.get_graph().draw_ascii()
    )


    # -----------------------------------------------
    # 테스트 질문
    # -----------------------------------------------

    test_questions = [

        # greeting
        "안녕하세요",

        # calc
        "10 + 20",

        # scope
        "오늘 날씨 어때요?",

        # document - 정상 검색 예상
        "환불은 며칠 이내에 신청해야 하나요?",

        # document - 재검색/fallback 가능
        "대표이사가 누구인가요?",
    ]


    # -----------------------------------------------
    # 테스트 실행
    # -----------------------------------------------

    for q in test_questions:

        result = ask(
            q,
            verbose=True
        )


        print(
            f"   A: "
            f"{result['answer'][:70]}"
        )


        print(
            f"   의도="
            f"{result['intent']}"
        )


        print(
            f"   판정="
            f"{result['grade']} "
            f"재생성="
            f"{result['retries']}회 "
            f"재작성="
            f"{result['rewrites']}회 "
            f"검증통과="
            f"{result['verified']}"
        )


        print(
            f"   실행시간="
            f"{result['elapsed']}초"
        )


        # -------------------------------------------
        # 노드 오류가 있는 경우
        # -------------------------------------------

        if result["node_error"]:

            print(
                f"   노드오류="
                f"{result['node_error']}"
            )


        # -------------------------------------------
        # 검색 질의 이력
        # -------------------------------------------

        if result["tried_queries"]:

            print(
                f"   검색 질의="
                f"{' → '.join(result['tried_queries'])}"
            )