import os
import sys
import warnings
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '18'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '19'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '25'))

from langgraph.graph import StateGraph, START, END
from graph_state import RAGState
from graph_state2 import make_initial_state
from retriever import retriever_node
from generator import generator_node
from fallback import fallback_node

# ── 라우팅 ──
def route_after_retrieve(state: RAGState) -> str:
    return "ok" if state.get("retrieval_ok") else "empty"

# ── 조립 ──
def build_graph():
    g = StateGraph(RAGState)
    
    g.add_node("retrieve", retriever_node)
    g.add_node("generate", generator_node)
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
        "sources": [{"file": d.metadata["filename"],                      "page": d.metadata["page_no"]}                    for d in final.get("documents", [])],
        "cited":   final.get("has_citation", False),
        "log":     final.get("log", []),
        "ok":      True,
    }
    
if __name__ == "__main__":
    # print(app.get_graph().draw_ascii())
    questions = [
        "환불은 며칠 이내인가요?",
        "반품하고 싶은데 언제까지?"
    ]

    for q in questions:
            s = {"question": q, "query": q}         
            s.update(retriever_node(s))          # 검색
            r = generator_node(s)                # 생성
            
            print(f"\n{'='*55}")
            print(f"Q: {q}")
            print(f"근거 {len(s['documents'])}건")
            print(f"A: {r['answer'][:110]}")
            print(f"   부족신고={r['insufficient']} "
                  f"인용정상={r['has_citation']}")         
            print(f"   {r['log'][0]}")