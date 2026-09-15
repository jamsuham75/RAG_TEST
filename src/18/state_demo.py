from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END

class DemoState(TypedDict):
    question: str
    documents: List[str]
    answer: str

def retrieve(state: DemoState):
    print("[retrieve] 받은 State:", state)
    return {"documents": ["조각A", "조각B"]}

def generate(state: DemoState):
    print("[generate] 받은 State:", state)     
    n = len(state["documents"])
    return {"answer": f"{n}건의 근거로 만든 답변"}

g = StateGraph(DemoState)
g.add_node("retrieve", retrieve)
g.add_node("generate", generate)
g.add_edge(START, "retrieve")
g.add_edge("retrieve", "generate")
g.add_edge("generate", END)

app = g.compile()
final = app.invoke({"question": "환불 규정은?"}) 
print("\n[최종] State:", final)