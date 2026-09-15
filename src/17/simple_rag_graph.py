from typing import TypedDict
from langgraph.graph import StateGraph


# =========================================================
# Step 1. State 정의
# =========================================================

class SimpleRAGState(TypedDict):
    query: str
    results: list
    answer: str


# =========================================================
# Step 2. Node 정의
# =========================================================

def search_node(state: SimpleRAGState):
    """검색을 담당하는 Node"""

    # State에서 사용자의 질문을 가져옴
    query = state["query"]

    print(f"[검색 Node] 질문: {query}")

    # 실제 검색 대신 더미 검색 결과 사용
    results = [
        "문서1: 제품 가격은 10,000원입니다.",
        "문서2: 배송비는 무료입니다.",
        "문서3: 현재 할인 행사가 진행 중입니다."
    ]

    # State에 검색 결과 추가
    state["results"] = results

    return state


def answer_node(state: SimpleRAGState):
    """답변 생성을 담당하는 Node"""

    # State에서 검색 결과를 가져옴
    results = state["results"]

    print(f"[답변 Node] 검색 결과: {results}")

    # 실제 LLM 대신 더미 답변 사용
    answer = "검색 결과를 바탕으로 만든 답변입니다."

    # State에 답변 추가
    state["answer"] = answer

    return state


# =========================================================
# Step 3. Graph 만들기
# =========================================================

graph = StateGraph(SimpleRAGState)

# Node 등록
graph.add_node("search", search_node)
graph.add_node("answer", answer_node)

# Node 연결
graph.add_edge("search", "answer")

# 시작 Node
graph.set_entry_point("search")

# 마지막 Node
graph.set_finish_point("answer")


# =========================================================
# Step 4. Graph 컴파일
# =========================================================

runnable = graph.compile()


# =========================================================
# Step 5. Graph 실행
# =========================================================

input_state = {
    "query": "가격이 얼마야?",
    "results": [],
    "answer": ""
}

output_state = runnable.invoke(input_state)


# =========================================================
# Step 6. 최종 결과 확인
# =========================================================

print("\n===== 최종 결과 =====")
print("질문:", output_state["query"])
print("검색 결과:", output_state["results"])
print("답변:", output_state["answer"])