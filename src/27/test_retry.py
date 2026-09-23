import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "18"))

from graph27 import app
from graph_state2 import make_initial_state


question = "환불 방법과 대표이사를 알려주세요"


for step in app.stream(
    make_initial_state(question),
    {"recursion_limit": 25}
):

    for node, result in step.items():

        print(f"\n[{node}]")

        # 해당 노드의 실행 기록 출력
        for log in result.get("log", []):
            print(log)