import os
import sys

# 필요한 폴더 등록
BASE = os.path.dirname(__file__)

for folder in ["18", "22", "24", "25", "26"]:
    sys.path.insert(0, os.path.join(BASE, "..", folder))

import graph22
import graph27


# ===================================================
# 테스트 질문
# ===================================================

TESTS = [
    {"q": "환불은 며칠 이내에 신청해야 하나요?", "keys": ["7일"]},
    {"q": "환불 방법을 알려주세요.", "keys": ["환불"]},
    {"q": "반품은 언제까지 가능한가요?", "keys": ["7일", "반품"]},
    {"q": "상품을 교환할 수 있나요?", "keys": ["교환"]},
    {"q": "배송은 며칠 걸리나요?", "keys": ["배송", "일"]},
    {"q": "배송비는 얼마인가요?", "keys": ["배송비", "무료"]},
    {"q": "주문을 취소하고 싶습니다.", "keys": ["취소"]},
    {"q": "결제 방법에는 무엇이 있나요?", "keys": ["결제", "카드"]},
    {"q": "고객센터 운영시간은 언제인가요?", "keys": ["운영시간", "고객센터"]},
    {"q": "회원가입은 어떻게 하나요?", "keys": ["회원가입"]},
    {"q": "적립금은 어떻게 사용하나요?", "keys": ["적립금"]},
    {"q": "쿠폰을 사용할 수 있나요?", "keys": ["쿠폰"]},

    # 문서에 없는 질문
    {"q": "대표이사는 누구인가요?", "no_answer": True},
    {"q": "회사 창립일은 언제인가요?", "no_answer": True},
]


# ===================================================
# "답을 찾지 못했다"는 답변인지 확인
# ===================================================

def is_no_answer(answer):
    words = [
        "확인할 수 없",
        "찾지 못",
        "관련 자료가 없",
        "알 수 없",
    ]

    for word in words:
        if word in answer:
            return True

    return False


# ===================================================
# 테스트
# ===================================================

def evaluate(graph, name):

    hit = 0
    halluc = 0

    for test in TESTS:

        result = graph.ask(test["q"])
        answer = result.get("answer", "")

        # -------------------------------------------
        # 문서에 없는 질문
        # -------------------------------------------
        if test.get("no_answer", False):

            ok = is_no_answer(answer)

            # 없는 내용을 만들어 답했다면 환각 의심
            if not ok:
                halluc += 1

        # -------------------------------------------
        # 문서에 있는 질문
        # -------------------------------------------
        else:

            ok = False

            # "모르겠다"는 답변이 아니라면
            if not is_no_answer(answer):

                # 정답 키워드가 하나라도 있는지 검사
                for key in test["keys"]:
                    if key in answer:
                        ok = True
                        break

        if ok:
            hit += 1

        print()
        print("Q:", test["q"])
        print("A:", answer[:100])
        print("판정:", result.get("grade", ""))
        print("재시도:", result.get("retries", 0))
        print("적중:", ok)

    # 결과
    total = len(TESTS)
    accuracy = hit / total * 100

    print()
    print("==============================")
    print(f"[{name}]")
    print(f"정답: {hit}/{total} ({accuracy:.0f}%)")
    print(f"환각 의심: {halluc}건")
    print("==============================")


# ===================================================
# 실행
# ===================================================

if __name__ == "__main__":

    evaluate(graph22, "22차시")
    evaluate(graph27, "27차시")