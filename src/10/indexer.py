import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '07'))
from prepare import prepare_chunks

load_dotenv()

INDEX_PATH  = "faiss_index"
EMBED_MODEL = "text-embedding-3-small"
DOC_PATH    = "../../data/manual.pdf"

def get_store(rebuild: bool = False):
    # 인덱스가 있으면 불러오고, 없으면 새로 만든다
    emb = OpenAIEmbeddings(model=EMBED_MODEL)

    if os.path.exists(INDEX_PATH) and not rebuild:
        print("→ 저장된 인덱스를 불러옵니다 (비용 0)")
        return FAISS.load_local(
            INDEX_PATH, emb, allow_dangerous_deserialization=True)

    print("→ 인덱스를 새로 만듭니다 (임베딩 비용 발생)")     
    chunks = prepare_chunks(DOC_PATH)     
    store = FAISS.from_documents(chunks, emb)     
    store.save_local(INDEX_PATH)
    print(f"✓ {INDEX_PATH}/ 에 저장 완료")     
    return store

if __name__ == "__main__":     
    store = get_store()