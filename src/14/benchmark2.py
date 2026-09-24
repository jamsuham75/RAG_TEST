# ============================================================
# 14차시 - RAG 설정값 비교 실험
#
# chunk_size, k, 프롬프트를 하나씩 바꿔가며
# RAG의 정답률이 어떻게 변하는지 비교합니다.
# ============================================================

import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ============================================================
# 1. 다른 차시의 파일 가져오기
# ============================================================

# 현재 파일이 있는 폴더입니다.
CURRENT_DIR = Path(__file__).resolve().parent

# src 폴더입니다.
SRC_DIR = CURRENT_DIR.parent

# 06차시와 13차시 폴더를 Python 검색 경로에 추가합니다.
sys.path.insert(0, str(SRC_DIR / "06"))
sys.path.insert(0, str(SRC_DIR / "13"))

from ingest import load_documents
from prompts import PROMPTS


# ============================================================
# 2. OpenAI 모델 준비
# ============================================================

# .env 파일에서 OpenAI API Key를 읽습니다.
load_dotenv()

# 문서를 숫자 벡터로 바꾸는 임베딩 모델입니다.
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

# 답변을 생성할 LLM입니다.
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


# ============================================================
# 3. PDF 문서 읽기
# ============================================================

# 프로젝트 최상위 폴더를 찾습니다.
ROOT_DIR = Path(__file__).resolve().parents[2]

# PDF 파일 경로를 만듭니다.
PDF_PATH = ROOT_DIR / "data" / "manual.pdf"

# PDF 문서를 한 번만 읽어둡니다.
documents = load_documents(str(PDF_PATH))


# ============================================================
# 4. 테스트 질문
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
# 5. 하나의 실험 실행
# ============================================================

def run_experiment(name, chunk_size, overlap, k, version):

    print()
    print("-" * 70)
    print(
        f"{name} : "
        f"chunk={chunk_size}, "
        f"overlap={overlap}, "
        f"k={k}, "
        f"prompt={version}"
    )
    print("-" * 70)


    # --------------------------------------------------------
    # STEP 1. 문서를 chunk로 나눕니다.
    # --------------------------------------------------------

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap
    )

    chunks = splitter.split_documents(documents)

    print(f"문서 조각 수: {len(chunks)}")


    # --------------------------------------------------------
    # STEP 2. chunk를 임베딩하여 FAISS를 만듭니다.
    # --------------------------------------------------------

    store = FAISS.from_documents(
        chunks,
        embeddings
    )


    # --------------------------------------------------------
    # STEP 3. 사용할 프롬프트와 LLM을 연결합니다.
    # --------------------------------------------------------

    chain = (
        PROMPTS[version]
        | llm
        | StrOutputParser()
    )


    # --------------------------------------------------------
    # STEP 4. 테스트 질문을 하나씩 실행합니다.
    # --------------------------------------------------------

    correct_count = 0

    for test in TESTS:

        # 질문을 꺼냅니다.
        question = test["q"]

        # 정답으로 인정할 키워드를 꺼냅니다.
        answer_keys = test["keys"]


        # ----------------------------------------------------
        # 질문과 관련된 문서를 k개 검색합니다.
        # ----------------------------------------------------

        docs = store.similarity_search(
            question,
            k=k
        )


        # ----------------------------------------------------
        # 검색된 문서를 하나의 Context로 합칩니다.
        # ----------------------------------------------------

        context = ""

        for doc in docs:
            context += doc.page_content
            context += "\n\n"


        # ----------------------------------------------------
        # LLM에게 질문하여 답변을 생성합니다.
        # ----------------------------------------------------

        answer = chain.invoke(
            {
                "context": context,
                "question": question
            }
        )


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


    # --------------------------------------------------------
    # STEP 5. 정답률을 계산합니다.
    # --------------------------------------------------------

    total = len(TESTS)

    rate = correct_count / total * 100


    # --------------------------------------------------------
    # STEP 6. 실험 결과를 출력합니다.
    # --------------------------------------------------------

    print(
        f"결과: "
        f"{correct_count}/{total} "
        f"({rate:.0f}%)"
    )


# ============================================================
# 6. chunk_size 비교
# ============================================================

print()
print("=" * 80)
print("1. chunk_size 비교")
print("k=3, prompt=v2 고정")
print("=" * 80)

run_experiment(
    name="chunk_500",
    chunk_size=500,
    overlap=50,
    k=3,
    version="v2"
)

run_experiment(
    name="chunk_1024",
    chunk_size=1024,
    overlap=100,
    k=3,
    version="v2"
)

run_experiment(
    name="chunk_2048",
    chunk_size=2048,
    overlap=200,
    k=3,
    version="v2"
)


# ============================================================
# 7. k값 비교
# ============================================================

print()
print("=" * 80)
print("2. k값 비교")
print("chunk=500, prompt=v2 고정")
print("=" * 80)

run_experiment(
    name="k_3",
    chunk_size=500,
    overlap=50,
    k=3,
    version="v2"
)

run_experiment(
    name="k_5",
    chunk_size=500,
    overlap=50,
    k=5,
    version="v2"
)

run_experiment(
    name="k_10",
    chunk_size=500,
    overlap=50,
    k=10,
    version="v2"
)


# ============================================================
# 8. 프롬프트 버전 비교
# ============================================================

print()
print("=" * 80)
print("3. 프롬프트 버전 비교")
print("chunk=500, k=3 고정")
print("=" * 80)

run_experiment(
    name="v1",
    chunk_size=500,
    overlap=50,
    k=3,
    version="v1"
)

run_experiment(
    name="v2",
    chunk_size=500,
    overlap=50,
    k=3,
    version="v2"
)

run_experiment(
    name="v3",
    chunk_size=500,
    overlap=50,
    k=3,
    version="v3"
)