# ============================================================
# 기본 RAG 전체 과정을 실행하는 예제입니다.
# PDF를 분할하고 FAISS에 저장한 뒤, 관련 문서를 검색하여
# 검색된 문서를 근거로 LLM이 답변하도록 합니다.
# ============================================================

import os
import sys

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS


# ------------------------------------------------------------
# 1. 7차시 폴더를 Python 모듈 검색 경로에 추가
# ------------------------------------------------------------

# 현재 파일이 있는 폴더를 구합니다.
CURRENT_DIR = os.path.dirname(__file__)

# 7차시 폴더의 경로를 만듭니다.
CH07_DIR = os.path.join(CURRENT_DIR, "..", "07")

# 7차시의 prepare.py를 import할 수 있도록 경로를 추가합니다.
sys.path.insert(0, CH07_DIR)

# 7차시에서 만든 문서 준비 함수를 가져옵니다.
from prepare import prepare_chunks


# ------------------------------------------------------------
# 2. 환경변수 로드
# ------------------------------------------------------------

# .env 파일에서 OPENAI_API_KEY를 읽습니다.
load_dotenv()


# ------------------------------------------------------------
# 3. PDF 읽기 + 문서 분할
# ------------------------------------------------------------

# PDF를 읽고 검색하기 좋은 작은 조각으로 나눕니다.
chunks = prepare_chunks("../../data/manual.pdf")

print(f"✓ 문서 분할 완료: {len(chunks)}개")


# ------------------------------------------------------------
# 4. 임베딩 + FAISS 벡터 저장소 생성
# ------------------------------------------------------------

print("임베딩 중... (조금 걸립니다)")

# 문장을 숫자 벡터로 바꾸는 임베딩 모델을 준비합니다.
emb = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

# 문서 조각을 벡터로 변환하여 FAISS에 저장합니다.
store = FAISS.from_documents(chunks, emb)

print(f"✓ 인덱싱 완료: {store.index.ntotal}개 벡터")


# ------------------------------------------------------------
# 5. 답변 생성용 LLM 준비
# ------------------------------------------------------------

# 검색된 자료를 이용해 답변할 LLM을 준비합니다.
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

print("✓ 준비 완료\n")


# ------------------------------------------------------------
# 6. 검색된 문서를 Context 문자열로 변환
# ------------------------------------------------------------

def build_context(docs):
    # 여러 Document를 하나의 문자열로 합칠 리스트입니다.
    parts = []

    # 검색된 문서를 하나씩 꺼냅니다.
    for i, doc in enumerate(docs, 1):

        # 문서 번호, 파일명, 페이지, 내용을 문자열로 만듭니다.
        text = (
            f"[{i}] "
            f"({doc.metadata['filename']} "
            f"p.{doc.metadata['page_no']})\n"
            f"{doc.page_content}"
        )

        # 만들어진 문자열을 리스트에 추가합니다.
        parts.append(text)

    # 모든 문서를 하나의 문자열로 합칩니다.
    context = "\n\n".join(parts)

    return context


# ------------------------------------------------------------
# 7. 질문 → 검색 → 답변 생성
# ------------------------------------------------------------

def ask(question, k=3):

    # 질문과 의미가 가까운 문서 k개를 검색합니다.
    found = store.similarity_search(question, k=k)

    # 검색 결과가 없으면 답변 생성을 중단합니다.
    if not found:
        print("관련 자료를 찾지 못했습니다.")
        return

    # 검색된 문서들을 LLM에게 전달할 Context로 만듭니다.
    context = build_context(found)

    # Context와 질문을 이용하여 프롬프트를 만듭니다.
    prompt = (
        "아래 자료만 근거로 답하세요.\n"
        "자료에 없는 내용은 '자료에서 확인할 수 없습니다'라고 답하세요.\n"
        "추측하지 마세요.\n\n"
        f"[자료]\n{context}\n\n"
        f"[질문] {question}"
    )

    # 프롬프트를 LLM에게 전달합니다.
    response = llm.invoke(prompt)

    # LLM 응답에서 실제 답변 문자열만 가져옵니다.
    answer = response.content

    # 질문과 답변을 출력합니다.
    print("Q:", question)
    print("A:", answer)

    # 검색에 사용된 출처를 출력합니다.
    print("\n참고한 자료:")

    for doc in found:
        print(
            f"   · {doc.metadata['filename']} "
            f"{doc.metadata['page_no']}페이지"
        )

    print("-" * 55)


# ------------------------------------------------------------
# 8. 프로그램 실행
# ------------------------------------------------------------

if __name__ == "__main__":
    ask("환불은 며칠 이내에 신청해야 하나요?")