# 검색 결과에 따라 다음 노드를 선택하는 조건 분기 실습입니다.
# 결과가 있으면 답변하고, 없으면 같은 질문으로 다시 검색합니다.
# 반복 검색이 실행 제한에 도달하면 중단 안내를 출력합니다.

from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.errors import GraphRecursionError


# 1. 노드들이 함께 사용할 데이터 구조를 정의합니다.
class SimpleRAGState(TypedDict):
    query: str      # 사용자의 질문
    results: list   # 검색 결과 목록
    answer: str     # 최종 답변


# 2. 질문에 "가격"이 있으면 검색에 성공했다고 가정합니다.
def search_node(state: SimpleRAGState):
    query = state["query"]
    print("\n[검색] 질문:", query)

    # 실제 검색 대신 질문의 단어로 결과를 결정합니다.
    if "가격" in query:
        results = [
            "문서1: 제품 가격은 10,000원입니다.",
            "문서2: 배송비는 무료입니다.",
            "문서3: 현재 할인 행사가 진행 중입니다."
        ]
    else:
        results = []

    print("[검색] 결과:", results)

    # 변경할 검색 결과만 반환합니다.
    return {"results": results}


# 3. 검색 성공 시 예시 답변을 반환합니다.
def answer_node(state: SimpleRAGState):
    print("[답변] 답변을 생성합니다.")

    # 실제 LLM 대신 고정된 답변을 사용합니다.
    return {"answer": "검색 결과를 바탕으로 만든 답변입니다."}


# 4. 검색 결과의 유무에 따라 경로 이름을 반환합니다.
def check_search_quality(state: SimpleRAGState):
    # 검색 결과가 하나 이상이면 답변 경로를 선택합니다.
    if len(state["results"]) > 0:
        print("[판단] 검색 성공 → 답변")
        return "good"

    # 검색 결과가 없으면 재검색 경로를 선택합니다.
    print("[판단] 검색 실패 → 다시 검색")
    return "bad"


# 5. 그래프를 만들고 노드를 등록합니다.
graph = StateGraph(SimpleRAGState)

graph.add_node("search", search_node)
graph.add_node("answer", answer_node)

# 검색 노드부터 실행합니다.
graph.add_edge(START, "search")

# 판단 함수가 반환한 경로 이름에 따라 이동합니다.
graph.add_conditional_edges(
    "search",
    check_search_quality,
    {
        "good": "answer",  # 성공하면 답변 노드로 이동
        "bad": "search"    # 실패하면 검색 노드로 돌아감
    }
)

# 답변을 만들면 실행을 종료합니다.
graph.add_edge("answer", END)

# 그래프를 실행 가능한 형태로 만듭니다.
app = graph.compile()


# 6. 처음 전달할 데이터를 준비합니다.
initial_state = {
    "query": "제품 가격이 얼마야?",
    "results": [],
    "answer": ""
}


# 7. 그래프를 실행하고 최종 결과를 출력합니다.
try:
    # 그래프 실행 단계 수를 제한하여 무한 반복을 막습니다.
    result = app.invoke(initial_state, {"recursion_limit": 10})

    print("\n===== 최종 결과 =====")
    print("질문:", result["query"])
    print("검색 결과:", result["results"])
    print("답변:", result["answer"])

except GraphRecursionError:
    # 반복 검색이 실행 제한에 도달하면 안내합니다.
    print("\n[중단] 검색이 반복되어 실행 제한에 도달했습니다.")