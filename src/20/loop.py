from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class S(TypedDict):
    count: int
    
def step(state):
    n = state["count"] + 1
    print(f"  실행 {n}회차")
    return {"count": n}

g = StateGraph(S)
g.add_node("step", step)
g.add_edge(START, "step")
g.add_edge("step", "step")        # ★ 자기 자신으로! 무한루프 
app = g.compile()

# ⚠ recursion_limit로 안전장치를 걸고 실행
try:
    app.invoke({"count": 0}, {"recursion_limit": 10}) 
except Exception as e:
    print("중단됨:", type(e).__name__)