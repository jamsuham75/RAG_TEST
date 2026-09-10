import sys
import os

from langchain_text_splitters import RecursiveCharacterTextSplitter

# 06 디렉토리를 path에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '06'))

from ingest import load_documents

docs = load_documents("../../data/manual.pdf")

# ✨ 이 부분만 07에 추가
from langchain_core.documents import Document
full_text = "\n\n".join([d.page_content for d in docs])
merged_doc = Document(page_content=full_text)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,        # 조각 하나의 최대 길이
    chunk_overlap=50,      # 겹치는 길이
    # separators=["\n\n", "\n", ". ", " ", ""],   # 자를 곳 우선순위     
    separators=[". ", " ", ""],   # 자를 곳 우선순위     
    length_function=len,   # 길이를 세는 방법 (글자 수)
)

chunks = splitter.split_documents([merged_doc]) 


def try_size(docs, size, overlap):
    sp = RecursiveCharacterTextSplitter(
        chunk_size=size, chunk_overlap=overlap,         
        separators=["\n\n", "\n", ". ", " ", ""])     
    chunks = sp.split_documents(docs)
    lengths = [len(c.page_content) for c in chunks]     
    print(f"size={size:<5} overlap={overlap:<4} "           
          f"조각수={len(chunks):<4} "           
          f"평균={sum(lengths)//len(lengths):<5} "           
          f"최소={min(lengths):<5} 최대={max(lengths)}")     
    return chunks

print("chunk_size별 비교 (작은 문서라 30자부터 시작)") 
print("-" * 60)
for s in (30, 50, 100, 150, 250):     
    try_size([merged_doc], s, int(s * 0.2))