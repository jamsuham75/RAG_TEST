# ===================================================
# 30차시 - Query Rewrite + 재검색
# src/30/graph30.py
# ===================================================

import os
import sys
import warnings


# ===================================================
# 경로 설정
# ===================================================

# 현재 폴더
# C:\REG_TEST\src\30
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 상위 src 폴더
# C:\REG_TEST\src
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

warnings.filterwarnings("ignore")

# src/config.py 사용
sys.path.insert(0, SRC_DIR)

# 이전 차시 모듈 사용
for folder in ["18", "19", "24", "25", "26", "29"]:
    sys.path.insert(
        0,
        os.path.join(SRC_DIR, folder)
    )


# ===================================================
# Import
# ===================================================

import config

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

# 같은 30 폴더에 있음
from rewriter import rewrite_node


# ===================================================
# 설정
# ===================================================

MAX_RETRY = getattr(config, "MAX_RETRY", 2)
MAX_REWRITE = getattr(config, "MAX_REWRITE", 2)


# ===================================================
# 재생성 횟수 증가
# ===================================================

def bump_node(state):

    n = state.get("retries", 0) + 1

    return {
        "retries": n,
        "log": [f"재생성 {n}회"]
    }


# ===================================================
# 1. 질문 유형 분기
# ===================================================

def route_intent(state):

    intent = state.get("intent", "document")

    if intent == "greeting":
        return "greeting"

    if intent == "calc":
        return "calc"

    if intent == "scope":
        return "scope"

    return "document"


# ===================================================
# 2. 검색 후 분기
# ===================================================

def route_retrieve(state):

    # 검색 성공
    if state.get("retrieval_ok"):
        return "generate"

    # 재작성 횟수 초과
    if state.get("rewrites", 0) >= MAX_REWRITE:
        return "fallback"

    # 검색 결과는 있지만 점수가 낮음
    if state.get("fail_reason") in ("low_score", ""):
        return "rewrite"

    # 검색 오류 등
    return "fallback"


# ===================================================
# 3. 검증 후 분기
# ===================================================

def route_verify(state):

    grade = state.get("grade", "retry")

    # 검증 성공
    if grade == "pass":
        return "end"

    # 더 이상 진행하지 않음
    if grade == "giveup":
        return "fallback"

    # 근거가 부족함
    # → 검색어를 바꿔 다시 검색
    if grade == "research":

        if state.get("rewrites", 0) >= MAX_REWRITE:
            return "fallback"

        return "rewrite"

    # 답변만 다시 만들어 보면 되는 경우
    if state.get("retries", 0) >= MAX_RETRY:
        return "fallback"

    return "retry"


# ===================================================
# 그래프 생성
# ===================================================

def build_graph():

    g = StateGraph(RAGState)


    # -------------------------------------------------
    # 노드 등록
    # -------------------------------------------------

    g.add_node("classify", classifier_node)

    g.add_node("greeting", greeting_node)
    g.add_node("calc", calc_node)
    g.add_node("scope", scope_node)

    g.add_node("retrieve", retriever_node)
    g.add_node("rewrite", rewrite_node)
    g.add_node("generate", generator_node)
    g.add_node("verify", verifier_node)

    g.add_node("bump", bump_node)
    g.add_node("fallback", fallback_node)


    # -------------------------------------------------
    # START → classify
    # -------------------------------------------------

    g.add_edge(START, "classify")


    # -------------------------------------------------
    # 질문 유형 분기
    # -------------------------------------------------

    g.add_conditional_edges(
        "classify",
        route_intent,
        {
            "greeting": "greeting",
            "calc": "calc",
            "scope": "scope",
            "document": "retrieve",
        }
    )

    g.add_edge("greeting", END)
    g.add_edge("calc", END)
    g.add_edge("scope", END)


    # -------------------------------------------------
    # Retriever 결과
    # -------------------------------------------------

    g.add_conditional_edges(
        "retrieve",
        route_retrieve,
        {
            "generate": "generate",

            # ★ 검색 실패
            "rewrite": "rewrite",

            "fallback": "fallback",
        }
    )


    # -------------------------------------------------
    # ★ Rewrite 후 다시 검색
    # -------------------------------------------------

    g.add_edge(
        "rewrite",
        "retrieve"
    )


    # -------------------------------------------------
    # 생성 → 검증
    # -------------------------------------------------

    g.add_edge(
        "generate",
        "verify"
    )


    # -------------------------------------------------
    # 검증 결과 분기
    # -------------------------------------------------

    g.add_conditional_edges(
        "verify",
        route_verify,
        {
            # 정상 종료
            "end": END,

            # 같은 근거로 다시 생성
            "retry": "bump",

            # 검색어를 바꿔 다시 검색
            "rewrite": "rewrite",

            # 포기
            "fallback": "fallback",
        }
    )


    # -------------------------------------------------
    # 재생성
    # -------------------------------------------------

    g.add_edge(
        "bump",
        "generate"
    )


    # -------------------------------------------------
    # Fallback
    # -------------------------------------------------

    g.add_edge(
        "fallback",
        END
    )


    return g.compile()


# ===================================================
# 그래프 컴파일
# ===================================================

app = build_graph()


# ===================================================
# 외부에서 호출
# ===================================================

def ask(question, verbose=False):

    state = make_initial_state(question)

    final = app.invoke(
        state,
        {
            "recursion_limit": 25
        }
    )

    if verbose:

        print(f"\nQ: {question}")

        for line in final.get("log", []):
            print("  ·", line)

    return {
        "answer": final.get("answer", ""),

        "intent": final.get("intent", ""),

        "grade": final.get("grade", ""),

        "reason": final.get("reason", ""),

        "retries": final.get("retries", 0),

        "rewrites": final.get("rewrites", 0),

        "tried_queries": final.get(
            "tried_queries",
            []
        ),

        "sources": [
            {
                "file": d.metadata.get("filename"),
                "page": d.metadata.get("page_no"),
            }
            for d in final.get("documents", [])
        ],

        "log": final.get("log", [])
    }


# ===================================================
# 직접 실행 테스트
# ===================================================

if __name__ == "__main__":

    questions = [
        "안녕하세요",
        "10 + 20",
        "오늘 날씨 어때요?",
        "환불은 며칠 이내에 신청해야 하나요?",
        "반품하고 싶은데 언제까지 가능해요?",
        "대표이사가 누구인가요?",
    ]

    for q in questions:

        result = ask(q, verbose=True)

        print("A:", result["answer"])

        print(
            "재생성:",
            result["retries"],
            "회"
        )

        print(
            "재작성:",
            result["rewrites"],
            "회"
        )

        print(
            "검색어:",
            result["tried_queries"]
        )

        print("-" * 60)