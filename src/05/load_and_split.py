# ============================================================
# 텍스트 파일 로딩 및 분할 실습
# notice.txt 파일을 읽은 뒤 작은 크기의 Chunk로 나눕니다.
# 마지막으로 분할된 Chunk의 개수와 각 Chunk의 글자 수를 확인합니다.
# ============================================================

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ------------------------------------------------------------
# 1. 텍스트 파일 불러오기
# ------------------------------------------------------------

# 읽어올 텍스트 파일을 지정합니다.
loader = TextLoader(
    "../../data/notice.txt",
    encoding="utf-8"
)

# 파일을 읽어 LangChain의 Document 객체로 변환합니다.
documents = loader.load()

# 불러온 문서의 개수를 확인합니다.
print(f"문서 개수: {len(documents)}")


# ------------------------------------------------------------
# 2. 문서를 작은 Chunk로 나누기
# ------------------------------------------------------------

# 한 Chunk는 최대 150자로 하고, 앞뒤 Chunk를 30자 정도 겹치게 합니다.
splitter = RecursiveCharacterTextSplitter(
    chunk_size=150,
    chunk_overlap=30
)

# 불러온 문서를 여러 개의 Chunk로 나눕니다.
chunks = splitter.split_documents(documents)

# 만들어진 Chunk의 개수를 확인합니다.
print(f"Chunk 개수: {len(chunks)}")


# ------------------------------------------------------------
# 3. 각 Chunk의 크기 확인하기
# ------------------------------------------------------------

# 각 Chunk를 하나씩 꺼내 실제 글자 수를 출력합니다.
for i, chunk in enumerate(chunks, 1):

    # page_content에는 Chunk의 실제 텍스트가 들어 있습니다.
    text = chunk.page_content

    # Chunk 번호와 글자 수를 출력합니다.
    print(f"Chunk {i}: {len(text)} 글자")