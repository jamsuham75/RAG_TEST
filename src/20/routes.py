def route_after_retrieve(state: dict) -> str:
    # 검색 결과가 있으면 생성, 없으면 안내
    return "ok" if state.get("retrieval_ok") else "empty"