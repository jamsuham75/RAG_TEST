import os
import sys
import warnings

from dotenv import load_dotenv

# G:\RAG_TEST\src 를 Python 경로에 추가
SRC_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

sys.path.insert(0, SRC_DIR)

warnings.filterwarnings("ignore")

import config

from rag_app.indexer import get_store

load_dotenv()

_store = get_store()          # 모듈 로드 시 한 번만

def _search(query, k, search_type):
    # 검색 방식에 따라 다른 API를 호출한다
    if search_type == "mmr":
        docs = _store.max_marginal_relevance_search(
            query, k=k, fetch_k=k * 4, lambda_mult=0.5)
        return [(d, None) for d in docs]        # MMR은 점수 미제공     
    return _store.similarity_search_with_relevance_scores(query, k=k) 

def retriever_node(state) -> dict:
    retries = state.get("retries", 0)

    query = state.get("query") or state.get("question", "")

    # 재시도할수록 검색 문서 수를 증가시킴
    k = state.get("top_k") or (
        config.TOP_K + retries * 3
    )

    stype = state.get("search_type") or config.SEARCH_TYPE

    # 재시도할수록 점수 기준을 조금 완화
    floor = state.get("min_score")

    if floor is None:
        floor = max(
            0.30,
            config.MIN_SCORE - retries * 0.05
        )
    
    if not query.strip():
        return {"documents": [], "scores": [], "retrieval_ok": False,                 
                "fail_reason": "empty_query",
                "log": ["검색: 질의가 비어 있음"]}
    try:
        pairs = _search(query, k, stype)
    except Exception as e:
        return {"documents": [], "scores": [], "retrieval_ok": False,                 
                "fail_reason": "search_error",
                "log": [f"검색 오류: {type(e).__name__}"]}
    if not pairs:
        return {"documents": [], "scores": [], "retrieval_ok": False,                 
                "fail_reason": "no_result",
                "log": ["검색: 결과 0건"]}
        
    scores = [round(s, 3) if s is not None else None for _, s in pairs]     # 점수가 있는 경우에만 임계값 필터 적용
    
    if scores[0] is not None:
        kept = []
        for d, s in pairs:
            if s >= floor:                 
                kept.append(d)
        reason = "" if kept else "low_score"    
    else:
        kept, reason = [d for d, _ in pairs], ""
    return {
        "documents":    kept,
        "scores":       scores,
        "retrieval_ok": len(kept) > 0,
        "fail_reason":  reason,
        "log": [f"검색({stype},k={k}): {len(kept)}/{len(pairs)}건 "                 
                f"통과 최고={scores[0]}"],
    }
    
if __name__ == "__main__":
    CASES = [
        {"query": "환불은 며칠 이내인가요?"},          # 정상
        {"query": "반품하고 싶은데 언제까지?"},        # 표현 차이
        {"query": "대표이사가 누구인가요?"},           # 없는 내용
        {"query": ""},                                # 빈 질의
        {"query": "환불 규정", "top_k": 10},          # k 확대
        {"query": "환불과 교환 차이", "search_type": "mmr"},
    ]
    
    for c in CASES:
        r = retriever_node(c)
        print(f"\nQ: {c['query'] or '(빈 질의)'}")         
        print(f"   통과 {len(r['documents'])}건 | "
              f"ok={r['retrieval_ok']} | "
              f"사유={r['fail_reason'] or '-'}")
        print(f"   점수: {r['scores'][:5]}")