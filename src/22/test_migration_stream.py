import warnings

from graph import app
from graph_state2 import make_initial_state
warnings.filterwarnings("ignore")

QUESTIONS = [
    "환불은 며칠 이내인가요?",
    "대표이사가 누구인가요?",
]


for q in QUESTIONS:
    print("\n" + "=" * 55)
    print(f"Q: {q}")
    print("=" * 55)

    for step in app.stream(make_initial_state(q)):
        for node, update in step.items():
            print(f"  [{node}] {list(update.keys())}")

            if node == "retrieve":
                print("    검색 점수:", update.get("scores"))
                print(
                    "    검색 성공 여부:",
                    update.get("retrieval_ok")
                )