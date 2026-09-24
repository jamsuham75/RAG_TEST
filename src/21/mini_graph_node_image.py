from typing import TypedDict
from langgraph.graph import StateGraph, START, END


# ==========================================
# 1. State
# ==========================================

class MiniState(TypedDict):
    question: str
    documents: list[str]
    answer: str
    grade: str
    retries: int


def init(question):
    return {
        "question": question,
        "documents": [],
        "answer": "",
        "grade": "",
        "retries": 0
    }


# ==========================================
# 2. 노드
# ==========================================

def retrieve(state):

    if "없는" in state["question"]:
        docs = []
    else:
        docs = ["조각A", "조각B", "조각C"]

    print(f"→ 검색: {len(docs)}건")

    return {"documents": docs}


def generate(state):

    if state["retries"] == 0:
        quality = "부실한"
    else:
        quality = "좋은"

    answer = f"{len(state['documents'])}건 근거로 만든 {quality} 답변"

    print(f"→ 생성: {answer}")

    return {"answer": answer}


def verify(state):

    if "좋은" in state["answer"]:
        print("→ 검증: 통과")
        return {"grade": "pass"}

    print("→ 검증: 실패")
    return {"grade": "retry"}


def bump(state):

    count = state["retries"] + 1

    print(f"→ 재시도: {count}회")

    return {"retries": count}


def fallback(state):

    print("→ fallback")

    return {
        "answer": "자료를 찾지 못했습니다.",
        "grade": "giveup"
    }


# ==========================================
# 3. 분기 함수
# ==========================================

MAX_RETRY = 2


def route_retrieve(state):

    if state["documents"]:
        return "ok"

    return "empty"


def route_verify(state):

    if state["grade"] == "pass":
        return "done"

    if state["retries"] >= MAX_RETRY:
        return "giveup"

    return "retry"


# ==========================================
# 4. 그래프 만들기
# ==========================================

g = StateGraph(MiniState)

g.add_node("retrieve", retrieve)
g.add_node("generate", generate)
g.add_node("verify", verify)
g.add_node("bump", bump)
g.add_node("fallback", fallback)


# 시작 → 검색
g.add_edge(START, "retrieve")


# 검색 결과에 따라 분기
g.add_conditional_edges(
    "retrieve",
    route_retrieve,
    {
        "ok": "generate",
        "empty": "fallback"
    }
)


# 생성 → 검증
g.add_edge("generate", "verify")


# 검증 결과에 따라 분기
g.add_conditional_edges(
    "verify",
    route_verify,
    {
        "done": END,
        "retry": "bump",
        "giveup": "fallback"
    }
)


# 재시도 → 다시 생성
g.add_edge("bump", "generate")


# fallback → 종료
g.add_edge("fallback", END)


# 그래프 완성
app = g.compile()


# ==========================================
# 5. 실행
# ==========================================

print("■ 그래프 실행")

for step in app.stream(init("환불 규정은?")):
    print(step)


# ==========================================
# 6. 그래프 이미지 저장
# ==========================================

png = app.get_graph().draw_mermaid_png()

with open("graph_structure.png", "wb") as f:
    f.write(png)

print("graph_structure.png 저장 완료")