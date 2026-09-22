import hashlib
import json
import re

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

import config

load_dotenv(config.ENV_PATH)

# 학습용 PDF의 반복 머리말·꼬리말
NOISE = [
    "RAG PRACTICE / 가상 문서 / v1.0",
    "교육을 위해 창작한 문서입니다. 실제 기관·제품의 안내가 아닙니다.",
]


def _load():
    if not config.DOC_PATH.is_file():
        raise FileNotFoundError(
            f"PDF 파일을 찾을 수 없습니다: {config.DOC_PATH}"
        )

    docs = PyPDFLoader(str(config.DOC_PATH)).load()

    for d in docs:
        text = d.page_content

        for noise in NOISE:
            text = text.replace(noise, "")

        # 반복 꼬리말과 페이지 표시 제거
        text = re.sub(
            r"RAG PRACTICE\s*\|\s*FICTIONAL SAMPLE\s*\d+\s*/\s*\d+",
            "",
            text,
        )

        text = re.sub(r"\n{3,}", "\n\n", text)

        d.page_content = text.strip()
        d.metadata["filename"] = config.DOC_PATH.name
        d.metadata["page_no"] = d.metadata.get("page", 0) + 1

    # 모든 페이지를 처리한 뒤 반환
    return [d for d in docs if d.page_content]


def _split(docs):
    if not 0 <= config.CHUNK_OVERLAP < config.CHUNK_SIZE:
        raise ValueError(
            "CHUNK_OVERLAP은 0 이상, CHUNK_SIZE 미만이어야 합니다."
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = splitter.split_documents(docs)

    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i

    return chunks


def _index_info():
    """저장된 인덱스를 그대로 사용해도 되는지 비교할 정보."""
    if not config.DOC_PATH.is_file():
        raise FileNotFoundError(
            f"PDF 파일을 찾을 수 없습니다: {config.DOC_PATH}"
        )

    return {
        "filename": config.DOC_PATH.name,
        "pdf_hash": hashlib.sha256(
            config.DOC_PATH.read_bytes()
        ).hexdigest(),
        "chunk_size": config.CHUNK_SIZE,
        "chunk_overlap": config.CHUNK_OVERLAP,
        "embed_model": config.EMBED_MODEL,
        "preprocess_version": 1,
    }


def get_store(rebuild: bool = False):
    load_dotenv(config.ENV_PATH)

    index_path = config.INDEX_PATH
    info_path = index_path / "index_info.json"

    current_info = _index_info()
    emb = OpenAIEmbeddings(model=config.EMBED_MODEL)

    index_exists = (
        (index_path / "index.faiss").is_file()
        and (index_path / "index.pkl").is_file()
        and info_path.is_file()
    )

    if index_exists and not rebuild:
        try:
            saved_info = json.loads(
                info_path.read_text(encoding="utf-8")
            )

            if saved_info == current_info:
                # 이 앱이 직접 만든 신뢰할 수 있는 인덱스만 로드합니다.
                store = FAISS.load_local(
                    str(index_path),
                    emb,
                    allow_dangerous_deserialization=True,
                )
                print("✓ 저장된 도서관 인덱스를 불러왔습니다.")
                return store

            print("→ 문서 또는 설정이 변경되어 인덱스를 다시 만듭니다.")

        except Exception as e:
            print(f"[인덱스 로드 실패] {e}")
            print("→ 원본 PDF로 인덱스를 다시 만듭니다.")

    chunks = _split(_load())

    if not chunks:
        raise ValueError("PDF에서 검색 가능한 텍스트를 찾지 못했습니다.")

    store = FAISS.from_documents(chunks, emb)

    index_path.mkdir(parents=True, exist_ok=True)
    store.save_local(str(index_path))

    info_path.write_text(
        json.dumps(current_info, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"✓ 도서관 인덱스 생성 완료: 조각 {len(chunks)}개")
    return store