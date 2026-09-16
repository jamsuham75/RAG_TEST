import config

def fallback_node(state: dict) -> dict:
    # 근거를 찾지 못했을 때 안내 메시지를 만든다
    tried = state.get("tried_queries", [])
    msg = config.MSG_NO_DOC
    if tried:
        msg += f"\n(시도한 검색어: {', '.join(tried)})"
    msg += "\n질문을 조금 더 구체적으로 바꿔 다시 물어봐 주세요."
    return {
        "answer": msg,
        "grade":  "giveup",
        "log":    ["[fallback] 안내 메시지 반환"],
    }
if __name__ == "__main__":
    print(fallback_node({"question": "대표이사 이름은?"})["answer"])