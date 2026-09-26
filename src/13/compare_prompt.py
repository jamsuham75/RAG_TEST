# ============================================================
# 프롬프트 버전 비교 프로그램
# 같은 질문과 같은 검색 자료를 V1, V2, V3 프롬프트에 전달하여
# 프롬프트에 따라 답변이 어떻게 달라지는지 비교합니다.
# ============================================================

import os
import sys

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser


# ------------------------------------------------------------
# 11차시 폴더의 retriever.py를 사용할 수 있도록 경로를 추가합니다.
# append()를 사용해 현재 13차시 폴더를 먼저 찾도록 합니다.
# ------------------------------------------------------------

CURRENT_DIR = os.path.dirname(__file__)
RETRIEVER_DIR = os.path.join(CURRENT_DIR, "..", "11")

sys.path.append(RETRIEVER_DIR)


# ------------------------------------------------------------
# 이전 차시에서 만든 검색 기능을 가져옵니다.
# prompts.py는 현재 13차시 폴더의 파일을 사용합니다.
# ------------------------------------------------------------

from retriever import search, build_context
from prompts import PROMPTS


# ------------------------------------------------------------
# .env 파일의 OPENAI_API_KEY를 환경변수로 불러옵니다.
# ------------------------------------------------------------

load_dotenv()


# ------------------------------------------------------------
# 답변 생성에 사용할 LLM을 준비합니다.
# temperature=0은 답변의 임의성을 줄여 비교하기 쉽게 합니다.
# ------------------------------------------------------------

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


# ============================================================
# 프롬프트 비교 함수
# 하나의 질문을 검색한 뒤 같은 근거로 V1, V2, V3를 비교합니다.
# ============================================================

def compare(question):

    # 질문과 관련된 문서를 한 번만 검색합니다.
    documents = search(question)

    # 검색된 문서를 LLM에게 전달할 문자열로 만듭니다.
    context = build_context(documents)

    # 질문과 검색 결과 개수를 출력합니다.
    print("=" * 60)
    print("Q:", question)
    print("근거:", len(documents), "개")
    print("-" * 60)

    # V1, V2, V3 프롬프트를 하나씩 실행합니다.
    for name, prompt in PROMPTS.items():

        # 프롬프트 → LLM → 문자열 변환 순서로 연결합니다.
        chain = prompt | llm | StrOutputParser()

        # 같은 검색 자료와 같은 질문으로 답변을 생성합니다.
        answer = chain.invoke({
            "context": context,
            "question": question
        })

        # 현재 프롬프트 버전과 답변을 출력합니다.
        print()
        print(f"[{name}]")
        print(answer)

    # 하나의 질문에 대한 비교가 끝났음을 표시합니다.
    print("=" * 60)


# ============================================================
# 이 파일을 직접 실행했을 때만 테스트합니다.
# ============================================================

if __name__ == "__main__":

    compare("환불 신청 방법과 수수료를 알려주세요")