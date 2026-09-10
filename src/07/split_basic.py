import sys
import os

from langchain_text_splitters import RecursiveCharacterTextSplitter

# 06 디렉토리를 path에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '06'))

from ingest import load_documents


docs = load_documents("../../data/manual.pdf")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,        # 조각 하나의 최대 길이
    chunk_overlap=20,      # 겹치는 길이
    separators=["\n\n", "\n", ". ", " ", ""],   # 자를 곳 우선순위     
    length_function=len,   # 길이를 세는 방법 (글자 수)
)

chunks = splitter.split_documents(docs) 


print(f"원본 {len(docs)}쪽  →  조각 {len(chunks)}개") 
print()
print("--- 0번 조각 ---")
print(chunks[0].page_content)
print()
print("메타데이터:", chunks[0].metadata)