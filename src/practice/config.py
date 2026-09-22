from pathlib import Path

BASE = Path(__file__).resolve().parent
PROJECT_ROOT = BASE.parent.parent

# ── 환경 변수 ──
ENV_PATH = PROJECT_ROOT / ".env"

# ── 문서 처리 ──
DOC_PATH = PROJECT_ROOT / "data" / "01_도서관_이용안내.pdf"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# ── 임베딩 · 저장소 ──
EMBED_MODEL = "text-embedding-3-small"

# 실행 위치와 관계없이 같은 폴더에 저장
INDEX_PATH = BASE / "faiss_index_library"

# ── 검색 ──
TOP_K = 5

# 초기 실습용 값입니다.
# 검색 로그를 보고 문서에 맞게 조정하세요.
MIN_SCORE = -0.1

# ── 생성 ──
LLM_MODEL = "gpt-4o-mini"
TEMPERATURE = 0

# ── 메시지 ──
MSG_NO_DOC = "확인할 수 없습니다."
MSG_ERROR = "일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."