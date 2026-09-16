import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '18'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '19'))

from langgraph.graph import StateGraph, START, END 
from graph_state import RAGState
from retrieve import retrieve_node 
from generate import generate_node 
from fallback import fallback_node 
from routes import route_after_retrieve 

g = StateGraph(RAGState)

# ── 노드 등록 ──
g.add_node("retrieve", retrieve_node) 
g.add_node("generate", generate_node) 
g.add_node("fallback", fallback_node)

# ── Edge 연결 ──
g.add_edge(START, "retrieve")

g.add_conditional_edges(     
    "retrieve",    
    route_after_retrieve,
    {"ok": "generate", "empty": "fallback"}, 
)

g.add_edge("generate", END) 
g.add_edge("fallback", END) 

app = g.compile()

print(app.get_graph().draw_ascii())

png = app.get_graph().draw_mermaid_png() 
with open("graph.png", "wb") as f:     
    f.write(png)
print("graph.png 저장 완료")