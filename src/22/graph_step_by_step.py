import os
import sys

# --------------------------------------------------
# 18차시와 19차시 모듈 경로 추가
# --------------------------------------------------
BASE_DIR = os.path.dirname(__file__)

sys.path.insert(
    0,
    os.path.join(BASE_DIR, "..", "18")
)

sys.path.insert(
    0,
    os.path.join(BASE_DIR, "..", "19")
)


# --------------------------------------------------
# LangGraph 및 노드 import
# --------------------------------------------------
from langgraph.graph import StateGraph, START, END

from graph_state import RAGState
from graph_state2 import make_initial_state

from retrieve import retrieve_node
from generate import generate_node
from fallback import fallback_node


# --------------------------------------------------
# 검색 결과에 따른 라우팅 함수
# --------------------------------------------------
def route_after_retrieve(state: RAGState) -> str:
    """
    검색 결과가 있으면 generate로,
    검색 결과가 없으면 fallback으로 이동시킵니다.
    """

    if state.get("retrieval_ok"):
        return "ok"

    return "empty"


# ==================================================
# 1단계: retrieve 노드만 연결
# ==================================================
def build_step1_graph():
    g = StateGraph(RAGState)

    # retrieve 노드 등록
    g.add_node("retrieve", retrieve_node)

    # START → retrieve → END
    g.add_edge(START, "retrieve")
    g.add_edge("retrieve", END)

    return g.compile()


def test_step1():
    print("\n" + "=" * 60)
    print("1단계: retrieve 노드만 연결")
    print("=" * 60)

    app = build_step1_graph()

    result = app.invoke(
        make_initial_state("환불은 며칠 이내인가요?")
    )

    print("검색 결과:", len(result.get("documents", [])), "건")
    print("점수:", result.get("scores", []))
    print("검색 성공 여부:", result.get("retrieval_ok"))


# ==================================================
# 2단계: retrieve + generate 연결
# ==================================================
def build_step2_graph():
    g = StateGraph(RAGState)

    # 노드 등록
    g.add_node("retrieve", retrieve_node)
    g.add_node("generate", generate_node)

    # START → retrieve → generate → END
    g.add_edge(START, "retrieve")
    g.add_edge("retrieve", "generate")
    g.add_edge("generate", END)

    return g.compile()


def test_step2():
    print("\n" + "=" * 60)
    print("2단계: generate 노드 추가")
    print("=" * 60)

    app = build_step2_graph()

    result = app.invoke(
        make_initial_state("환불은 며칠 이내인가요?")
    )

    print("답변:")
    print(result.get("answer", ""))


# ==================================================
# 3단계: 조건 분기와 fallback 추가
# ==================================================
def build_step3_graph():
    g = StateGraph(RAGState)

    # 노드 등록
    g.add_node("retrieve", retrieve_node)
    g.add_node("generate", generate_node)
    g.add_node("fallback", fallback_node)

    # START → retrieve
    g.add_edge(START, "retrieve")

    # retrieve 결과에 따른 조건부 분기
    g.add_conditional_edges(
        "retrieve",
        route_after_retrieve,
        {
            "ok": "generate",
            "empty": "fallback",
        }
    )

    # 각 경로의 종료 연결
    g.add_edge("generate", END)
    g.add_edge("fallback", END)

    return g.compile()


def test_step3():
    print("\n" + "=" * 60)
    print("3단계: 조건 분기와 fallback 추가")
    print("=" * 60)

    app = build_step3_graph()

    # 검색 결과가 있을 것으로 예상되는 질문
    print("\n[정상 질문]")
    result1 = app.invoke(
        make_initial_state("환불은 며칠 이내인가요?")
    )

    print("답변:")
    print(result1.get("answer", ""))
    print("실행 로그:", result1.get("log", []))

    # 검색 결과가 없을 것으로 예상되는 질문
    print("\n[검색 실패 질문]")
    result2 = app.invoke(
        make_initial_state("대표이사가 누구인가요?")
    )

    print("답변:")
    print(result2.get("answer", ""))
    print("실행 로그:", result2.get("log", []))


# ==================================================
# 그래프 구조 출력
# ==================================================
def print_graphs():
    print("\n" + "=" * 60)
    print("그래프 구조 확인")
    print("=" * 60)

    print("\n[1단계 그래프]")
    app1 = build_step1_graph()
    print(app1.get_graph().draw_ascii())

    print("\n[2단계 그래프]")
    app2 = build_step2_graph()
    print(app2.get_graph().draw_ascii())

    print("\n[3단계 그래프]")
    app3 = build_step3_graph()
    print(app3.get_graph().draw_ascii())


# ==================================================
# 프로그램 시작
# ==================================================
if __name__ == "__main__":

    # 1단계 테스트
    test_step1()

    # 2단계 테스트
    test_step2()

    # 3단계 테스트
    test_step3()

    # 그래프 모양 출력
    print_graphs()