from typing import TypedDict
from langgraph.graph import StateGraph, START, END


# =========================================
# 1. State
# =========================================

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


# =========================================
# 2. 노드
# =========================================

def retrieve(state):
    # "없는"이 들어가면 검색 실패로 가정
    if "없는" in state["question"]:
        docs = []
    else:
        docs = ["조각A", "조각B", "조각C"]

    print(f"검색: {len(docs)}건")

    return {"documents": docs}


def generate(state):
    # 처음에는 부실한 답변,
    # 재시도하면 좋은 답변으로 가정
    if state["retries"] == 0:
        quality = "부실한"
    else:
        quality = "좋은"

    answer = f"{len(state['documents'])}건 근거로 만든 {quality} 답변"

    print(f"생성: {answer}")

    return {"answer": answer}


def verify(state):
    # 답변에 "좋은"이 있으면 통과
    if "좋은" in state["answer"]:
        print("검증: 통과")
        return {"grade": "pass"}

    print("검증: 실패")
    return {"grade": "retry"}


def bump(state):
    # 재시도 횟수 1 증가
    count = state["retries"] + 1

    print(f"재시도: {count}회")

    return {"retries": count}


def fallback(state):
    print("fallback")

    return {
        "answer": "자료를 찾지 못했습니다.",
        "grade": "giveup"
    }


# =========================================
# 3. 분기 함수
# =========================================

MAX_RETRY = 2


def after_retrieve(state):

    if state["documents"]:
        return "ok"

    return "empty"


def after_verify(state):

    # 검증 성공
    if state["grade"] == "pass":
        return "done"

    # 최대 재시도 횟수 도달
    if state["retries"] >= MAX_RETRY:
        return "giveup"

    # 다시 생성
    return "retry"


# =========================================
# 4. 그래프 만들기
# =========================================

g = StateGraph(MiniState)


# 노드 등록
g.add_node("retrieve", retrieve)
g.add_node("generate", generate)
g.add_node("verify", verify)
g.add_node("bump", bump)
g.add_node("fallback", fallback)


# START → retrieve
g.add_edge(START, "retrieve")


# retrieve 이후 분기
g.add_conditional_edges(
    "retrieve",
    after_retrieve,
    {
        "ok": "generate",
        "empty": "fallback"
    }
)


# generate → verify
g.add_edge("generate", "verify")


# verify 이후 분기
g.add_conditional_edges(
    "verify",
    after_verify,
    {
        "done": END,
        "retry": "bump",
        "giveup": "fallback"
    }
)


# 재시도
g.add_edge("bump", "generate")


# fallback 이후 종료
g.add_edge("fallback", END)


# 그래프 완성
app = g.compile()


# =========================================
# 5. 그래프 구조 확인
# =========================================

print(app.get_graph().draw_ascii())


# =========================================
# 6. 그래프 실행
# =========================================

result = app.invoke(init("환불 규정은?"))

print("\n최종 결과")
print(result)


# # =========================================
# # 7. 그래프 이미지 저장
# # =========================================

# png = app.get_graph().draw_mermaid_png()

# with open("graph_structure.png", "wb") as f:
#     f.write(png)

# print("\ngraph_structure.png 저장 완료")