# ============================================================
# 14차시 - config.py 최종 설정 검증
#
# config.py에 저장된 RAG 설정으로 실제 질문을 실행하고
# 검색과 답변이 정상적으로 동작하는지 확인합니다.
# ============================================================

import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ============================================================
# 1. 다른 차시의 파일을 가져오기 위한 경로 설정
# ============================================================

# 현재 파일이 있는 폴더입니다.
CURRENT_DIR = Path(__file__).resolve().parent

# src 폴더입니다.
SRC_DIR = CURRENT_DIR.parent

# 06차시와 13차시 폴더를 Python 검색 경로에 추가합니다.
sys.path.insert(0, str(SRC_DIR / "06"))
sys.path.insert(0, str(SRC_DIR / "13"))


# 필요한 파일을 가져옵니다.
from ingest import load_documents
from prompts import PROMPTS

# 최종 RAG 설정을 가져옵니다.
from config import (
    DOC_PATH,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EMBED_MODEL,
    TOP_K,
    LLM_MODEL,
    TEMPERATURE,
    PROMPT_VER
)


# ============================================================
# 2. OpenAI 모델 준비
# ============================================================

# .env 파일에서 OpenAI API Key를 읽습니다.
load_dotenv()

# 문서를 벡터로 변환할 임베딩 모델입니다.
embeddings = OpenAIEmbeddings(
    model=EMBED_MODEL
)

# 답변을 생성할 LLM입니다.
llm = ChatOpenAI(
    model=LLM_MODEL,
    temperature=TEMPERATURE
)


# ============================================================
# 3. 테스트 질문
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
    }
]


# ============================================================
# 4. config.py 설정으로 RAG 실행
# ============================================================

def run_test():

    # --------------------------------------------------------
    # STEP 1. PDF 문서를 읽습니다.
    # --------------------------------------------------------

    documents = load_documents(
        str(DOC_PATH)
    )

    print(f"① PDF 로딩 완료: {len(documents)}페이지")


    # --------------------------------------------------------
    # STEP 2. 문서를 chunk로 나눕니다.
    # --------------------------------------------------------

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    chunks = splitter.split_documents(
        documents
    )

    print(f"② 문서 분할 완료: {len(chunks)}개")


    # --------------------------------------------------------
    # STEP 3. FAISS 벡터 저장소를 만듭니다.
    # --------------------------------------------------------

    store = FAISS.from_documents(
        chunks,
        embeddings
    )

    print("③ FAISS 생성 완료")


    # --------------------------------------------------------
    # STEP 4. 프롬프트와 LLM을 연결합니다.
    # --------------------------------------------------------

    chain = (
        PROMPTS[PROMPT_VER]
        | llm
        | StrOutputParser()
    )

    print(f"④ 프롬프트 준비 완료: {PROMPT_VER}")


    # --------------------------------------------------------
    # STEP 5. 테스트 질문을 하나씩 실행합니다.
    # --------------------------------------------------------

    correct_count = 0

    for test in TESTS:

        # 질문을 가져옵니다.
        question = test["q"]

        # 정답으로 인정할 키워드를 가져옵니다.
        answer_keys = test["keys"]


        # ----------------------------------------------------
        # 질문과 관련된 문서를 TOP_K개 검색합니다.
        # ----------------------------------------------------

        docs = store.similarity_search(
            question,
            k=TOP_K
        )


        # ----------------------------------------------------
        # 검색된 문서를 하나의 Context로 만듭니다.
        # ----------------------------------------------------

        context = ""

        for doc in docs:
            context += doc.page_content
            context += "\n\n"


        # ----------------------------------------------------
        # LLM에게 질문하여 답변을 생성합니다.
        # ----------------------------------------------------

        answer = chain.invoke({
            "context": context,
            "question": question
        })


        # ----------------------------------------------------
        # 답변에 정답 키워드가 있는지 검사합니다.
        # ----------------------------------------------------

        correct = False

        for key in answer_keys:

            if key in answer:
                correct = True
                break


        # 정답이면 개수를 증가시킵니다.
        if correct:
            correct_count += 1


        # 질문별 결과를 출력합니다.
        print()
        print("질문:", question)
        print("답변:", answer)
        print("정답 여부:", correct)


    # --------------------------------------------------------
    # STEP 6. 전체 정답률을 계산합니다.
    # --------------------------------------------------------

    total = len(TESTS)

    rate = correct_count / total * 100


    # --------------------------------------------------------
    # STEP 7. 최종 결과를 출력합니다.
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print(f"정답: {correct_count}/{total}")
    print(f"정답률: {rate:.0f}%")
    print("=" * 60)


# ============================================================
# 5. 현재 설정 확인
# ============================================================

print("■ config.py 최종 설정 검증")
print("-" * 60)

print(f"chunk_size : {CHUNK_SIZE}")
print(f"overlap    : {CHUNK_OVERLAP}")
print(f"k          : {TOP_K}")
print(f"prompt     : {PROMPT_VER}")
print(f"LLM        : {LLM_MODEL}")

print()


# ============================================================
# 6. 검증 시작
# ============================================================

run_test()