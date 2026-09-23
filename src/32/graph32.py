# ===================================================
# graph32.py
# 32차시 - Modular RAG 종합
# ===================================================

import os
import sys

from langgraph.graph import StateGraph, START, END


# ===================================================
# 이전 차시 모듈 경로
# ===================================================

BASE_DIR = os.path.dirname(__file__)

for folder in ["18", "19", "24", "25", "26", "29", "30", "31"]:
    sys.path.insert(0, os.path.join(BASE_DIR, "..", folder))


# ===================================================
# 필요한 모듈 불러오기
# ===================================================

from graph_state2 import RAGState, make_initial_state

from classifier import classifier_node
from intents import greeting_node, calc_node, scope_node

from retriever import retriever_node
from generator import generator_node
from verifier import verifier_node
from rewriter import rewrite_node
from fallback import fallback_node

import config


# ===================================================
# 최대 재시도 횟수
# ===================================================

MAX_RETRY = getattr(config, "MAX_RETRY", 2)
MAX_REWRITE = getattr(config, "MAX_REWRITE", 2)


# ===================================================
# 재생성 횟수 증가
# ===================================================

def bump_node(state):

    retries = state.get("retries", 0) + 1

    return {
        "retries": retries,
        "log": [f"재생성 {retries}회차"]
    }


# ===================================================
# 1. 질문 분류 후 어디로 갈지 결정
# ===================================================

def route_by_intent(state):

    intent = state.get("intent", "document")

    if intent == "greeting":
        return "greeting"

    if intent == "calc":
        return "calc"

    if intent == "scope":
        return "scope"

    return "document"


# ===================================================
# 2. 검색 후 어디로 갈지 결정
# ===================================================

def route_after_retrieve(state):

    # 검색 성공
    if state.get("retrieval_ok"):
        return "ok"

    # 재검색 횟수를 모두 사용함
    if state.get("rewrites", 0) >= MAX_REWRITE:
        return "giveup"

    # 검색 오류라면 재검색하지 않고 종료
    if state.get("fail_reason") in (
        "search_error",
        "no_result",
        "empty_query"
    ):
        return "giveup"

    # 검색 결과가 좋지 않으면 질문을 고쳐 다시 검색
    return "research"


# ===================================================
# 3. 답변 검증 후 어디로 갈지 결정
# ===================================================

def route_after_verify(state):

    grade = state.get("grade", "retry")

    # 답변 정상
    if grade == "pass":
        return "done"

    # 더 이상 진행할 수 없음
    if grade == "giveup":
        return "giveup"

    # 검색 자료가 부족함 → 다시 검색
    if grade == "research":

        if state.get("rewrites", 0) >= MAX_REWRITE:
            return "giveup"

        return "research"

    # 답변만 다시 생성
    if state.get("retries", 0) < MAX_RETRY:
        return "regenerate"

    return "giveup"


# ===================================================
# 4. 질문 재작성 후 어디로 갈지 결정
# ===================================================

def route_after_rewrite(state):

    if state.get("query"):
        return "retry_search"

    return "giveup"


# ===================================================
# 그래프 만들기
# ===================================================

def build_graph():

    graph = StateGraph(RAGState)


    # -------------------------------------------------
    # 노드 등록
    # -------------------------------------------------

    graph.add_node("classify", classifier_node)

    graph.add_node("greeting", greeting_node)
    graph.add_node("calc", calc_node)
    graph.add_node("scope", scope_node)

    graph.add_node("retrieve", retriever_node)
    graph.add_node("generate", generator_node)
    graph.add_node("verify", verifier_node)

    graph.add_node("bump", bump_node)
    graph.add_node("rewrite", rewrite_node)
    graph.add_node("fallback", fallback_node)


    # -------------------------------------------------
    # START → 질문 분류
    # -------------------------------------------------

    graph.add_edge(START, "classify")


    # -------------------------------------------------
    # 질문 종류에 따른 분기
    # -------------------------------------------------

    graph.add_conditional_edges(
        "classify",
        route_by_intent,
        {
            "greeting": "greeting",
            "calc": "calc",
            "scope": "scope",
            "document": "retrieve"
        }
    )


    # 인사 / 계산 / 범위 밖 질문은 바로 종료
    graph.add_edge("greeting", END)
    graph.add_edge("calc", END)
    graph.add_edge("scope", END)


    # -------------------------------------------------
    # 검색 후 분기
    # -------------------------------------------------

    graph.add_conditional_edges(
        "retrieve",
        route_after_retrieve,
        {
            "ok": "generate",
            "research": "rewrite",
            "giveup": "fallback"
        }
    )


    # -------------------------------------------------
    # 답변 생성 → 검증
    # -------------------------------------------------

    graph.add_edge("generate", "verify")


    # -------------------------------------------------
    # 검증 후 분기
    # -------------------------------------------------

    graph.add_conditional_edges(
        "verify",
        route_after_verify,
        {
            "done": END,
            "regenerate": "bump",
            "research": "rewrite",
            "giveup": "fallback"
        }
    )


    # -------------------------------------------------
    # 재생성
    # -------------------------------------------------

    graph.add_edge("bump", "generate")


    # -------------------------------------------------
    # 재검색
    # -------------------------------------------------

    graph.add_conditional_edges(
        "rewrite",
        route_after_rewrite,
        {
            "retry_search": "retrieve",
            "giveup": "fallback"
        }
    )


    # -------------------------------------------------
    # 실패 안내 후 종료
    # -------------------------------------------------

    graph.add_edge("fallback", END)


    return graph.compile()


# ===================================================
# 그래프 생성
# ===================================================

app = build_graph()


# ===================================================
# 질문 실행 함수
# ===================================================

def ask(question):

    state = make_initial_state(question)

    result = app.invoke(
        state,
        {"recursion_limit": 40}
    )

    return result


# ===================================================
# 테스트
# ===================================================

if __name__ == "__main__":

    question = "만불은 며칠 이내에 신청해야 하나요?"

    result = ask(question)

    print("질문 :", question)
    print("답변 :", result.get("answer"))
    print("의도 :", result.get("intent"))
    print("판정 :", result.get("grade"))
    print("재생성 :", result.get("retries", 0))
    print("재검색 :", result.get("rewrites", 0))