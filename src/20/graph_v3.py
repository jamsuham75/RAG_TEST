import os
import sys
import warnings

warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "18"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "19"))

from langgraph.graph import StateGraph, START, END

from graph_state import RAGState
from retrieve import retrieve_node
from generate import generate_node
from fallback import fallback_node
from routes import route_after_retrieve


# 그래프 생성
g = StateGraph(RAGState)


# 노드 등록
g.add_node("retrieve", retrieve_node)
g.add_node("generate", generate_node)
g.add_node("fallback", fallback_node)


# Edge 연결
g.add_edge(START, "retrieve")

g.add_conditional_edges(
    "retrieve",
    route_after_retrieve,
    {
        "ok": "generate",
        "empty": "fallback",
    },
)

g.add_edge("generate", END)
g.add_edge("fallback", END)


# 그래프 컴파일
app = g.compile()


# 그래프 실행 함수
def run(question):
    init = {
        "question": question,
        "query": question,
        "retries": 0,
        "log": [],
        "tried_queries": [],
    }

    final = app.invoke(init)

    print("Q:", question)
    print("A:", final["answer"][:70])

    for line in final["log"]:
        print("   ", line)

    print("-" * 55)


# 테스트 실행
run("환불은 며칠 이내인가요?")
run("대표이사 이름은?")