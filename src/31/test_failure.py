from unittest.mock import patch
import graph31


# 일부러 에러가 나는 함수
def broken_node(state):
    raise RuntimeError("일부러 발생시킨 오류")


with patch("graph31.retriever_node", broken_node):

    result = graph31.ask(
        "환불은 며칠 이내인가요?"
    )

    print("시스템 생존")
    print("오류:", result["node_error"])