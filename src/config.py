from pathlib import Path


# config.py는 G:\RAG_TEST\src\config.py에 있음
SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent


# ── 문서 처리 ──
DOC_PATH = PROJECT_ROOT / "data" / "manual.pdf"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


# ── 임베딩 · 저장소 ──
EMBED_MODEL = "text-embedding-3-small"

# 인덱스도 프로젝트 루트 기준으로 고정
INDEX_PATH = PROJECT_ROOT / "faiss_index"


# ── 검색 ──
TOP_K = 5
MIN_SCORE = 0.0
SEARCH_TYPE = "similarity"


# ── 생성 ──
LLM_MODEL = "gpt-4o-mini"
TEMPERATURE = 0
PROMPT_VER = "v3"


# ── 메시지 ──
MSG_NO_DOC = "관련 자료를 찾지 못했습니다."
MSG_ERROR = "일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."