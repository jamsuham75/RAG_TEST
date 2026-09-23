import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

sys.path.insert(0, SRC_DIR)

from graph29 import app
from graph_state2 import make_initial_state


# ===================================================
# 테스트 질문
# ===================================================

CASES = [
    ("안녕하세요", "greeting"),
    ("고맙습니다", "greeting"),
    ("125 + 340 * 2", "calc"),
    ("오늘 날씨 어때요?", "scope"),
    ("환불은 며칠 이내인가요?", "document"),
    ("휴가 신청은 어떻게 하나요?", "document"),
]


# ===================================================
# 테스트 실행
# ===================================================

for question, expected in CASES:

    # 그래프 실행
    result = app.invoke(
        make_initial_state(question),
        {"recursion_limit": 25}
    )

    # 실제 분류 결과
    actual = result.get("intent", "")

    # 예상값과 실제값 비교
    if actual == expected:
        mark = "✓"
    else:
        mark = "✗"

    # 결과 출력
    print()
    print(f"{mark} 질문: {question}")
    print(f"   실제 분류: {actual}")
    print(f"   예상 분류: {expected}")
    print(f"   답변: {result.get('answer', '')[:60]}")