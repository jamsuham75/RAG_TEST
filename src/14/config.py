# ═════════════════════════════════════════════
#  RAG 설정
#  최종 결정 : 2026-08-03
#  근거      : 14차시 벤치마크 (질문 20개 기준)
#              기준선 60% → 최종 90% (+30%p)
# ═════════════════════════════════════════════
# ── 문서 처리 ──
DOC_PATH      = "../../data/manual.pdf"
CHUNK_SIZE    = 500      # 500→300: +10%p, 토큰 33% 절감
CHUNK_OVERLAP = 50       # chunk_size의 10%
# ── 임베딩 · 저장소 ──
EMBED_MODEL   = "text-embedding-3-small"   # ⚠ 변경 시 인덱스 재생성 
INDEX_PATH    = "faiss_index"
# ── 검색 ──
TOP_K         = 5        # 3→5: +10%p (k=8은 노이즈로 하락) 
MIN_SCORE     = -1.0     # 9차시 실측값
SEARCH_TYPE   = "similarity"
# ── 생성 ──
LLM_MODEL     = "gpt-4o-mini"
TEMPERATURE   = 0
PROMPT_VER    = "v3"     # v2→v3: +10%p, 토큰 증가 없음
# ── 실험 기록 ──
# | 실험   | 설정                  | 정답률 | 토큰 | 
# # | 기준선 | chunk500 k3 v2        |  60%  |  840 | 
# # | 1차    | chunk300 k3 v2        |  70%  |  560 | 
# # | 2차    | chunk300 k5 v2        |  80%  |  890 | 
# # | 3차    | chunk300 k5 v3 ★최종  |  90%  |  890 |