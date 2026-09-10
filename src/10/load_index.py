from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS 
from langchain_openai import OpenAIEmbeddings

load_dotenv()

emb = OpenAIEmbeddings(model="text-embedding-3-small")

# 저장된 인덱스 불러오기 (비용 0, 즉시 완료)
store = FAISS.load_local(
    "faiss_index",
    emb,
    allow_dangerous_deserialization=True,
)
print("✓ 인덱스 로드 완료")
found = store.similarity_search("환불 규정", k=3)
print(f"검색 결과 {len(found)}건")