from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, START, END 
import operator

class MiniState(TypedDict):
    question: str
    documents: List[str]
    answer: str
    grade: str
    retries: int
    log: Annotated[List[str], operator.add]

def init(q: str) -> MiniState:
    return {"question": q, "documents": [], "answer": "",
            "grade": "", "retries": 0, "log": []}