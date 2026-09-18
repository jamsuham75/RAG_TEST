import json
from collections import Counter


with open("logs/queries.jsonl", encoding="utf-8") as f:
    rows = [
        json.loads(line)
        for line in f
        if line.strip()
    ]


if not rows:
    print("로그가 없습니다.")
    raise SystemExit


print("총 질문:", len(rows))

print(
    "검증 통과율:",
    f"{sum(r['verified'] for r in rows) / len(rows) * 100:.0f}%"
)

print(
    "유형 분포:",
    Counter(r["intent"] for r in rows)
)


rewrite_count = 0
error_count = 0
fallback_kinds = []


for r in rows:
    if r["rewrites"] > 0:
        rewrite_count += 1

    if r["node_error"]:
        error_count += 1

    if r["fallback_kind"]:
        fallback_kinds.append(r["fallback_kind"])


print(
    "재작성 발생률:",
    f"{rewrite_count / len(rows) * 100:.0f}%"
)

print(
    "평균 응답:",
    f"{sum(r['elapsed'] for r in rows) / len(rows):.1f}초"
)

print(
    "오류 발생:",
    error_count
)

print(
    "실패 사유:",
    Counter(fallback_kinds)
)