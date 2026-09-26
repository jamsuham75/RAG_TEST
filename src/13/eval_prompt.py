# ============================================================
# 프롬프트 버전별 성능 평가 프로그램
# 같은 질문 세트를 V1, V2, V3 프롬프트에 각각 실행하여
# 정답 개수와 정답률, 실패한 질문을 비교합니다.
# ============================================================

import os
import sys

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser


# ------------------------------------------------------------
# 11차시 폴더의 retriever.py를 사용할 수 있도록 경로를 추가합니다.
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
# 평가에 사용할 LLM을 준비합니다.
# temperature=0으로 답변의 임의성을 줄입니다.
# ------------------------------------------------------------

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


# ============================================================
# 테스트 질문
# q    : 질문
# keys : 정답으로 인정할 핵심 단어
# ============================================================

TESTS = [
    {
        "q": "환불은 며칠 이내인가요?",
        "keys": ["7일", "일주일"]
    },
    {
        "q": "교환 기간은?",
        "keys": ["30일"]
    },
    {
        "q": "대표이사 이름은?",
        "keys": ["확인할 수 없"]
    },

    # 필요한 경우 20개까지 추가합니다.
]


# ============================================================
# 프롬프트 평가 함수
# 지정한 프롬프트로 모든 질문을 실행하고 정답률을 계산합니다.
# ============================================================

def evaluate(version):

    # 현재 평가할 프롬프트를 가져옵니다.
    prompt = PROMPTS[version]

    # 프롬프트 → LLM → 문자열 변환 순서로 연결합니다.
    chain = prompt | llm | StrOutputParser()

    # 맞힌 문제 수를 저장합니다.
    correct_count = 0

    # 틀린 질문을 저장합니다.
    failed_questions = []

    # 테스트 질문을 하나씩 실행합니다.
    for test in TESTS:

        # 현재 질문을 가져옵니다.
        question = test["q"]

        # 정답으로 인정할 핵심 단어를 가져옵니다.
        answer_keys = test["keys"]

        # 질문과 관련된 문서를 검색합니다.
        documents = search(question)

        # 검색 결과가 있으면 LLM용 근거를 만듭니다.
        if documents:
            context = build_context(documents)
        else:
            context = "(자료 없음)"

        # 현재 프롬프트로 답변을 생성합니다.
        answer = chain.invoke({
            "context": context,
            "question": question
        })

        # 처음에는 오답으로 가정합니다.
        is_correct = False

        # 정답 키워드가 답변에 있는지 확인합니다.
        for key in answer_keys:

            # 키워드 하나라도 있으면 정답입니다.
            if key in answer:
                is_correct = True
                break

        # 정답이면 정답 개수를 1 증가시킵니다.
        if is_correct:
            correct_count += 1

        # 오답이면 실패 목록에 질문을 추가합니다.
        else:
            failed_questions.append(question)

    # 전체 질문 수를 구합니다.
    total_count = len(TESTS)

    # 정답률을 계산합니다.
    accuracy = correct_count / total_count * 100

    # 평가 결과를 출력합니다.
    print(
        f"[{version}] 정답 "
        f"{correct_count}/{total_count} = {accuracy:.0f}%"
    )

    # 실패한 질문이 있으면 최대 5개까지 출력합니다.
    if failed_questions:
        print(
            "   실패:",
            ", ".join(failed_questions[:5])
        )

    # 계산한 정답률을 반환합니다.
    return accuracy


# ============================================================
# 이 파일을 직접 실행했을 때만 평가를 수행합니다.
# ============================================================

if __name__ == "__main__":

    print("■ 프롬프트 버전별 정답률")

    # V1, V2, V3를 같은 질문으로 각각 평가합니다.
    for version in ("v1", "v2", "v3"):
        evaluate(version)