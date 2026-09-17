from typing import TypedDict, Annotated, List
import operator


from typing import TypedDict, Annotated, List
import operator


class RAGState(TypedDict):

    # ===============================================
    # 기본 질문
    # ===============================================

    question: str
    query: str


    # ===============================================
    # 29차시 - 질문 분류
    # ===============================================

    intent: str


    # ===============================================
    # Retriever
    # ===============================================

    documents: list
    scores: list

    retrieval_ok: bool
    fail_reason: str


    # ===============================================
    # Generator
    # ===============================================

    answer: str

    insufficient: bool
    has_citation: bool
    gen_error: str


    # ===============================================
    # Verifier
    # ===============================================

    grade: str
    reason: str


    # ===============================================
    # 재생성
    # ===============================================

    retries: int


    # ===============================================
    # 30차시 - Rewrite
    # ===============================================

    rewrites: int

    # 새로운 검색 질의를 계속 누적
    tried_queries: Annotated[
        List[str],
        operator.add
    ]


    # ===============================================
    # 전체 실행 로그
    # ===============================================

    log: Annotated[
        List[str],
        operator.add
    ]


# 2. 초기 State 생성
def make_initial_state(question: str) -> dict:

    return {

        # 기본 질문
        "question": question,
        "query": question,

        # 29차시 - 분류
        "intent": "",

        # Retriever
        "documents": [],
        "scores": [],
        "retrieval_ok": False,
        "fail_reason": "",

        # Generator
        "answer": "",
        "insufficient": False,
        "has_citation": False,
        "gen_error": "",

        # Verifier
        "grade": "",
        "reason": "",

        # 재생성
        "retries": 0,

        # 30차시 - Rewrite
        "rewrites": 0,

        # 원본 질문도 첫 번째 검색 질의이므로 기록
        "tried_queries": [question],

        # 실행 로그
        "log": [],
    }

