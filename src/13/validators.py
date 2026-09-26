# ============================================================
# 프롬프트 비교 + 인용 검증 프로그램
# 같은 질문과 같은 검색 자료를 V1, V2, V3 프롬프트에 전달하여
# 답변 차이를 비교하고 [1], [2] 같은 인용 번호도 검사합니다.
# ============================================================

import os
import sys
import re

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser


# ------------------------------------------------------------
# 11차시 폴더의 retriever.py를 사용할 수 있도록 경로를 추가합니다.
# append()를 사용해 현재 폴더의 prompts.py를 먼저 찾도록 합니다.
# ------------------------------------------------------------

CURRENT_DIR = os.path.dirname(__file__)
RETRIEVER_DIR = os.path.join(CURRENT_DIR, "..", "11")

sys.path.append(RETRIEVER_DIR)


# ------------------------------------------------------------
# 검색 기능과 프롬프트를 가져옵니다.
# ------------------------------------------------------------

from retriever import search, build_context
from prompts import PROMPTS


# ------------------------------------------------------------
# .env 파일의 OPENAI_API_KEY를 불러옵니다.
# ------------------------------------------------------------

load_dotenv()


# ------------------------------------------------------------
# 답변을 생성할 LLM을 준비합니다.
# temperature=0은 답변의 임의성을 줄이기 위한 설정입니다.
# ------------------------------------------------------------

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


# ============================================================
# 인용 검사 함수
# 답변에 [1], [2] 같은 인용 번호가 있는지 확인하고,
# 실제 검색된 문서 범위 안의 번호인지 검사합니다.
# ============================================================

def check_citation(answer, document_count):

    # 답변에서 [숫자] 형태의 인용 번호를 모두 찾습니다.
    found_numbers = re.findall(r"\[(\d+)\]", answer)

    # 인용 번호가 하나도 없으면 실패입니다.
    if not found_numbers:
        return False, "인용 번호가 전혀 없음"

    # 찾은 문자열 번호를 정수로 바꿉니다.
    citation_numbers = []

    for number in found_numbers:
        citation_numbers.append(int(number))

    # 존재하지 않는 인용 번호가 있는지 검사합니다.
    invalid_numbers = []

    for number in citation_numbers:

        # 인용 번호는 1부터 검색 문서 개수까지만 가능합니다.
        if number < 1 or number > document_count:
            invalid_numbers.append(number)

    # 잘못된 인용 번호가 있으면 실패입니다.
    if invalid_numbers:
        return False, f"존재하지 않는 근거 번호: {invalid_numbers}"

    # 모든 인용 번호가 정상입니다.
    return True, f"인용 {len(citation_numbers)}건 정상"


# ============================================================
# 프롬프트 비교 함수
# 하나의 질문을 검색한 뒤 같은 근거로 V1, V2, V3를 실행합니다.
# 각 답변이 올바른 인용 번호를 사용했는지도 검사합니다.
# ============================================================

def compare(question):

    # 질문과 관련된 문서를 한 번만 검색합니다.
    documents = search(question)

    # 검색된 문서를 LLM에게 전달할 문자열로 만듭니다.
    context = build_context(documents)

    # 질문과 검색 결과를 출력합니다.
    print("=" * 70)
    print("📌 질문:", question)
    print("📚 근거 문서:", len(documents), "개")
    print("-" * 70)

    # 실제로 검색된 근거 내용을 출력합니다.
    print()
    print("【검색된 근거】")
    print(context)
    print()
    print("-" * 70)

    # V1, V2, V3 프롬프트를 하나씩 실행합니다.
    for name, prompt in PROMPTS.items():

        # 현재 실행 중인 프롬프트 버전을 출력합니다.
        print()
        print("✅", name)
        print("-" * 70)

        # 프롬프트 → LLM → 문자열 변환 순서로 연결합니다.
        chain = prompt | llm | StrOutputParser()

        # 같은 검색 근거와 같은 질문으로 답변을 생성합니다.
        answer = chain.invoke({
            "context": context,
            "question": question
        })

        # 생성된 답변을 출력합니다.
        print("답변:")
        print(answer)
        print()

        # 답변의 인용 번호를 검사합니다.
        citation_ok, citation_message = check_citation(
            answer,
            len(documents)
        )

        # 인용 검사 성공 여부에 따라 표시를 정합니다.
        if citation_ok:
            mark = "✓"
        else:
            mark = "✗"

        # 인용 검사 결과를 출력합니다.
        print("🔍 인용 검증:", mark, citation_message)

    print()
    print("=" * 70)


# ============================================================
# 프로그램 시작 함수
# 여러 테스트 질문을 하나씩 compare() 함수에 전달합니다.
# ============================================================

def main():

    # 비교할 테스트 질문을 준비합니다.
    test_questions = [
        "환불 신청 방법과 수수료를 알려주세요",
        "환불은 언제까지 가능한가요?",
        "배송 비용은 얼마인가요?"
    ]

    print()
    print("🚀 프롬프트 비교 데모 시작")
    print()

    # 질문을 하나씩 꺼내 프롬프트를 비교합니다.
    for question in test_questions:
        compare(question)
        print()


# ============================================================
# 이 파일을 직접 실행했을 때만 main()을 실행합니다.
# ============================================================

if __name__ == "__main__":
    main()