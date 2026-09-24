# ============================================================
# FAISS 인덱스를 생성하거나 불러오는 코드입니다.
# 새로 만들 때는 생성 조건을 build_info.json에 함께 기록합니다.
# ============================================================

import os
import sys
import json
import datetime

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
# 사용할 문서, 모델, 저장 경로를 설정합니다.
# ------------------------------------------------------------

DOC_PATH = "../../data/manual.pdf"
EMBED_MODEL = "text-embedding-3-small"
FAISS_PATH = "faiss_index"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


# ------------------------------------------------------------
# FAISS 인덱스와 생성 정보를 함께 저장합니다.
# ------------------------------------------------------------

def save_with_meta(store, path, info):

    # FAISS 인덱스를 저장합니다.
    store.save_local(path)

    # 인덱스를 만든 시간을 추가합니다.
    info["created_at"] = datetime.datetime.now().isoformat()

    # 생성 정보를 JSON 파일로 저장합니다.
    meta_path = os.path.join(path, "build_info.json")

    with open(meta_path, "w", encoding="utf-8") as file:
        json.dump(
            info,
            file,
            ensure_ascii=False,
            indent=2
        )


# ------------------------------------------------------------
# 기존 인덱스가 있으면 불러오고, 없으면 새로 만듭니다.
# ------------------------------------------------------------

def get_store():

    # 임베딩 모델을 준비합니다.
    embedding = OpenAIEmbeddings(
        model=EMBED_MODEL
    )


    # 기존 인덱스가 있으면 그대로 불러옵니다.
    if os.path.exists(FAISS_PATH):

        print("→ 저장된 인덱스를 불러옵니다 (임베딩 비용 없음)")

        store = FAISS.load_local(
            FAISS_PATH,
            embedding,
            allow_dangerous_deserialization=True
        )

        return store


    # 기존 인덱스가 없으면 새로 만듭니다.
    print("→ 새로운 인덱스를 만듭니다")


    # PDF 문서를 작은 조각으로 나눕니다.
    chunks = prepare_chunks(DOC_PATH)


    # 문서 조각을 임베딩하여 FAISS 인덱스를 만듭니다.
    store = FAISS.from_documents(
        chunks,
        embedding
    )


    # 인덱스를 만들 때 사용한 설정 정보를 준비합니다.
    build_info = {
        "source": DOC_PATH,
        "embed_model": EMBED_MODEL,
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "chunk_count": len(chunks),
    }


    # FAISS와 생성 정보를 함께 저장합니다.
    save_with_meta(
        store,
        FAISS_PATH,
        build_info
    )

    print(f"✓ 인덱스 저장 완료: {FAISS_PATH}/")

    return store


# ------------------------------------------------------------
# 이 파일을 직접 실행했을 때 인덱스를 준비합니다.
# ------------------------------------------------------------

if __name__ == "__main__":

    store = get_store()