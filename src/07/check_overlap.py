# ============================================================
# Chunk Overlap 확인 실습
# PDF 전체 내용을 하나의 문서로 합친 뒤 청킹하고,
# 앞뒤 청크에 내용이 실제로 겹치는지 확인합니다.
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
# 3. 여러 페이지의 내용을 하나의 문서로 합칩니다.
# ------------------------------------------------------------

full_text = ""

for doc in docs:
    full_text += doc.page_content + "\n\n"

merged_doc = Document(page_content=full_text)


# ------------------------------------------------------------
# 4. 문서를 청크로 나눕니다.
# ------------------------------------------------------------

splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,       # 청크 하나의 최대 글자 수
    chunk_overlap=50,     # 앞뒤 청크가 겹치는 글자 수
    separators=[". ", " ", ""],  # 자를 위치의 우선순위
    length_function=len,  # 글자 수를 기준으로 길이 계산
)

chunks = splitter.split_documents([merged_doc])


# ------------------------------------------------------------
# 5. 두 청크의 경계를 출력하여 overlap을 확인합니다.
# ------------------------------------------------------------

def show_boundary(chunks, index=0):

    # 앞 청크의 마지막 80자를 출력합니다.
    print(f"=== {index}번 청크의 마지막 80자 ===")
    print(chunks[index].page_content[-80:])

    print()

    # 다음 청크의 처음 80자를 출력합니다.
    print(f"=== {index + 1}번 청크의 처음 80자 ===")
    print(chunks[index + 1].page_content[:80])

    print()
    print("▶ 위아래에 같은 내용이 보이면 overlap이 적용된 것입니다.")


# ------------------------------------------------------------
# 6. 0번과 1번 청크의 경계를 확인합니다.
# ------------------------------------------------------------

show_boundary(chunks, 0)