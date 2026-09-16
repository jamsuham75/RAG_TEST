import config
import os
import sys
import warnings
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '10'))
from indexer import get_store

_store = get_store()

def retrieve_node(state: dict) -> dict:
    # 검색만 담당한다. 판단은 하지 않는다.
    query = state.get("query") or state["question"]
    k     = state.get("top_k", config.TOP_K)
    pairs = _store.similarity_search_with_relevance_scores(
        query, k=k)
    # 기준(MIN_SCORE)을 넘는 것만 골라 담기
    docs = []
    for d, s in pairs:
        if s >= config.MIN_SCORE:
            docs.append(d)
    scores = [round(s, 3) for _, s in pairs]
    return {
        "documents":    docs,
        "scores":       scores,
        "retrieval_ok": len(docs) > 0,
        "log":          [f"[retrieve] '{query}' → "                          f"{len(docs)}/{len(pairs)}건 통과"],     }
# ── 단독 테스트 ──
if __name__ == "__main__":
    r = retrieve_node({"question": "환불은 며칠 이내인가요?"})     
    print("통과 문서:", len(r["documents"]))
    print("점수      :", r["scores"])
    print("검색 성공 :", r["retrieval_ok"])     
    print("로그      :", r["log"][0])