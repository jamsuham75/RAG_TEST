from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

loader = TextLoader("../../data/notice.txt", encoding="utf-8")
documents = loader.load()

print(f"문서 개수: {len(documents)}")
# 2단계: 텍스트 분할
splitter = RecursiveCharacterTextSplitter(
    chunk_size=150,
    chunk_overlap=30
)
chunks = splitter.split_documents(documents) 
print(f"chunk 개수: {len(chunks)}")
# 3단계: 결과 확인
for i, chunk in enumerate(chunks, 1):
    print(f"Chunk {i}: {len(chunk.page_content)} 글자")