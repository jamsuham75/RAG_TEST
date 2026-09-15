from typing import TypedDict
from langgraph.graph import StateGraph

import matplotlib.pyplot as plt
from PIL import Image
import io


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
    # query에 "가격"이라는 단어가 있으면 검색 성공으로 가정
    if "가격" in query:
        results = [
            "문서1: 제품 가격은 10,000원입니다.",
            "문서2: 배송비는 무료입니다.",
            "문서3: 현재 할인 행사가 진행 중입니다."
        ]
    else:
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
# Step 3. 검색 결과 품질 판단 함수
# =========================================================

def check_search_quality(state: SimpleRAGState):
    """검색 결과가 있는지 확인"""

    if len(state["results"]) > 0:
        return "good"
    else:
        return "bad"


# =========================================================
# Step 4. Graph 생성
# =========================================================

graph = StateGraph(SimpleRAGState)


# =========================================================
# Step 5. Node 추가
# =========================================================

graph.add_node("search", search_node)
graph.add_node("answer", answer_node)


# =========================================================
# Step 6. Conditional Edge 추가
# =========================================================

graph.add_conditional_edges(
    "search",
    check_search_quality,
    {
        "good": "answer",
        "bad": "search"
    }
)


# =========================================================
# Step 7. 시작점과 끝점 설정
# =========================================================

graph.set_entry_point("search")
graph.set_finish_point("answer")


# =========================================================
# Step 8. Graph 컴파일
# =========================================================

runnable = graph.compile()


# =========================================================
# Step 9. Graph 시각화
# =========================================================

print("Graph 이미지를 생성합니다...")

# 컴파일된 Graph를 Mermaid PNG로 변환
image_data = runnable.get_graph().draw_mermaid_png()

# PNG 데이터를 PIL 이미지로 변환
image = Image.open(io.BytesIO(image_data))

# 이미지 출력
plt.figure(figsize=(8, 6))
plt.imshow(image)
plt.axis("off")
plt.title("LangGraph - Conditional RAG Graph")
plt.show()