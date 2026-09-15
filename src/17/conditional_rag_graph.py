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

    query = state["query"]

    print(f"\n[검색 Node] 질문: {query}")

    # 실제 검색 대신 간단한 조건으로 검색 결과를 만듦
    # "가격"이라는 단어가 있으면 검색 성공
    if "가격" in query:
        results = [
            "문서1: 제품 가격은 10,000원입니다.",
            "문서2: 배송비는 무료입니다.",
            "문서3: 현재 할인 행사가 진행 중입니다."
        ]
    else:
        # 검색 결과가 없는 경우
        results = []

    state["results"] = results

    print("[검색 Node] 검색 결과:", results)

    return state


def answer_node(state: SimpleRAGState):
    """답변 생성을 담당하는 Node"""

    results = state["results"]

    print("\n[답변 Node] 검색 결과를 이용하여 답변을 생성합니다.")

    # 실제 LLM 대신 더미 답변 사용
    answer = "검색 결과를 바탕으로 만든 답변입니다."

    state["answer"] = answer

    return state


# =========================================================
# Step 3. 검색 결과의 품질을 판단하는 함수
# =========================================================

def check_search_quality(state: SimpleRAGState):

    print("\n[조건 검사] 검색 결과를 확인합니다.")

    # 검색 결과가 하나 이상 있으면 good
    if len(state["results"]) > 0:
        print("[조건 검사] 검색 결과 있음 → good")
        return "good"

    # 검색 결과가 없으면 bad
    else:
        print("[조건 검사] 검색 결과 없음 → bad")
        return "bad"


# =========================================================
# Step 4. Graph 만들기
# =========================================================

graph = StateGraph(SimpleRAGState)

# Node 추가
graph.add_node("search", search_node)
graph.add_node("answer", answer_node)


# =========================================================
# Step 5. Conditional Edge 추가
# =========================================================

graph.add_conditional_edges(
    "search",                  # search Node 실행 후
    check_search_quality,      # 이 함수로 상태를 판단
    {
        "good": "answer",      # good → answer Node
        "bad": "search"        # bad  → 다시 search Node
    }
)


# 시작점 설정
graph.set_entry_point("search")

# 끝점 설정
graph.set_finish_point("answer")


# =========================================================
# Step 6. Graph 컴파일
# =========================================================

runnable = graph.compile()


# =========================================================
# Step 7. Graph 실행
# =========================================================

input_state = {
    "query": "제품 똥이 얼마야?",
    "results": [],
    "answer": ""
}

output_state = runnable.invoke(input_state)


# =========================================================
# Step 8. 최종 결과 확인
# =========================================================

print("\n===== 최종 결과 =====")
print("질문:", output_state["query"])
print("검색 결과:", output_state["results"])
print("답변:", output_state["answer"])