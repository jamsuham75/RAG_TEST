# 검색 결과에 따라 답변 또는 재검색으로 이동하는 그래프를 만듭니다.
# 완성된 그래프를 PNG 이미지로 만들어 화면에 표시합니다.
# 이 코드는 그래프 구조만 시각화하며, 검색과 답변을 실행하지 않습니다.

from typing import TypedDict
from langgraph.graph import StateGraph

import io
import matplotlib.pyplot as plt
from PIL import Image


# 1. 노드들이 함께 사용할 데이터 구조를 정의합니다.
class SimpleRAGState(TypedDict):
    query: str      # 사용자의 질문
    results: list   # 검색 결과 목록
    answer: str     # 최종 답변


# 2. 질문에 "가격"이 있으면 검색에 성공했다고 가정합니다.
def search_node(state: SimpleRAGState):
    # State에서 사용자의 질문을 읽습니다.
    query = state["query"]
    print("\n[검색 Node] 질문:", query)

    # 실제 검색 대신 질문에 포함된 단어를 확인합니다.
    if "가격" in query:
        results = [
            "문서1: 제품 가격은 10,000원입니다.",
            "문서2: 배송비는 무료입니다.",
            "문서3: 현재 할인 행사가 진행 중입니다."
        ]
    else:
        results = []

    print("[검색 Node] 검색 결과:", results)

    # State를 직접 수정하지 않고 검색 결과만 반환합니다.
    return {"results": results}


# 3. 검색 성공 시 예시 답변을 반환합니다.
def answer_node(state: SimpleRAGState):
    print("\n[답변 Node] 검색 결과를 이용하여 답변을 생성합니다.")

    # 실제 LLM 대신 고정된 답변을 사용합니다.
    return {"answer": "검색 결과를 바탕으로 만든 답변입니다."}


# 4. 검색 결과가 있는지 검사하여 다음 경로를 선택합니다.
def check_search_quality(state: SimpleRAGState):
    # 검색 결과가 있으면 답변 경로를 선택합니다.
    if len(state["results"]) > 0:
        return "good"
    else:
        return "bad"


# 5. 그래프를 만들고 사용할 노드를 등록합니다.
graph = StateGraph(SimpleRAGState)

graph.add_node("search", search_node)
graph.add_node("answer", answer_node)


# 6. 검색 후 조건 검사 결과에 따라 이동합니다.
graph.add_conditional_edges(
    "search",
    check_search_quality,
    {
        "good": "answer",  # 검색 성공 → 답변
        "bad": "search"    # 검색 실패 → 다시 검색
    }
)

# 검색에서 시작하고 답변 후 종료합니다.
graph.set_entry_point("search")
graph.set_finish_point("answer")

# 그래프를 실행 가능한 형태로 만듭니다.
runnable = graph.compile()


# 7. 그래프 구조를 PNG 이미지 데이터로 만듭니다.
print("Graph 이미지를 생성합니다...")

image_data = runnable.get_graph().draw_mermaid_png()

# PNG 바이트 데이터를 메모리상의 파일처럼 다룹니다.
image_file = io.BytesIO(image_data)

# 메모리상의 PNG 데이터를 PIL 이미지 객체로 엽니다.
image = Image.open(image_file)


# 8. 그래프 이미지를 화면에 표시합니다.
plt.figure(figsize=(8, 6))  # 그림의 가로·세로 크기를 지정합니다.
plt.imshow(image)          # PIL 이미지를 표시합니다.
plt.axis("off")            # 좌표축과 눈금을 숨깁니다.
plt.title("LangGraph - Conditional RAG Graph")
plt.show()                 # 그림 창을 화면에 띄웁니다.