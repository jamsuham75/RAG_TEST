# ============================================================
# 14차시 - RAG 설정값 비교 실험
#
# ① PDF를 chunk로 나눈다.
# ② FAISS 검색 저장소를 만든다.
# ③ 테스트 질문을 검색하고 답변한다.
# ④ 정답 키워드가 포함되었는지 확인한다.
# ⑤ 설정에 따른 정답률을 비교한다.
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

CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR.parent

sys.path.insert(0, str(SRC_DIR / "06"))
sys.path.insert(0, str(SRC_DIR / "13"))

from ingest import load_documents
from prompts import PROMPTS


# ============================================================
# 2. OpenAI 모델 준비
# ============================================================

load_dotenv()

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


# ============================================================
# 3. PDF 문서 읽기
# ============================================================

ROOT_DIR = Path(__file__).resolve().parents[2]
PDF_PATH = ROOT_DIR / "data" / "manual.pdf"

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
# 5. 실험 실행
# ============================================================

def run_experiment(name, chunk_size, overlap, k, version):

    print()
    print("=" * 70)
    print(f"실험: {name}")
    print(
        f"chunk={chunk_size}, "
        f"overlap={overlap}, "
        f"k={k}, "
        f"prompt={version}"
    )
    print("=" * 70)


    # --------------------------------------------------------
    # STEP 1. PDF 문서를 chunk로 자릅니다.
    # --------------------------------------------------------

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap
    )

    chunks = splitter.split_documents(documents)

    print(f"① 문서 분할 완료: {len(chunks)}개")


    # --------------------------------------------------------
    # STEP 2. chunk를 임베딩하여 FAISS를 만듭니다.
    # --------------------------------------------------------

    store = FAISS.from_documents(
        chunks,
        embeddings
    )

    print("② FAISS 생성 완료")


    # --------------------------------------------------------
    # STEP 3. 사용할 프롬프트와 LLM을 연결합니다.
    # --------------------------------------------------------

    chain = (
        PROMPTS[version]
        | llm
        | StrOutputParser()
    )

    print(f"③ 프롬프트 준비 완료: {version}")


    # --------------------------------------------------------
    # STEP 4. 테스트 질문을 하나씩 실행합니다.
    # --------------------------------------------------------

    correct_count = 0

    for test in TESTS:

        question = test["q"]
        answer_keys = test["keys"]


        # 질문과 관련된 문서를 k개 찾습니다.
        docs = store.similarity_search(
            question,
            k=k
        )


        # 검색된 문서를 하나의 문자열로 합칩니다.
        context = ""

        for doc in docs:
            context += doc.page_content
            context += "\n\n"


        # Context를 이용하여 답변을 생성합니다.
        answer = chain.invoke({
            "context": context,
            "question": question
        })


        # 답변에 정답 키워드가 있는지 검사합니다.
        correct = False

        for key in answer_keys:

            if key in answer:
                correct = True
                break


        # 정답이면 개수를 증가시킵니다.
        if correct:
            correct_count += 1


        # 질문별 결과를 보여줍니다.
        print()
        print("질문:", question)
        print("답변:", answer)
        print("정답 여부:", correct)


    # --------------------------------------------------------
    # STEP 5. 전체 정답률을 계산합니다.
    # --------------------------------------------------------

    total = len(TESTS)

    rate = correct_count / total * 100


    print()
    print("-" * 70)
    print(
        f"{name} 결과: "
        f"{correct_count}/{total} "
        f"({rate:.0f}%)"
    )


# ============================================================
# 6. 실제 실험 시작
# ============================================================

run_experiment(
    name="기준선",
    chunk_size=500,
    overlap=50,
    k=3,
    version="v2"
)