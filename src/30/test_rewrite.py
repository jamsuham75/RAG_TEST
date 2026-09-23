# ===================================================
# 30차시 - Rewrite 테스트
# ===================================================

import os
import sys

# 현재 폴더: src/30
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 상위 src 폴더
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

# 모듈 경로
sys.path.insert(0, CURRENT_DIR)
sys.path.insert(0, SRC_DIR)

for folder in ["18", "19", "24", "25", "26", "29"]:
    sys.path.append(
        os.path.join(SRC_DIR, folder)
    )


# ===================================================
# 그래프 가져오기
# ===================================================

from graph30 import app
from graph_state2 import make_initial_state


# ===================================================
# 테스트 질문
# ===================================================

QUESTIONS = [
    "반품하고 싶은데 언제까지 가능해요?",
    "물건 바꾸려면 택배비 누가 내나요?",
    "돈 돌려받으려면 어떻게 해요?",
]


# ===================================================
# 테스트 실행
# ===================================================

for question in QUESTIONS:

    print("\n" + "=" * 60)
    print("Q:", question)
    print("=" * 60)

    # 처음 상태 생성
    state = make_initial_state(question)

    # 그래프 실행
    result = app.invoke(
        state,
        {"recursion_limit": 30}
    )

    # 결과 출력
    print("A:", result.get("answer", ""))

    print(
        "재작성:",
        result.get("rewrites", 0),
        "회"
    )

    print(
        "최종 검색어:",
        result.get("query", "")
    )

    print(
        "시도한 검색어:",
        result.get("tried_queries", [])
    )

    print(
        "최종 판정:",
        result.get("grade", "")
    )