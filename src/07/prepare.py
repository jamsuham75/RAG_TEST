# ============================================================
# PDF 문서를 읽어서 여러 개의 청크(Chunk)로 나누는 코드입니다.
# 각 청크에 번호를 붙이고, 청크 길이를 확인한 뒤 반환합니다.
# ============================================================

import os
import sys

from langchain_text_splitters import RecursiveCharacterTextSplitter


# ------------------------------------------------------------
# 1. 06차시의 ingest.py를 사용할 수 있도록 경로를 추가합니다.
# ------------------------------------------------------------

CURRENT_DIR = os.path.dirname(__file__)
INGEST_DIR = os.path.join(CURRENT_DIR, "..", "06")

sys.path.insert(0, INGEST_DIR)

from ingest import load_documents


# ------------------------------------------------------------
# 2. 청킹 설정값을 지정합니다.
# ------------------------------------------------------------

CHUNK_SIZE = 200
CHUNK_OVERLAP = 50


# ------------------------------------------------------------
# 3. PDF 문서를 읽고 청크로 나눕니다.
# ------------------------------------------------------------

def prepare_chunks(path):

    # PDF를 페이지별 Document로 읽습니다.
    docs = load_documents(path)

    # 문서를 나눌 방법을 설정합니다.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=[". ", " ", ""],
        length_function=len,
    )

    # 페이지별 Document를 여러 청크로 나눕니다.
    chunks = splitter.split_documents(docs)


    # --------------------------------------------------------
    # 4. 각 청크에 고유 번호를 붙입니다.
    # --------------------------------------------------------

    for index, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = index


    # --------------------------------------------------------
    # 5. 각 청크의 글자 수를 조사합니다.
    # --------------------------------------------------------

    lengths = []

    for chunk in chunks:
        length = len(chunk.page_content)
        lengths.append(length)


    # --------------------------------------------------------
    # 6. 청킹 결과를 출력합니다.
    # --------------------------------------------------------

    average = sum(lengths) // len(lengths)
    minimum = min(lengths)
    maximum = max(lengths)

    print(f"✓ 청크 {len(chunks)}개 생성")
    print(f"  평균 길이: {average}자")
    print(f"  최소 길이: {minimum}자")
    print(f"  최대 길이: {maximum}자")

    # 너무 짧은 청크가 있으면 확인 메시지를 출력합니다.
    if minimum < 50:
        print("⚠ 50자 미만 청크가 있습니다. 내용을 확인하세요.")

    return chunks


# ------------------------------------------------------------
# 7. 이 파일을 직접 실행할 때만 테스트합니다.
# ------------------------------------------------------------

if __name__ == "__main__":

    # PDF를 청킹합니다.
    chunks = prepare_chunks("../../data/manual.pdf")

    # 앞의 청크 3개만 확인합니다.
    for chunk in chunks[:3]:

        # 청크 번호와 원본 페이지 번호를 출력합니다.
        chunk_id = chunk.metadata["chunk_id"]
        page_no = chunk.metadata["page_no"]

        print(f"\n[{chunk_id}] p.{page_no}")

        # 청크 내용의 앞부분만 출력합니다.
        print(chunk.page_content[:100])