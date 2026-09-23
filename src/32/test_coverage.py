# ===================================================
# test_coverage.py
# 32차시 - 경로 커버리지 테스트
# ===================================================

from collections import Counter

from graph32 import app
from graph_state2 import make_initial_state


# 테스트 질문
CASES = [
    ("안녕하세요", "greeting 경로"),
    ("120 * 3 + 45", "calc 경로"),
    ("오늘 날씨 어때요?", "scope 경로"),
    ("환불은 며칠 이내인가요?", "정상 RAG 경로"),
    ("반품하고 싶은데 언제까지?", "재검색 경로"),
    ("환불 방법과 수수료는?", "재생성 경로"),
    ("대표이사가 누구인가요?", "fallback 경로"),
]


# 전체 노드 목록
ALL_NODES = [
    "classify",
    "greeting",
    "calc",
    "scope",
    "retrieve",
    "generate",
    "verify",
    "bump",
    "rewrite",
    "fallback",
]


# 노드별 방문 횟수
visited = Counter()


# ===================================================
# 테스트 실행
# ===================================================

for question, description in CASES:

    state = make_initial_state(question)
    nodes = []

    # 그래프를 한 단계씩 실행
    for step in app.stream(
        state,
        {"recursion_limit": 40}
    ):

        for node_name in step.keys():

            nodes.append(node_name)
            visited[node_name] += 1


    print(f"\n[{description}]")
    print(f"Q: {question}")
    print(f"경로: {' -> '.join(nodes)}")


# ===================================================
# 결과 출력
# ===================================================

print("\n" + "=" * 50)
print("노드별 방문 횟수")
print("=" * 50)


for node_name in ALL_NODES:

    count = visited[node_name]

    if count > 0:
        mark = "✓"
    else:
        mark = "✗ 미방문"

    print(f"{node_name:<10} {count:>3}회  {mark}")


# 미방문 노드 찾기
missing = [
    node
    for node in ALL_NODES
    if visited[node] == 0
]


print("=" * 50)

if not missing:
    print("✓ 모든 노드를 최소 1회 이상 방문했습니다.")
else:
    print("✗ 미방문 노드:", ", ".join(missing))