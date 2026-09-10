import sys
import os

from langchain_text_splitters import RecursiveCharacterTextSplitter

# 06 디렉토리를 path에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '06'))

from ingest import load_documents

CHUNK_SIZE = 200
CHUNK_OVERLAP = 50

def prepare_chunks(path: str):
    # 문서를 읽고 조각으로 나눠서 돌려준다
    docs = load_documents(path)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=[". ", " ", ""],   # 자를 곳 우선순위 
        length_function=len,
    )
    chunks = splitter.split_documents(docs)
    # 조각마다 번호를 매겨둔다 (나중에 추적용)
    for i, c in enumerate(chunks):
        c.metadata["chunk_id"] = i
    lengths = [len(c.page_content) for c in chunks]
    print(f"✓ 조각 {len(chunks)}개 생성 "           
          f"(평균 {sum(lengths)//len(lengths)}자, "           
          f"최소 {min(lengths)}자, 최대 {max(lengths)}자)")     
    if min(lengths) < 50:
        print("⚠ 50자 미만 조각이 있습니다. chunk_size 확인 권장")     
    return chunks
    
if __name__ == "__main__":
    chunks = prepare_chunks("../../data/manual.pdf")     
    for c in chunks[:3]:
        print(f"\n[{c.metadata['chunk_id']}] "               
              f"p.{c.metadata['page_no']}")         
        print(c.page_content[:100])