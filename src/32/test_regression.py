# ===================================================
# test_regression.py
# 32차시 - 전체 회귀 테스트
# ===================================================

from graph32 import ask


# 테스트 질문
TESTS = [
    {
        "q": "환불은 며칠 이내인가요?",
        "keys": ["7일"],
    },
    {
        "q": "교환 기간은 얼마인가요?",
        "keys": ["14일"],
    },
    {
        "q": "고객센터 운영 시간은?",
        "keys": ["09:00", "18:00", "9시", "18시"],
    },
    {
        "q": "반품하고 싶은데 언제까지?",
        "keys": ["7일"],
    },
    {
        "q": "물건 바꾸려면 택배비 누가?",
        "keys": ["배송비", "택배비", "고객"],
    },
    {
        "q": "환불 방법과 수수료는?",
        "keys": ["환불", "수수료"],
    },
    {
        "q": "대표이사가 누구인가요?",
        "keys": [
            "관련 자료를 찾지 못했습니다",
            "확인할 수 없습니다",
            "정보가 없습니다",
        ],
    },
]


# 답변에 키워드가 하나라도 있는지 확인
def check_answer(answer, keys):

    for key in keys:
        if key in answer:
            return True

    return False


# ===================================================
# 테스트 실행
# ===================================================

correct = 0
pass_count = 0
retry_count = 0
rewrite_count = 0
# total_time = 0


for test in TESTS:

    question = test["q"]
    keys = test["keys"]

    # RAG 실행
    result = ask(question)

    answer = result.get("answer", "")

    # 정답 확인
    ok = check_answer(answer, keys)

    if ok:
        correct += 1
        mark = "✓"
    else:
        mark = "✗"

    # 통계
    if result.get("grade") == "pass":
        pass_count += 1

    if result.get("retries", 0) > 0:
        retry_count += 1

    if result.get("rewrites", 0) > 0:
        rewrite_count += 1

    # total_time += result.get("elapsed", 0)

    # 질문별 결과
    print(
        f"{mark} {question} | "
        f"판정={result.get('grade')} | "
        f"재생성={result.get('retries', 0)} | "
        f"재검색={result.get('rewrites', 0)}"
    )


# ===================================================
# 전체 결과
# ===================================================

count = len(TESTS)

print("\n" + "=" * 50)
print(f"정답률   : {correct}/{count} ({correct / count * 100:.0f}%)")
print(f"검증통과 : {pass_count}/{count}")
print(f"재생성   : {retry_count}건")
print(f"재검색   : {rewrite_count}건")
# print(f"평균시간 : {total_time / count:.1f}초")
print("=" * 50)