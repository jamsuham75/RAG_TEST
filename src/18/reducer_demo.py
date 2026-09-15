from typing import TypedDict, Annotated, List
import operator

from langgraph.graph import StateGraph, START, END


# ─────────────────────────────
# 실험 A: Reducer 없음
# 같은 키가 들어오면 덮어쓰기
# ─────────────────────────────
class StateA(TypedDict):
    log: List[str]


# ─────────────────────────────
# 실험 B: Reducer 있음
# 같은 키가 들어오면 리스트 이어 붙이기
# ─────────────────────────────
class StateB(TypedDict):
    log: Annotated[List[str], operator.add]


# ─────────────────────────────
# 노드
# ─────────────────────────────
def step1(state):
    return {"log": ["1단계 완료"]}


def step2(state):
    return {"log": ["2단계 완료"]}


def step3(state):
    return {"log": ["3단계 완료"]}


# ─────────────────────────────
# 그래프 실행 함수
# ─────────────────────────────
def run(StateCls, label):
    g = StateGraph(StateCls)

    g.add_node("s1", step1)
    g.add_node("s2", step2)
    g.add_node("s3", step3)

    g.add_edge(START, "s1")
    g.add_edge("s1", "s2")
    g.add_edge("s2", "s3")
    g.add_edge("s3", END)

    app = g.compile()

    result = app.invoke({"log": []})

    print(f"{label}: {result['log']}")


# ─────────────────────────────
# 비교 실행
# ─────────────────────────────
run(StateA, "Reducer 없음")
run(StateB, "Reducer 있음")