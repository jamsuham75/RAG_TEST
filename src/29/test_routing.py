import os
import sys
import warnings

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
warnings.filterwarnings("ignore")

sys.path.insert(0, SRC_DIR)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '25'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '13'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '24'))

import json, re
import config

from graph29 import app
from graph_state2 import make_initial_state

import time


CASES = [
    ("안녕하세요", "greeting"),
    ("고맙습니다", "greeting"),
    ("125 + 340 * 2", "calc"),
    ("오늘 날씨 어때요?", "scope"),
    ("환불은 며칠 이내인가요?", "document"),
    ("휴가 신청은 어떻게 하나요?", "document"),
]


for q, expected in CASES:
    t0 = time.time()

    nodes = []
    final = None

    # stream으로 실행하면서 경로와 최종 상태를 함께 확인
    for step in app.stream(
        make_initial_state(q),
        {
            "recursion_limit": 25,
        },
    ):
        nodes.extend(step.keys())

        # 각 단계의 상태를 합쳐 최종 상태 구성
        if isinstance(step, dict):
            for node_state in step.values():
                if isinstance(node_state, dict):
                    if final is None:
                        final = {}

                    final.update(node_state)

    sec = time.time() - t0

    if final is None:
        final = {}

    actual = final.get("intent", "")
    mark = "✓" if actual == expected else "✗"

    print(f"\n{mark} Q: {q}")
    print(f"   유형: {actual} (기대: {expected})")
    print(f"   경로: {' -> '.join(nodes)}")
    print(f"   시간: {sec:.2f}초")
    print(f"   A: {final.get('answer', '')[:60]}")