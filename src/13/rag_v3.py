# ============================================================
# RAG 질문 처리 프로그램
# 질문과 관련된 문서를 검색하고 V3 프롬프트로 답변을 생성합니다.
# 답변의 인용 번호를 검사하고 답변, 출처, 검증 결과를 반환합니다.
# ============================================================

import os
import sys

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser


# ------------------------------------------------------------
# 11차시의 retriever.py를 사용할 수 있도록 경로를 추가합니다.
# ------------------------------------------------------------

CURRENT_DIR = os.path.dirname(__file__)
RETRIEVER_DIR = os.path.join(CURRENT_DIR, "..", "11")

sys.path.append(RETRIEVER_DIR)


# ------------------------------------------------------------
# 필요한 기능을 가져옵니다.
# ------------------------------------------------------------

from retriever import search, build_context
from prompts import RAG_PROMPT_V3
from validators import check_citation


# ------------------------------------------------------------
# .env 파일의 OPENAI_API_KEY를 불러옵니다.
# ------------------------------------------------------------

load_dotenv()


# ------------------------------------------------------------
# 답변 생성에 사용할 LLM을 준비합니다.
# ------------------------------------------------------------

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


# ------------------------------------------------------------
# V3 프롬프트 → LLM → 문자열 변환 순서로 연결합니다.
# 앞의 _는 이 파일 내부에서 사용하는 변수라는 의미입니다.
# ------------------------------------------------------------

_chain = RAG_PROMPT_V3 | llm | StrOutputParser()


# 자료에 없는 내용을 나타내는 문구입니다.
NO_INFO = "자료에서 확인할 수 없습니다"


# ============================================================
# 질문 처리 함수
# 문서 검색 → 답변 생성 → 인용 검사 → 결과 반환을 수행합니다.
# verbose=True이면 실행 내용을 화면에 출력합니다.
# ============================================================

def ask(question, k=3, verbose=True):

    # 질문과 관련된 문서를 검색합니다.
    documents = search(question, k=k)

    # verbose가 True이면 질문을 출력합니다.
    if verbose:
        print("Q:", question)

    # --------------------------------------------------------
    # 검색 결과가 없는 경우
    # --------------------------------------------------------

    if not documents:

        # 검색 실패 결과를 만듭니다.
        result = {
            "answer": "관련 자료를 찾지 못했습니다.",
            "sources": [],
            "cited": False,
            "insufficient": True
        }

        # verbose가 True이면 검색 실패 내용을 출력합니다.
        if verbose:
            print("A:", result["answer"])
            print("⚠️ 검색 결과 없음")
            print("-" * 55)

        # LLM을 호출하지 않고 바로 결과를 반환합니다.
        return result

    # --------------------------------------------------------
    # 검색 결과가 있는 경우
    # --------------------------------------------------------

    # 검색 문서를 LLM에게 전달할 문자열로 만듭니다.
    context = build_context(documents)

    # V3 프롬프트를 사용하여 답변을 생성합니다.
    answer = _chain.invoke({
        "context": context,
        "question": question
    })

    # 답변의 [1], [2] 같은 인용 번호를 검사합니다.
    cited, citation_message = check_citation(
        answer,
        len(documents)
    )

    # --------------------------------------------------------
    # 화면 출력
    # --------------------------------------------------------

    if verbose:

        # 생성된 답변을 출력합니다.
        print("A:", answer)

        # 검색된 문서의 페이지 번호를 출력합니다.
        pages = []

        for document in documents:
            page_no = document.metadata["page_no"]
            pages.append(f"p.{page_no}")

        print("출처:", pages)

        # 인용 검사 결과를 출력합니다.
        print("인용:", citation_message)

        # 인용 검증에 실패하면 경고합니다.
        if not cited:
            print("⚠️ 인용 검증 실패 — 확인 필요")

        print("-" * 55)

    # --------------------------------------------------------
    # 검색된 문서의 metadata를 출처 정보로 저장합니다.
    # --------------------------------------------------------

    sources = []

    for document in documents:
        sources.append(document.metadata)

    # --------------------------------------------------------
    # 최종 결과를 딕셔너리로 반환합니다.
    # --------------------------------------------------------

    return {
        "answer": answer,
        "sources": sources,
        "cited": cited,
        "insufficient": NO_INFO in answer
    }


# ============================================================
# 이 파일을 직접 실행했을 때 테스트합니다.
# ============================================================

if __name__ == "__main__":

    ask("환불은 며칠 이내에 신청해야 하나요?")
    ask("대표이사가 누구인가요?")
    ask("환불 방법과 수수료를 알려주세요")