import json
import datetime
import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '07'))
from prepare import prepare_chunks

load_dotenv()

DOC_PATH = "../../data/manual.pdf"
EMBED_MODEL = "text-embedding-3-small"
FAISS_PATH = "faiss_index"

def save_with_meta(store, path, info):
    """인덱스를 메타데이터와 함께 저장"""
    store.save_local(path)
    info["created_at"] = datetime.datetime.now().isoformat()
    with open(f"{path}/build_info.json", "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)

def get_store():
    emb = OpenAIEmbeddings(model=EMBED_MODEL)
    
    # 인덱스가 이미 있으면 로드
    if os.path.exists(FAISS_PATH):
        print(f"→ 저장된 인덱스를 불러옵니다 (비용 0)")
        store = FAISS.load_local(FAISS_PATH, emb, allow_dangerous_deserialization=True)
        return store
    
    # 없으면 생성
    print("→ 새로운 인덱스를 만듭니다")
    chunks = prepare_chunks(DOC_PATH)
    store = FAISS.from_documents(chunks, emb)
    
    # ← 메타데이터와 함께 저장
    save_with_meta(store, FAISS_PATH, {
        "source": DOC_PATH,
        "embed_model": EMBED_MODEL,
        "chunk_size": 500,
        "chunk_overlap": 50,
        "chunk_count": len(chunks),
    })
    print(f"✓ 인덱스 저장 완료: {FAISS_PATH}/")
    
    return store

if __name__ == "__main__":
    store = get_store()