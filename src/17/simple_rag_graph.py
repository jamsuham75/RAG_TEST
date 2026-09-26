# LangGraph에서 검색 → 답변 순서로 실행하는 기본 실습입니다.
# State를 통해 질문, 검색 결과, 답변을 전달합니다.
# 실제 검색과 LLM 대신 미리 작성한 데이터를 사용합니다.

from typing import TypedDict
from langgraph.graph import StateGraph, START, END


# 1. 노드들이 함께 사용할 데이터의 구조를 정의합니다.
class SimpleRAGState(TypedDict):
    query: str      # 사용자의 질문
    results: list   # 검색 결과 목록
    answer: str     # 최종 답변


# 2. 질문을 확인하고 예시 검색 결과를 반환합니다.
def search_node(state: SimpleRAGState):
    # 현재 State에서 질문을 읽습니다.
    print("[검색 노드] 질문:", state["query"])

    # 실제 검색 대신 고정된 문서 목록을 준비합니다.
    results = [
        "문서1: 제품 가격은 10,000원입니다.",
        "문서2: 배송비는 무료입니다.",
        "문서3: 현재 할인 행사가 진행 중입니다."
    ]

    # LangGraph가 results 항목을 갱신하도록 반환합니다.
    return {"results": results}


# 3. 검색 결과를 확인하고 예시 답변을 반환합니다.
def answer_node(state: SimpleRAGState):
    # 앞의 검색 노드가 반환한 결과를 읽습니다.
    print("[답변 노드] 검색 결과:", state["results"])

    # 실제 LLM 대신 고정된 답변을 준비합니다.
    answer = "검색 결과를 바탕으로 만든 답변입니다."

    # LangGraph가 answer 항목을 갱신하도록 반환합니다.
    return {"answer": answer}


# 4. State의 구조를 지정하여 그래프를 만듭니다.
graph = StateGraph(SimpleRAGState)

# 각 함수를 그래프에서 실행할 노드로 등록합니다.
graph.add_node("search", search_node)
graph.add_node("answer", answer_node)

# 시작 → 검색 → 답변 → 종료 순서로 연결합니다.
graph.add_edge(START, "search")
graph.add_edge("search", "answer")
graph.add_edge("answer", END)

# 연결한 그래프를 실행 가능한 형태로 만듭니다.
app = graph.compile()


# 5. 그래프에 처음 전달할 데이터를 준비합니다.
initial_state = {
    "query": "가격이 얼마야?",
    "results": [],
    "answer": ""
}

# 그래프를 실행하고 최종 State를 받습니다.
result = app.invoke(initial_state)


# 6. 최종 State에 담긴 값을 출력합니다.
print("\n===== 최종 결과 =====")
print("질문:", result["query"])
print("검색 결과:", result["results"])
print("답변:", result["answer"])