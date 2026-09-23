def safe_node(fn, state):
    try:
        # 노드 실행
        result = fn(state)

        return result

    except Exception as e:
        # 오류가 나면 그래프가 죽지 않고 오류 정보 반환
        print("[ERROR]", e)

        return {
            "node_error": str(e),
            "log": ["노드 실행 중 오류 발생"]
        }