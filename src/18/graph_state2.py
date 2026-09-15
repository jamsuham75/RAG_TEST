from typing import TypedDict, Annotated, List
import operator


# 1. State 스키마
class RAGState(TypedDict):
    question: str
    query: str
    documents: list
    scores: list
    answer: str
    grade: str
    reason: str
    retries: int
    log: Annotated[List[str], operator.add]
    tried_queries: List[str]


# 2. 초기 State 생성
def make_initial_state(question: str) -> dict:
    return {
        "question": question,
        "query": question,       # 처음에는 원본 질문과 동일
        "retries": 0,
        "log": [],
        "tried_queries": [],
    }

