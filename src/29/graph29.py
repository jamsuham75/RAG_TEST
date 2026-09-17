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


from langgraph.graph import StateGraph, START, END

from graph_state import RAGState
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

import config


MAX_RETRY = getattr(config, "MAX_RETRY", 2)


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


def route_after_retrieve(state: RAGState) -> str:
    """
    검색 성공 여부에 따라 분기합니다.
    """

    return "ok" if state.get("retrieval_ok") else "empty"


def route_after_verify(state: RAGState) -> str:
    """
    검증 결과에 따라 종료 또는 재생성으로 분기합니다.
    """

    grade = state.get("grade", "retry")

    # 검증 통과
    if grade == "pass":
        return "done"

    # Verifier가 명시적으로 포기
    if grade == "giveup":
        return "giveup"

    # 최대 재시도 횟수 초과
    if state.get("retries", 0) >= MAX_RETRY:
        return "giveup"

    # 그 외에는 재생성
    return "regenerate"


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
    # 기존 RAG 노드
    # ------------------------------------------------

    g.add_node("retrieve", retriever_node)
    g.add_node("generate", generator_node)
    g.add_node("verify", verifier_node)
    g.add_node("bump", bump_node)
    g.add_node("fallback", fallback_node)

    # ------------------------------------------------
    # 시작 → 분류
    # ------------------------------------------------

    g.add_edge(START, "classify")

    # ------------------------------------------------
    # 분류 결과에 따른 분기
    # ------------------------------------------------

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

    # ------------------------------------------------
    # 단축 경로 → 바로 종료
    # ------------------------------------------------

    g.add_edge("greeting", END)
    g.add_edge("calc", END)
    g.add_edge("scope", END)

    # ------------------------------------------------
    # 기존 RAG 흐름
    # ------------------------------------------------

    # 검색 결과에 따른 분기
    g.add_conditional_edges(
        "retrieve",
        route_after_retrieve,
        {
            "ok": "generate",
            "empty": "fallback",
        },
    )

    # 생성 → 검증
    g.add_edge("generate", "verify")

    # 검증 결과에 따른 분기
    g.add_conditional_edges(
        "verify",
        route_after_verify,
        {
            "done": END,
            "giveup": "fallback",
            "regenerate": "bump",
        },
    )

    # 재시도 횟수 증가 → 다시 생성
    g.add_edge("bump", "generate")

    # 검색 실패 또는 검증 포기
    g.add_edge("fallback", END)

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
        "retries": final.get("retries", 0),
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
            f"재시도={result['retries']}회 "
            f"검증통과={result['verified']}"
        )