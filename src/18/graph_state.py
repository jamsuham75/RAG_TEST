from typing import TypedDict, Annotated, List, Any 
import operator

class RAGState(TypedDict, total=False):
    # ── 입력 ──
    question: str            # 사용자 원본 질문 (변경 금지)     query: str               # 검색용 질문 (재작성 가능)
    # ── 검색 결과 ──
    documents: List[Any]     # 검색된 조각
    scores: List[float]      # 유사도 점수
    retrieval_ok: bool       # 검색 성공 여부
    # ── 생성 결과 ──
    answer: str              # 생성된 답변
    insufficient: bool       # 근거 부족 자가신고
    has_citation: bool       # 출처 번호 포함 여부
    # ── 검증 결과 ──
    grade: str               # "pass" | "retry"
    reason: str              # 판정 이유
    # ── 제어 ──
    retries: int             # 재시도 횟수
    top_k: int               # 검색 개수 (동적 조절용)
    # ── 이력 (누적) ──
    log: Annotated[List[str], operator.add]     
    tried_queries: Annotated[List[str], operator.add]