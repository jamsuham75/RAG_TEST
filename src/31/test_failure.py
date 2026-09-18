import os
import sys
from unittest.mock import patch


# ===================================================
# 경로 설정
# ===================================================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

sys.path.insert(0, CURRENT_DIR)
sys.path.insert(0, SRC_DIR)
sys.path.insert(0, os.path.join(SRC_DIR, "24"))
sys.path.insert(0, os.path.join(SRC_DIR, "25"))
sys.path.insert(0, os.path.join(SRC_DIR, "26"))


# ===================================================
# 31차시 그래프
# ===================================================

from graph31 import ask


# ===================================================
# 장애 테스트 함수
# ===================================================

def test_case(name, target, exception):

    print(f"\n{'=' * 55}")
    print(f"[{name}]")
    print("=" * 55)

    with patch(target, side_effect=exception):

        try:

            r = ask("환불은 며칠 이내인가요?")

            print("✓ 시스템 생존")
            print(f"  답변: {r.get('answer', '')[:70]}")
            print(f"  검증: {r.get('verified')}")
            print(f"  grade: {r.get('grade')}")
            print(f"  오류: {r.get('node_error', '')}")

        except Exception as e:

            print(
                f"✗ 시스템 중단! "
                f"{type(e).__name__}: {e}"
            )


# ===================================================
# 1. 검색 노드 장애
# ===================================================

test_case(
    "검색 노드 오류",
    "retriever.retriever_node",
    RuntimeError("index corrupted")
)


# ===================================================
# 2. 생성 노드 장애
# ===================================================

test_case(
    "LLM 생성 오류",
    "generator.generator_node",
    TimeoutError("request timeout")
)


# ===================================================
# 3. 검증 노드 장애
# ===================================================

test_case(
    "검증 노드 오류",
    "verifier.verifier_node",
    ValueError("invalid response")
)