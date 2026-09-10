import sys
import os

# 06 디렉토리를 path에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '07'))

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from prepare import prepare_chunks        # 7차시에서 만든 함수 

load_dotenv()
# ①② 문서 읽고 조각내기 (6·7차시 결과 재사용)
chunks = prepare_chunks("../../data/manual.pdf")
# ③ 조각을 벡터로 바꿔 저장
print("임베딩 중... (조금 걸립니다)")
emb = OpenAIEmbeddings(model="text-embedding-3-small") 

store = FAISS.from_documents(chunks, emb)
print("✓ 인덱싱 완료")