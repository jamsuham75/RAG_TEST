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

def show_boundary(chunks, i=0):
    print(f"=== {i}번 조각의 마지막 80자 ===")
    print(chunks[i].page_content[-80:])
    print()
    print(f"=== {i+1}번 조각의 처음 80자 ===")
    print(chunks[i+1].page_content[:80])
    print()
    print("▶ 위아래에 같은 문장이 보이면 overlap 정상 작동!") 

    
# 3·4번 조각 사이가 실제로 겹치는 지점입니다
show_boundary(chunks, 0)