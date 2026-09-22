import os
import sys
import warnings
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '18'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '19'))

from langgraph.graph import StateGraph, START, END
# from graph_state2 import RAGState
from graph_state2 import make_initial_state, RAGState
from retrieve import retrieve_node
from generate import generate_node
from fallback import fallback_node

# ── 라우팅 ──
def route_after_retrieve(state: RAGState) -> str:
    return "ok" if state.get("retrieval_ok") else "empty"

# ── 조립 ──
def build_graph():
    g = StateGraph(RAGState)
    
    g.add_node("retrieve", retrieve_node)
    g.add_node("generate", generate_node)
    g.add_node("fallback", fallback_node)
    g.add_edge(START, "retrieve")
    g.add_conditional_edges(
        "retrieve", route_after_retrieve,
        {"ok": "generate", "empty": "fallback"})
    g.add_edge("generate", END)
    g.add_edge("fallback", END)
    
    # ─────────────────────────────────────────     
    #  3부에서 여기에 추가됩니다
    #  26차시  verify 노드
    #  27차시  bump 노드 + 재생성 루프
    #  30차시  rewrite 노드 + 재검색 루프
    # ─────────────────────────────────────────     
    
    return g.compile()

app = build_graph()

def ask(question: str) -> dict:
    # 15차시 ask()와 같은 인터페이스를 유지한다     
    final = app.invoke(make_initial_state(question),                        
                       {"recursion_limit": 20})     
    return {
        "answer":  final["answer"],
        "sources": [{"file": d.metadata["filename"],
                     "page": d.metadata["page_no"]}
                    for d in final.get("documents", [])],
        "cited":   final.get("has_citation", False),
        "log":     final.get("log", []),
        "ok":      True,
    }
    
if __name__ == "__main__":
    print(app.get_graph().draw_ascii())