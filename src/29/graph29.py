import os
import sys


# ===================================================
# 다른 차시의 파일을 import하기 위한 경로 설정
# ===================================================

BASE_DIR = os.path.dirname(__file__)

sys.path.insert(0, os.path.join(BASE_DIR, "..", "18"))
sys.path.insert(0, os.path.join(BASE_DIR, "..", "19"))
sys.path.insert(0, os.path.join(BASE_DIR, "..", "24"))
sys.path.insert(0, os.path.join(BASE_DIR, "..", "25"))
sys.path.insert(0, os.path.join(BASE_DIR, "..", "26"))
sys.path.insert(0, os.path.join(BASE_DIR, "..", "29"))


# ===================================================
# 필요한 모듈 가져오기
# ===================================================

from langgraph.graph import StateGraph, START, END

from graph_state import RAGState
from graph_state2 import make_initial_state

from classifier import classifier_node
from intents import greeting_node, calc_node, scope_node

from retriever import retriever_node
from generator import generator_node
from verifier import verifier_node
from fallback import fallback_node

import config


MAX_RETRY = config.MAX_RETRY


# ===================================================
# 재시도 횟수 증가
# ===================================================

def bump_node(state):

    retries = state.get("retries", 0) + 1

    return {
        "retries": retries,
        "log": [f"재시도 {retries}회차"]
    }


# ===================================================
# 1. 질문 종류에 따라 이동할 곳 결정
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
# 2. 검색 결과에 따라 이동할 곳 결정
# ===================================================

def route_retrieve(state):

    if state.get("retrieval_ok"):
        return "success"

    return "fail"


# ===================================================
# 3. 검증 결과에 따라 이동할 곳 결정
# ===================================================

def route_verify(state):

    grade = state.get("grade", "retry")


    # 답변이 정상
    if grade == "pass":
        return "done"


    # 더 이상 진행할 수 없음
    if grade == "giveup":
        return "giveup"


    # 재시도 횟수를 모두 사용함
    if state.get("retries", 0) >= MAX_RETRY:
        return "giveup"


    # 다시 답변 생성
    return "retry"


# ===================================================
# 그래프 만들기
# ===================================================

def build_graph():

    graph = StateGraph(RAGState)


    # ------------------------------------------------
    # 노드 등록
    # ------------------------------------------------

    graph.add_node("classify", classifier_node)

    graph.add_node("greeting", greeting_node)
    graph.add_node("calc", calc_node)
    graph.add_node("scope", scope_node)

    graph.add_node("retrieve", retriever_node)
    graph.add_node("generate", generator_node)
    graph.add_node("verify", verifier_node)

    graph.add_node("bump", bump_node)
    graph.add_node("fallback", fallback_node)


    # ------------------------------------------------
    # 시작
    # ------------------------------------------------

    graph.add_edge(START, "classify")


    # ------------------------------------------------
    # 질문 종류에 따라 분기
    # ------------------------------------------------

    graph.add_conditional_edges(
        "classify",
        route_intent,
        {
            "greeting": "greeting",
            "calc": "calc",
            "scope": "scope",
            "document": "retrieve"
        }
    )


    # ------------------------------------------------
    # 간단한 질문은 바로 종료
    # ------------------------------------------------

    graph.add_edge("greeting", END)
    graph.add_edge("calc", END)
    graph.add_edge("scope", END)


    # ------------------------------------------------
    # 문서 검색 결과 확인
    # ------------------------------------------------

    graph.add_conditional_edges(
        "retrieve",
        route_retrieve,
        {
            "success": "generate",
            "fail": "fallback"
        }
    )


    # ------------------------------------------------
    # 답변 생성 후 검증
    # ------------------------------------------------

    graph.add_edge("generate", "verify")


    # ------------------------------------------------
    # 검증 결과에 따라 분기
    # ------------------------------------------------

    graph.add_conditional_edges(
        "verify",
        route_verify,
        {
            "done": END,
            "retry": "bump",
            "giveup": "fallback"
        }
    )


    # ------------------------------------------------
    # 재시도
    # ------------------------------------------------

    graph.add_edge("bump", "generate")


    # ------------------------------------------------
    # 실패 안내 후 종료
    # ------------------------------------------------

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

    # 초기 State 만들기
    state = make_initial_state(question)

    # 그래프 실행
    result = app.invoke(
        state,
        {"recursion_limit": 25}
    )

    return result


# ===================================================
# 직접 실행
# ===================================================

if __name__ == "__main__":

    questions = [
        "안녕하세요",
        "10 + 20",
        "오늘 날씨 어때요?",
        "환불은 며칠 이내에 신청해야 하나요?",
        "대표이사가 누구인가요?"
    ]


    for question in questions:

        print("\n===================================")
        print("질문:", question)

        result = ask(question)

        print("답변:", result.get("answer", ""))
        print("분류:", result.get("intent", ""))
        print("판정:", result.get("grade", ""))
        print("재시도:", result.get("retries", 0))