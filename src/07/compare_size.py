# ============================================================
# Chunk Size 비교 실습
# PDF 전체 내용을 하나의 문서로 합친 뒤,
# chunk_size를 바꿔가며 청크 수와 길이를 비교합니다.
# ============================================================

import os
import sys

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ------------------------------------------------------------
# 1. 06차시의 ingest.py를 사용할 수 있도록 경로를 추가합니다.
# ------------------------------------------------------------

CURRENT_DIR = os.path.dirname(__file__)
INGEST_DIR = os.path.join(CURRENT_DIR, "..", "06")

sys.path.insert(0, INGEST_DIR)

from ingest import load_documents


# ------------------------------------------------------------
# 2. PDF 문서를 불러옵니다.
# ------------------------------------------------------------

docs = load_documents("../../data/manual.pdf")


# ------------------------------------------------------------
# 3. 페이지별 내용을 하나의 문자열로 합칩니다.
# ------------------------------------------------------------

full_text = ""

for doc in docs:
    full_text += doc.page_content + "\n\n"


# 합친 문자열을 하나의 LangChain Document로 만듭니다.
merged_doc = Document(page_content=full_text)


# ------------------------------------------------------------
# 4. 지정한 크기로 문서를 나누고 결과를 출력합니다.
# ------------------------------------------------------------

def try_size(document, chunk_size, chunk_overlap):

    # 전달받은 크기로 문서 분할기를 만듭니다.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    # 하나의 문서를 여러 청크로 나눕니다.
    chunks = splitter.split_documents([document])

    # 각 청크의 글자 수를 저장합니다.
    lengths = []

    for chunk in chunks:
        length = len(chunk.page_content)
        lengths.append(length)

    # 청크의 평균 길이를 계산합니다.
    average = sum(lengths) // len(lengths)

    # 결과를 출력합니다.
    print(
        f"size={chunk_size:<5} "
        f"overlap={chunk_overlap:<4} "
        f"청크수={len(chunks):<4} "
        f"평균={average:<5} "
        f"최소={min(lengths):<5} "
        f"최대={max(lengths)}"
    )

    return chunks


# ------------------------------------------------------------
# 5. 여러 chunk_size를 적용하여 결과를 비교합니다.
# ------------------------------------------------------------

print("chunk_size별 비교")
print("-" * 60)

chunk_sizes = [30, 50, 100, 150, 250]

for size in chunk_sizes:

    # overlap은 chunk_size의 20%로 설정합니다.
    overlap = int(size * 0.2)

    # 현재 설정으로 청킹 결과를 확인합니다.
    try_size(merged_doc, size, overlap)