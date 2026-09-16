import config
from indexer import get_store

_store = get_store()          # 모듈 로드 시 한 번만

def _search(query, k, search_type):
    # 검색 방식에 따라 다른 API를 호출한다
    if search_type == "mmr":
        docs = _store.max_marginal_relevance_search(
            query, k=k, fetch_k=k * 4, lambda_mult=0.5)
        return [(d, None) for d in docs]        # MMR은 점수 미제공     
    return _store.similarity_search_with_relevance_scores(query, k=k) 

def retriever_node(state) -> dict:
    query = state.get("query") or state.get("question", "")
    k     = state.get("top_k") or config.TOP_K
    stype = state.get("search_type") or config.SEARCH_TYPE
    floor = state.get("min_score")
    
    if floor is None:
        floor = config.MIN_SCORE
    
    if not query.strip():
        return {"documents": [], "scores": [], "retrieval_ok": False,                 "fail_reason": "empty_query",
                "log": ["검색: 질의가 비어 있음"]}
    try:
        pairs = _search(query, k, stype)
    except Exception as e:
        return {"documents": [], "scores": [], "retrieval_ok": False,                 "fail_reason": "search_error",
                "log": [f"검색 오류: {type(e).__name__}"]}
    if not pairs:
        return {"documents": [], "scores": [], "retrieval_ok": False,                 "fail_reason": "no_result",
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
        "log": [f"검색({stype},k={k}): {len(kept)}/{len(pairs)}건 "                 f"통과 최고={scores[0]}"],
    }