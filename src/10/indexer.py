# ============================================================
# FAISS 인덱스를 불러오거나 새로 만드는 코드입니다.
# 인덱스가 있으면 재사용하고, 없거나 rebuild=True이면 새로 만듭니다.
# ============================================================

import os
import sys

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS


# ------------------------------------------------------------
# prepare.py가 있는 07 폴더를 Python 검색 경로에 추가합니다.
# ------------------------------------------------------------

CURRENT_DIR = os.path.dirname(__file__)
PREPARE_DIR = os.path.join(CURRENT_DIR, "..", "07")

sys.path.insert(0, PREPARE_DIR)

from prepare import prepare_chunks


# ------------------------------------------------------------
# .env 파일에서 OpenAI API Key를 읽습니다.
# ------------------------------------------------------------

load_dotenv()


# ------------------------------------------------------------
# 사용할 파일과 모델을 설정합니다.
# ------------------------------------------------------------

INDEX_PATH = "faiss_index"
DOC_PATH = "../../data/manual.pdf"
EMBED_MODEL = "text-embedding-3-small"


# ------------------------------------------------------------
# FAISS 인덱스를 준비합니다.
# rebuild=True이면 기존 인덱스가 있어도 새로 만듭니다.
# ------------------------------------------------------------

def get_store(rebuild=False):

    # 임베딩 모델을 준비합니다.
    embedding = OpenAIEmbeddings(
        model=EMBED_MODEL
    )


    # 기존 인덱스가 있고 재생성 요청이 없으면 불러옵니다.
    if os.path.exists(INDEX_PATH) and not rebuild:

        print("→ 저장된 인덱스를 불러옵니다 (임베딩 비용 없음)")

        store = FAISS.load_local(
            INDEX_PATH,
            embedding,
            allow_dangerous_deserialization=True
        )

        return store


    # 기존 인덱스가 없거나 rebuild=True이면 새로 만듭니다.
    print("→ 인덱스를 새로 만듭니다 (임베딩 비용 발생)")


    # PDF 문서를 작은 조각으로 나눕니다.
    chunks = prepare_chunks(DOC_PATH)


    # 문서 조각을 임베딩하고 FAISS 인덱스를 만듭니다.
    store = FAISS.from_documents(
        chunks,
        embedding
    )


    # 만든 인덱스를 디스크에 저장합니다.
    store.save_local(INDEX_PATH)

    print(f"✓ {INDEX_PATH}/ 에 저장 완료")


    # 완성된 FAISS 객체를 반환합니다.
    return store


# ------------------------------------------------------------
# 이 파일을 직접 실행했을 때 인덱스를 준비합니다.
# ------------------------------------------------------------

if __name__ == "__main__":

    store = get_store()