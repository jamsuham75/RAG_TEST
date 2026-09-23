# ===================================================
# graph31.py
# 31차시 - 방어적 코딩 + 운영 로그
# ===================================================

import os
import sys
import time
import warnings

warnings.filterwarnings("ignore")


# ===================================================
# 모듈 경로
# ===================================================

BASE_DIR = os.path.dirname(__file__)

for folder in ["18", "19", "24", "25", "26", "29", "30"]:
    sys.path.insert(
        0,
        os.path.join(BASE_DIR, "..", folder)
    )

sys.path.insert(0, BASE_DIR)


# ===================================================
# import
# ===================================================

from langgraph.graph import StateGraph, START, END

from graph_state2 import RAGState, make_initial_state

from retriever import retriever_node
from generator import generator_node
from verifier import verifier_node
from fallback import fallback_node

from classifier import classifier_node
from intents import greeting_node, calc_node, scope_node
from rewriter import rewrite_node

from safe import safe_node
from logger import log_query

import config


# ===================================================
# 설정
# ===================================================

# ===================================================
# 설정
# ===================================================

MAX_RETRY = getattr(config, "MAX_RETRY", 2)
MAX_REWRITE = getattr(config, "MAX_REWRITE", 2)


# ===================================================
# 안전 노드
# ===================================================

def safe_retriever_node(state):

    result = safe_node(retriever_node, state)

    if result.get("node_error"):
        result["documents"] = []
        result["retrieval_ok"] = False
        result["fail_reason"] = "search_error"

    return result


def safe_generator_node(state):

    result = safe_node(generator_node, state)

    if result.get("node_error"):
        result["answer"] = ""
        result["insufficient"] = True
        result["gen_error"] = "unknown"

    return result


def safe_verifier_node(state):

    result = safe_node(verifier_node, state)

    if result.get("node_error"):
        result["grade"] = "pass"
        result["reason"] = "검증 오류 - 통과 처리"
        result["verified"] = False

    return result


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
# 질문 종류에 따른 분기
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
# 검색 후 분기
# ===================================================

def route_after_retrieve(state):

    # 검색 성공
    if state.get("retrieval_ok"):
        return "ok"

    # 재작성 횟수 초과
    if state.get("rewrites", 0) >= MAX_REWRITE:
        return "giveup"

    fail_reason = state.get("fail_reason", "")

    # 검색 자체는 성공했지만 좋은 자료가 없음
    if fail_reason in ["low_score", ""]:
        return "research"

    # 검색 시스템 오류
    return "giveup"


# ===================================================
# 검증 후 분기
# ===================================================

def route_after_verify(state):

    grade = state.get("grade", "retry")

    # 정상 답변
    if grade == "pass":
        return "done"

    # 포기
    if grade == "giveup":
        return "giveup"

    # 자료를 다시 검색해야 함
    if grade == "research":

        if state.get("rewrites", 0) >= MAX_REWRITE:
            return "giveup"

        return "research"

    # 같은 자료로 다시 답변 생성
    if state.get("retries", 0) >= MAX_RETRY:
        return "giveup"

    return "regenerate"


# ===================================================
# 질문 재작성 후 분기
# ===================================================

def route_after_rewrite(state):

    query = state.get("query", "")
    tried_queries = state.get("tried_queries", [])

    if not query:
        return "giveup"

    if query in tried_queries:
        return "retry_search"

    return "giveup"


# ===================================================
# 그래프 만들기
# ===================================================

def build_graph():

    g = StateGraph(RAGState)


    # -------------------------------
    # 노드 등록
    # -------------------------------

    g.add_node("classify", classifier_node)

    g.add_node("greeting", greeting_node)
    g.add_node("calc", calc_node)
    g.add_node("scope", scope_node)

    g.add_node("retrieve", safe_retriever_node)
    g.add_node("generate", safe_generator_node)
    g.add_node("verify", safe_verifier_node)

    g.add_node("bump", bump_node)
    g.add_node("rewrite", rewrite_node)
    g.add_node("fallback", fallback_node)


    # -------------------------------
    # 시작
    # -------------------------------

    g.add_edge(START, "classify")


    # -------------------------------
    # 질문 분류
    # -------------------------------

    g.add_conditional_edges(
        "classify",
        route_by_intent,
        {
            "greeting": "greeting",
            "calc": "calc",
            "scope": "scope",
            "document": "retrieve"
        }
    )

    g.add_edge("greeting", END)
    g.add_edge("calc", END)
    g.add_edge("scope", END)


    # -------------------------------
    # 검색 후
    # -------------------------------

    g.add_conditional_edges(
        "retrieve",
        route_after_retrieve,
        {
            "ok": "generate",
            "research": "rewrite",
            "giveup": "fallback"
        }
    )


    # -------------------------------
    # 생성 후 검증
    # -------------------------------

    g.add_edge("generate", "verify")


    # -------------------------------
    # 검증 후
    # -------------------------------

    g.add_conditional_edges(
        "verify",
        route_after_verify,
        {
            "done": END,
            "regenerate": "bump",
            "research": "rewrite",
            "giveup": "fallback"
        }
    )


    # -------------------------------
    # 재생성
    # -------------------------------

    g.add_edge("bump", "generate")


    # -------------------------------
    # 재검색
    # -------------------------------

    g.add_conditional_edges(
        "rewrite",
        route_after_rewrite,
        {
            "retry_search": "retrieve",
            "giveup": "fallback"
        }
    )


    # -------------------------------
    # 실패
    # -------------------------------

    g.add_edge("fallback", END)


    return g.compile()


# ===================================================
# 그래프 생성
# ===================================================

app = build_graph()


# ===================================================
# 질문 실행
# ===================================================

def ask(question, verbose=False):

    start = time.time()

    state = make_initial_state(question)

    final = app.invoke(
        state,
        {"recursion_limit": 25}
    )

    elapsed = time.time() - start


    # 운영 로그 저장
    log_query(
        question,
        final,
        elapsed
    )


    # 실행 과정 출력
    if verbose:

        print(f"\nQ: {question}")

        for line in final.get("log", []):
            print("  ·", line)


    # 출처 만들기
    sources = []

    for doc in final.get("documents", []):

        sources.append({
            "file": doc.metadata.get("filename"),
            "page": doc.metadata.get("page_no")
        })


    # 결과 반환
    return {
        "answer": final.get("answer", ""),
        "sources": sources,

        "intent": final.get("intent", ""),
        "grade": final.get("grade", ""),
        "reason": final.get("reason", ""),

        "retries": final.get("retries", 0),
        "rewrites": final.get("rewrites", 0),

        "tried_queries": final.get(
            "tried_queries",
            []
        ),

        "verified": (
            final.get("grade") == "pass"
            and not final.get("node_error")
        ),

        "node_error": final.get("node_error", ""),
        "fail_reason": final.get("fail_reason", ""),
        "fallback_kind": final.get("fallback_kind", ""),

        "log": final.get("log", []),

        "ok": True
    }


# ===================================================
# 테스트
# ===================================================

if __name__ == "__main__":

    print(app.get_graph().draw_ascii())


    questions = [
        "안녕하세요",
        "10 + 20",
        "오늘 날씨 어때요?",
        "환불은 며칠 이내에 신청해야 하나요?",
        "대표이사가 누구인가요?"
    ]


    for question in questions:

        result = ask(
            question,
            verbose=True
        )

        print("A:", result["answer"])
        print("의도:", result["intent"])
        print("판정:", result["grade"])
        print("재시도:", result["retries"])
        print("재작성:", result["rewrites"])

        if result["node_error"]:
            print("노드 오류:", result["node_error"])

        print()