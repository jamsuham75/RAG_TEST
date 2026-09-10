import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '07'))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from prepare import prepare_chunks

load_dotenv()

INDEX_PATH  = "faiss_index"
EMBED_MODEL = "text-embedding-3-small"
emb = OpenAIEmbeddings(model=EMBED_MODEL)

# ① 조각 준비
chunks = prepare_chunks("../../data/manual.pdf")
# ② 인덱스 생성 — 여기서 임베딩 비용 발생
print("임베딩 중...")
store = FAISS.from_documents(chunks, emb)
# ③ 디스크에 저장 (핵심!)
store.save_local(INDEX_PATH)
print(f"✓ 인덱스를 {INDEX_PATH}/ 에 저장했습니다")