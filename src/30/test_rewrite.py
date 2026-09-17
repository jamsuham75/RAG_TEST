# ============================================================
# 30차시 - Rewrite 회귀 테스트
# ============================================================
# 과거에 검색에 실패했던 질문들이
# 질의 재작성(Rewrite) 후 해결되는지 확인한다.
# ============================================================

import os
import sys
import warnings


# ------------------------------------------------------------
# 1. 경로 설정
# ------------------------------------------------------------

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

warnings.filterwarnings("ignore")

# src
sys.path.insert(0, SRC_DIR)

# 현재 30차시를 가장 먼저 찾도록 설정
sys.path.insert(0, CURRENT_DIR)

# 이전 차시 모듈
sys.path.append(os.path.join(SRC_DIR, "18"))
sys.path.append(os.path.join(SRC_DIR, "19"))
sys.path.append(os.path.join(SRC_DIR, "24"))
sys.path.append(os.path.join(SRC_DIR, "25"))
sys.path.append(os.path.join(SRC_DIR, "26"))
sys.path.append(os.path.join(SRC_DIR, "29"))


# ------------------------------------------------------------
# 2. 30차시 그래프 가져오기
# ------------------------------------------------------------

from graph30 import app
from graph_state2 import make_initial_state


# ------------------------------------------------------------
# 3. 이전 차시에서 실패했던 질문
# ------------------------------------------------------------

FAILED_BEFORE = [
    "반품하고 싶은데 언제까지 가능해요?",
    "물건 바꾸려면 택배비 누가 내나요?",
    "돈 돌려받으려면 어떻게 해요?",
]


# ------------------------------------------------------------
# 4. Rewrite 테스트
# ------------------------------------------------------------

for q in FAILED_BEFORE:

    print(f"\n{'=' * 58}")
    print(f"Q: {q}")
    print("=" * 58)

    initial_state = make_initial_state(q)

    # --------------------------------------------------------
    # 노드별 실행 과정 확인
    # --------------------------------------------------------

    for step in app.stream(
        initial_state,
        {"recursion_limit": 30}
    ):

        for node, update in step.items():

            for line in update.get("log", []):
                print(f"   {line}")


    # --------------------------------------------------------
    # 최종 결과 확인
    # --------------------------------------------------------
    # stream()에서 사용했던 State와 별개로
    # 테스트 결과를 얻기 위해 처음부터 다시 실행한다.
    # --------------------------------------------------------

    final = app.invoke(
        make_initial_state(q),
        {"recursion_limit": 30}
    )

    print(f"\n   A: {final.get('answer', '')[:90]}")

    print(
        f"   재작성 {final.get('rewrites', 0)}회 | "
        f"판정 {final.get('grade', '')}"
    )

    print(
        f"   최종 검색어: "
        f"{final.get('query', '')}"
    )

    print(
        f"   시도한 검색어: "
        f"{final.get('tried_queries', [])}"
    )