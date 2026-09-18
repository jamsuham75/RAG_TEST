# ===================================================
# graph31.py
# 31차시 - 방어적 코딩 + 운영 로그
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

# 현재 31차시
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

# 31차시
from safe import safe_node
from logger import log_query

import config


# ===================================================
# 재시도 / 재작성 상한
# ===================================================

MAX_RETRY = getattr(config, "MAX_RETRY", 2)
MAX_REWRITE = getattr(config, "MAX_REWRITE", 2)


# ===================================================
# 31차시: 기존 노드에 안전장치 적용
# ===================================================

# Retriever에서 예외 발생
# → 그래프를 죽이지 않고 검색 실패 상태로 변환
safe_retriever_node = safe_node({
    "documents": [],
    "retrieval_ok": False,
    "fail_reason": "search_error",
})(retriever_node)


# Generator에서 예외 발생
# → 그래프를 죽이지 않고 생성 실패 상태로 변환
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
# 재시도 횟수 증가 노드
# ===================================================

def bump_node(state: RAGState) -> dict:

    n = state.get("retries", 0) + 1

    return {
        "retries": n,
        "log": [f"재시도 {n}회차 진입"],
    }


# ===================================================
# 분류 결과 상수
# ===================================================

GREETING = "greeting"
CALC = "calc"
SCOPE = "scope"
DOCUMENT = "document"


# ===================================================
# 분류 이후 라우팅
# ===================================================

def route_by_intent(state: RAGState) -> str:
    """
    분류 결과에 따라 다음 노드를 결정합니다.
    """

    intent = state.get("intent", DOCUMENT)

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
    """

    # 검색 성공
    if state.get("retrieval_ok"):
        return "ok"

    # -----------------------------------------------
    # 재작성 상한
    # -----------------------------------------------

    if state.get("rewrites", 0) >= MAX_REWRITE:
        return "giveup"

    # -----------------------------------------------
    # 검색 실패 원인
    # -----------------------------------------------

    fail_reason = state.get(
        "fail_reason",
        ""
    )

    # 검색은 정상 수행됐지만
    # 좋은 문서를 못 찾음
    # → 질문을 바꿔서 다시 검색
    if fail_reason in (
        "low_score",
        "",
    ):
        return "research"

    # search_error 등
    # 시스템 오류는 재작성해도 해결되지 않음
    return "giveup"


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
    """

    grade = state.get(
        "grade",
        "retry"
    )

    # -----------------------------------------------
    # 검증 성공
    # -----------------------------------------------

    if grade == "pass":
        return "done"

    # -----------------------------------------------
    # 명시적 포기
    # -----------------------------------------------

    if grade == "giveup":
        return "giveup"

    # -----------------------------------------------
    # 근거 부족
    # -----------------------------------------------

    if grade == "research":

        if (
            state.get("rewrites", 0)
            >= MAX_REWRITE
        ):
            return "giveup"

        return "research"

    # -----------------------------------------------
    # 같은 근거로 다시 생성
    # -----------------------------------------------

    if (
        state.get("retries", 0)
        >= MAX_RETRY
    ):
        return "giveup"

    return "regenerate"


# ===================================================
# Rewrite 이후 라우팅
# ===================================================

def route_after_rewrite(state: RAGState) -> str:
    """
    정상적인 새로운 질의
        → retrieve

    재작성 실패
        → fallback
    """

    query = state.get(
        "query",
        ""
    )

    tried = state.get(
        "tried_queries",
        []
    )

    # query가 없으면 실패
    if not query:
        return "giveup"

    # rewrite_node가 성공하면
    # 새로운 query가 tried_queries에 들어 있음
    if query in tried:
        return "retry_search"

    return "giveup"


# ===================================================
# 그래프 조립
# ===================================================

def build_graph():

    g = StateGraph(RAGState)


    # =================================================
    # 분류 노드
    # =================================================

    g.add_node(
        "classify",
        classifier_node
    )

    g.add_node(
        "greeting",
        greeting_node
    )

    g.add_node(
        "calc",
        calc_node
    )

    g.add_node(
        "scope",
        scope_node
    )


    # =================================================
    # RAG 노드
    #
    # ★ 31차시 핵심
    # 기존 노드가 아니라 safe_node로 감싼 노드를 등록
    # =================================================

    g.add_node(
        "retrieve",
        safe_retriever_node
    )

    g.add_node(
        "generate",
        safe_generator_node
    )

    g.add_node(
        "verify",
        safe_verifier_node
    )


    # =================================================
    # 기타 노드
    # =================================================

    g.add_node(
        "bump",
        bump_node
    )

    g.add_node(
        "fallback",
        fallback_node
    )

    g.add_node(
        "rewrite",
        rewrite_node
    )


    # =================================================
    # START → classify
    # =================================================

    g.add_edge(
        START,
        "classify"
    )


    # =================================================
    # classify → 의도별 분기
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
    # 단축 경로
    # =================================================

    g.add_edge(
        "greeting",
        END
    )

    g.add_edge(
        "calc",
        END
    )

    g.add_edge(
        "scope",
        END
    )


    # =================================================
    # retrieve 이후
    #
    #                 ┌─ ok ───────→ generate
    #                 │
    # retrieve ───────┼─ research ─→ rewrite
    #                 │
    #                 └─ giveup ───→ fallback
    # =================================================

    g.add_conditional_edges(
        "retrieve",

        route_after_retrieve,

        {
            "ok": "generate",
            "research": "rewrite",
            "giveup": "fallback",
        },
    )


    # =================================================
    # generate → verify
    # =================================================

    g.add_edge(
        "generate",
        "verify"
    )


    # =================================================
    # verify 이후
    #
    #               ┌─ done ────────→ END
    #               │
    # verify ───────┼─ regenerate ──→ bump
    #               │
    #               ├─ research ────→ rewrite
    #               │
    #               └─ giveup ──────→ fallback
    # =================================================

    g.add_conditional_edges(
        "verify",

        route_after_verify,

        {
            "done": END,
            "regenerate": "bump",
            "research": "rewrite",
            "giveup": "fallback",
        },
    )


    # =================================================
    # 재생성 루프
    # =================================================

    g.add_edge(
        "bump",
        "generate"
    )


    # =================================================
    # 재검색 루프
    # =================================================

    g.add_conditional_edges(
        "rewrite",

        route_after_rewrite,

        {
            "retry_search": "retrieve",
            "giveup": "fallback",
        },
    )


    # =================================================
    # fallback → END
    # =================================================

    g.add_edge(
        "fallback",
        END
    )


    # =================================================
    # 컴파일
    # =================================================

    return g.compile()


# ===================================================
# 31차시 실행 객체
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
    # 그래프 실행
    # -----------------------------------------------

    final = app.invoke(
        make_initial_state(question),
        {
            "recursion_limit": 25
        },
    )


    # -----------------------------------------------
    # 실행 시간 계산
    # -----------------------------------------------

    elapsed = (
        time.time() - t0
    )


    # -----------------------------------------------
    # 31차시 운영 로그
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

        print(f"\nQ: {question}")

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
            final.get("answer", ""),

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
            final.get("intent", ""),

        "grade":
            final.get("grade", ""),

        "reason":
            final.get("reason", ""),

        "retries":
            final.get("retries", 0),

        "rewrites":
            final.get("rewrites", 0),

        "tried_queries":
            final.get(
                "tried_queries",
                []
            ),

        # -------------------------------------------
        # 검증 여부
        #
        # verifier가 정상적으로 pass한 경우에만 True
        # verifier 자체에 오류가 발생했다면 False
        # -------------------------------------------

        "verified": (
            final.get("grade") == "pass"
            and not final.get("node_error")
        ),

        # 31차시 장애 확인용
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

        "log":
            final.get(
                "log",
                []
            ),

        "ok": True,
    }


# ===================================================
# 직접 실행 테스트
# ===================================================

if __name__ == "__main__":

    print(
        app.get_graph().draw_ascii()
    )


    test_questions = [

        "안녕하세요",

        "10 + 20",

        "오늘 날씨 어때요?",

        "환불은 며칠 이내에 신청해야 하나요?",

        "대표이사가 누구인가요?",
    ]


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
            f"   판정={result['grade']} "
            f"재생성={result['retries']}회 "
            f"재작성={result['rewrites']}회 "
            f"검증통과={result['verified']}"
        )

        if result["node_error"]:

            print(
                f"   노드오류="
                f"{result['node_error']}"
            )


        if result["tried_queries"]:

            print(
                f"   검색 질의="
                f"{' → '.join(result['tried_queries'])}"
            )