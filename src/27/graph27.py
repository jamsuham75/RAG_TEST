import os
import sys

BASE = os.path.dirname(__file__)

# 필요한 차시 폴더 등록
for folder in ["18", "19", "24", "25", "26"]:
    sys.path.insert(0, os.path.join(BASE, "..", folder))


from langgraph.graph import StateGraph, START, END

from graph_state import RAGState
from graph_state2 import make_initial_state

from retriever import retriever_node
from generator import generator_node
from verifier import verifier_node
from fallback import fallback_node

import config


MAX_RETRY = getattr(config, "MAX_RETRY", 2)


# 재시도 횟수 +1
def bump_node(state):
    n = state.get("retries", 0) + 1

    return {
        "retries": n,
        "log": [f"재시도 {n}회차 진입"]
    }


# 검색 후 어디로 갈지 결정
def route_retrieve(state):

    if state.get("retrieval_ok"):
        return "ok"

    return "empty"


# 검증 후 어디로 갈지 결정
def route_verify(state):

    grade = state.get("grade", "retry")

    if grade == "pass":
        return "done"

    if grade == "giveup":
        return "giveup"

    if state.get("retries", 0) >= MAX_RETRY:
        return "giveup"

    return "retry"


# 그래프 만들기
def build_graph():

    g = StateGraph(RAGState)

    # 노드
    g.add_node("retrieve", retriever_node)
    g.add_node("generate", generator_node)
    g.add_node("verify", verifier_node)
    g.add_node("bump", bump_node)
    g.add_node("fallback", fallback_node)

    # 시작
    g.add_edge(START, "retrieve")

    # 검색 후
    g.add_conditional_edges(
        "retrieve",
        route_retrieve,
        {
            "ok": "generate",
            "empty": "fallback"
        }
    )

    # 생성 후 검증
    g.add_edge("generate", "verify")

    # 검증 후
    g.add_conditional_edges(
        "verify",
        route_verify,
        {
            "done": END,
            "giveup": "fallback",
            "retry": "bump"
        }
    )

    # 재시도
    g.add_edge("bump", "generate")

    # 실패
    g.add_edge("fallback", END)

    return g.compile()


app = build_graph()


# 질문하기
def ask(question):

    state = make_initial_state(question)
    result = app.invoke(state, {"recursion_limit": 25})

    return {
        "answer": result.get("answer", ""),
        "grade": result.get("grade", ""),
        "reason": result.get("reason", ""),
        "retries": result.get("retries", 0)
    }


# 테스트
if __name__ == "__main__":

    questions = [
        "환불은 며칠 이내에 신청해야 하나요?",
        "대표이사가 누구인가요?"
    ]

    for question in questions:

        result = ask(question)

        print()
        print("Q:", question)
        print("A:", result["answer"])
        print("판정:", result["grade"])
        print("재시도:", result["retries"])