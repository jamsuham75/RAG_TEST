import os
import sys

# 18차시 상태 모듈
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "18"),
)

# 22차시 그래프 모듈
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "22"),
)

# 24차시 Retriever 모듈
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "24"),
)

# 25차시 Generator 모듈
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "25"),
)

# 26차시 Verifier 모듈
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "26"),
)


import graph22
import graph27


TESTS = [
    {
        "q": "환불은 며칠 이내에 신청해야 하나요?",
        "keys": ["7일"],
    },
    {
        "q": "환불 방법을 알려주세요.",
        "keys": ["환불"],
    },
    {
        "q": "반품은 언제까지 가능한가요?",
        "keys": ["7일", "반품"],
    },
    {
        "q": "상품을 교환할 수 있나요?",
        "keys": ["교환"],
    },
    {
        "q": "배송은 며칠 걸리나요?",
        "keys": ["배송", "일"],
    },
    {
        "q": "배송비는 얼마인가요?",
        "keys": ["배송비", "무료"],
    },
    {
        "q": "주문을 취소하고 싶습니다.",
        "keys": ["취소"],
    },
    {
        "q": "결제 방법에는 무엇이 있나요?",
        "keys": ["결제", "카드"],
    },
    {
        "q": "고객센터 운영시간은 언제인가요?",
        "keys": ["운영시간", "고객센터"],
    },
    {
        "q": "회원가입은 어떻게 하나요?",
        "keys": ["회원가입"],
    },
    {
        "q": "적립금은 어떻게 사용하나요?",
        "keys": ["적립금"],
    },
    {
        "q": "쿠폰을 사용할 수 있나요?",
        "keys": ["쿠폰"],
    },
    {
        "q": "대표이사는 누구인가요?",
        "keys": [],
        "no_answer": True,
    },
    {
        "q": "회사 창립일은 언제인가요?",
        "keys": [],
        "no_answer": True,
    },
]


def contains_any(answer: str, keywords: list[str]) -> bool:
    for keyword in keywords:
        if keyword in answer:
            return True

    return False


def looks_like_no_answer(answer: str) -> bool:
    no_answer_phrases = [
        "확인할 수 없",
        "찾지 못",
        "제공된 자료",
        "관련 자료가 없",
        "알 수 없",
    ]

    return any(
        phrase in answer
        for phrase in no_answer_phrases
    )


def evaluate(mod, name: str):
    hit = 0
    halluc = 0

    for test in TESTS:
        result = mod.ask(test["q"])
        answer = result.get("answer", "")

        is_hit = contains_any(
            answer,
            test.get("keys", []),
        )

        if is_hit:
            hit += 1

        if test.get("no_answer"):
            if not looks_like_no_answer(answer):
                halluc += 1
        
        print(
            f"\nQ: {test['q']}"
            f"\nA: {answer[:100]}"
            f"\n판정: {result.get('grade', '')}"
            f" / 재시도: {result.get('retries', 0)}"
            f" / 적중: {is_hit}"
        )

    total = len(TESTS)
    accuracy = hit / total * 100

    print(
        f"[{name}] "
        f"정답 {hit}/{total} "
        f"({accuracy:.0f}%) | "
        f"환각 의심 {halluc}건"
    )


if __name__ == "__main__":
    evaluate(graph22, "22차시")
    evaluate(graph27, "27차시")