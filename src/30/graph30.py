import os
import sys


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

# 30차시에서 추가
from rewriter import rewrite_node

import config


# ===================================================
# 재시도 / 재작성 상한
# ===================================================

MAX_RETRY = getattr(config, "MAX_RETRY", 2)
MAX_REWRITE = getattr(config, "MAX_REWRITE", 2)


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
# 라우팅 함수
# ===================================================

def route_by_intent(state: RAGState) -> str:
    """
    분류 결과에 따라 다음 노드를 결정합니다.
    """

    intent = state.get("intent", DOCUMENT)

    if intent in (GREETING, CALC, SCOPE):
        return intent

    # 알 수 없는 값이나 document는 RAG 검색으로 전달
    return DOCUMENT


# ===================================================
# Retriever 이후 라우팅
# ===================================================

def route_after_retrieve(state: RAGState) -> str:
    """
    검색 성공 여부와 실패 이유에 따라 분기합니다.

    성공
        → generate

    검색 품질 부족
        → rewrite

    재작성 상한 도달 또는 복구 불가능한 검색 오류
        → fallback
    """

    # 검색 성공
    if state.get("retrieval_ok"):
        return "ok"

    # -----------------------------------------------
    # 재작성 횟수 상한 확인
    # -----------------------------------------------

    if state.get("rewrites", 0) >= MAX_REWRITE:
        return "giveup"

    # -----------------------------------------------
    # 검색은 수행됐지만 적절한 근거를 확보하지 못한 경우
    # → 질의를 바꿔 다시 검색
    # -----------------------------------------------

    fail_reason = state.get("fail_reason", "")

    if fail_reason in ("low_score", ""):
        return "research"

    # -----------------------------------------------
    # search_error, no_result 등
    # 재작성으로 해결하기 어렵다고 판단
    # -----------------------------------------------

    return "giveup"


# ===================================================
# Verifier 이후 라우팅
# ===================================================

def route_after_verify(state: RAGState) -> str:
    """
    검증 결과에 따라 다음 행동을 결정합니다.

    pass
        → 종료

    retry
        → 같은 근거로 다시 생성

    research
        → 질의를 재작성하고 다시 검색

    giveup
        → fallback
    """

    grade = state.get("grade", "retry")

    # -----------------------------------------------
    # 검증 성공
    # -----------------------------------------------

    if grade == "pass":
        return "done"

    # -----------------------------------------------
    # Verifier가 명시적으로 포기
    # -----------------------------------------------

    if grade == "giveup":
        return "giveup"

    # -----------------------------------------------
    # 근거 자체가 부족한 경우
    # → 재생성이 아니라 재검색
    # -----------------------------------------------

    if grade == "research":

        # 재작성 상한 확인
        if state.get("rewrites", 0) >= MAX_REWRITE:
            return "giveup"

        return "research"

    # -----------------------------------------------
    # 같은 근거로 답변을 다시 생성할 수 있는 경우
    # -----------------------------------------------

    if state.get("retries", 0) >= MAX_RETRY:
        return "giveup"

    return "regenerate"


# ===================================================
# Rewrite 이후 라우팅
# ===================================================

def route_after_rewrite(state: RAGState) -> str:
    """
    Rewrite 결과를 확인합니다.

    정상적으로 새로운 질의가 만들어졌으면
        → retrieve

    재작성에 실패했으면
        → fallback
    """

    query = state.get("query", "")
    tried = state.get("tried_queries", [])

    # query가 없으면 재작성 실패
    if not query:
        return "giveup"

    # 정상적인 경우 다시 검색
    #
    # rewrite_node가 성공하면 새로운 query를 만들고
    # tried_queries에도 추가한다.
    if query in tried:
        return "retry_search"

    return "giveup"


# ===================================================
# 그래프 조립
# ===================================================

def build_graph():

    g = StateGraph(RAGState)

    # ------------------------------------------------
    # 분류 노드
    # ------------------------------------------------

    g.add_node("classify", classifier_node)
    g.add_node("greeting", greeting_node)
    g.add_node("calc", calc_node)
    g.add_node("scope", scope_node)

    # ------------------------------------------------
    # RAG 노드
    # ------------------------------------------------

    g.add_node("retrieve", retriever_node)
    g.add_node("generate", generator_node)
    g.add_node("verify", verifier_node)
    g.add_node("bump", bump_node)
    g.add_node("fallback", fallback_node)

    # ------------------------------------------------
    # 30차시 추가
    # ------------------------------------------------

    g.add_node("rewrite", rewrite_node)


    # =================================================
    # START → classify
    # =================================================

    g.add_edge(START, "classify")


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
    # 단축 경로 → END
    # =================================================

    g.add_edge("greeting", END)
    g.add_edge("calc", END)
    g.add_edge("scope", END)


    # =================================================
    # retrieve 이후 분기
    # =================================================
    #
    #                ┌─ 성공 ─────────→ generate
    #                │
    # retrieve ──────┼─ 검색 품질 부족 → rewrite
    #                │
    #                └─ 복구 불가 ─────→ fallback
    #

    g.add_conditional_edges(
        "retrieve",
        route_after_retrieve,
        {
            "ok": "generate",

            # ★ 30차시
            "research": "rewrite",

            "giveup": "fallback",
        },
    )


    # =================================================
    # generate → verify
    # =================================================

    g.add_edge("generate", "verify")


    # =================================================
    # verify 이후 분기
    # =================================================
    #
    #                ┌─ pass ───────→ END
    #                │
    # verify ────────┼─ retry ──────→ bump
    #                │
    #                ├─ research ───→ rewrite
    #                │
    #                └─ giveup ─────→ fallback
    #

    g.add_conditional_edges(
        "verify",
        route_after_verify,
        {
            "done": END,

            # 같은 근거로 답변 다시 생성
            "regenerate": "bump",

            # ★ 30차시
            # 근거가 부족하면 질의부터 다시 작성
            "research": "rewrite",

            "giveup": "fallback",
        },
    )


    # =================================================
    # 재생성 루프
    # =================================================
    #
    # bump → generate → verify
    #

    g.add_edge("bump", "generate")


    # =================================================
    # ★ 30차시: 재검색 루프
    # =================================================
    #
    # rewrite → retrieve
    #
    # query를 변경한 뒤 새로운 검색 수행
    #

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

    g.add_edge("fallback", END)


    # =================================================
    # 그래프 컴파일
    # =================================================

    return g.compile()


# ===================================================
# 그래프 실행 객체
# ===================================================

app = build_graph()


# ===================================================
# 외부 호출 함수
# ===================================================

def ask(question: str, verbose: bool = False) -> dict:

    final = app.invoke(
        make_initial_state(question),
        {
            "recursion_limit": 25
        },
    )

    if verbose:

        print(f"\nQ: {question}")

        for line in final.get("log", []):
            print(f"   · {line}")

    return {

        "answer": final.get("answer", ""),

        "sources": [
            {
                "file": d.metadata.get("filename"),
                "page": d.metadata.get("page_no"),
            }
            for d in final.get("documents", [])
        ],

        "intent": final.get("intent", ""),

        "grade": final.get("grade", ""),

        "reason": final.get("reason", ""),

        # 재생성 횟수
        "retries": final.get("retries", 0),

        # ★ 30차시: 재검색을 위한 질의 재작성 횟수
        "rewrites": final.get("rewrites", 0),

        # ★ 어떤 검색어들이 사용되었는지 확인
        "tried_queries": final.get("tried_queries", []),

        "verified": final.get("grade") == "pass",

        "log": final.get("log", []),

        "ok": True,
    }


# ===================================================
# 직접 실행 테스트
# ===================================================

if __name__ == "__main__":

    print(app.get_graph().draw_ascii())

    test_questions = [
        "안녕하세요",
        "10 + 20",
        "오늘 날씨 어때요?",
        "환불은 며칠 이내에 신청해야 하나요?",
        "대표이사가 누구인가요?",
    ]

    for q in test_questions:

        result = ask(q, verbose=True)

        print(f"   A: {result['answer'][:70]}")

        print(f"   의도={result['intent']}")

        print(
            f"   판정={result['grade']} "
            f"재생성={result['retries']}회 "
            f"재작성={result['rewrites']}회 "
            f"검증통과={result['verified']}"
        )

        # Rewrite가 발생했는지 확인하기 좋음
        if result["tried_queries"]:
            print(
                f"   검색 질의="
                f"{' → '.join(result['tried_queries'])}"
            )

