import time
import warnings
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter 
import os
import sys

# from yaml import warnings

# ✅ 경고 메시지 모두 제거
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '06'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '13'))

from ingest import load_documents
from prompts import PROMPTS
from dotenv import load_dotenv

load_dotenv()

emb = OpenAIEmbeddings(model="text-embedding-3-small")
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

DOCS = load_documents("../../data/manual.pdf")

_cache = {}

def make_store(chunk_size, overlap):
    key = (chunk_size, overlap)
    if key in _cache:
        return _cache[key]
    sp = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", " ", ""])
    chunks = sp.split_documents(DOCS)
    _cache[key] = FAISS.from_documents(chunks, emb)     
    print(f"   (인덱스 생성: chunk={chunk_size} 조각={len(chunks)})")     
    return _cache[key]


def build_context(docs):
    parts = []
    for i, d in enumerate(docs, 1):
        parts.append(f"[{i}] {d.page_content}")
    return "\n\n---\n\n".join(parts)


def run(name, chunk_size, overlap, k, min_score, version, tests):
    store = make_store(chunk_size, overlap)
    chain = PROMPTS[version] | llm | StrOutputParser()
    hit, tokens, t0 = 0, 0, time.time()
    fails = []
    
    for t in tests:
        pairs = store.similarity_search_with_relevance_scores(t["q"], k=k)
        # 기준(min_score)을 넘는 것만 골라 담기
        docs = []
        for d, s in pairs:
            if s >= min_score:
                docs.append(d)
        
        ctx = build_context(docs) if docs else "(자료 없음)"
        ans = chain.invoke({"context": ctx, "question": t["q"]})
        tokens += len(ctx) // 2  # 한글 대략 2자 = 1토큰
        
        # 정답 키워드 중 하나라도 답변에 들어있으면 정답
        ok = False
        for key in t["keys"]:
            if key in ans:
                ok = True
                break
        
        if ok:
            hit += 1
        else:
            fails.append(t["q"])
    
    sec = time.time() - t0
    rate = hit / len(tests) * 100
    print(f"{name:<12} chunk={chunk_size:<5} k={k:<3} "
          f"{version:<3} | 정답 {hit:>2}/{len(tests)} ({rate:>3.0f}%) "
          f"| 평균토큰 {tokens//len(tests):>5} | {sec:>4.0f}초")
    
    return {"name": name, "rate": rate,
            "tokens": tokens // len(tests), "fails": fails}


# ============================================================================
# 테스트 케이스
# ============================================================================
TESTS = [
    {"q": "환불은 며칠 이내인가요?",  "keys": ["7일", "일주일"]},     
    {"q": "교환 기간은?",             "keys": ["30일"]},
    {"q": "대표이사 이름은?",         "keys": ["확인할 수 없"]},     
    # ... 20개까지
]

print("■ 기준선 측정")
print("-" * 78)
# baseline = run("기준선", 500, 50, 3, -1.0, "v2", TESTS)

print("="*80)
print("1️⃣  chunk_size 비교 (k=3, v2 고정)")
print("="*80)
run("chunk_500", 500, 50, 3, -1.0, "v2", TESTS)
run("chunk_1024", 1024, 100, 3, -1.0, "v2", TESTS)
run("chunk_2048", 2048, 200, 3, -1.0, "v2", TESTS)

print("\n" + "="*80)
print("2️⃣  k값 비교 (chunk=500, v2 고정)")
print("="*80)
run("k_3", 500, 50, 3, -1.0, "v2", TESTS)
run("k_5", 500, 50, 5, -1.0, "v2", TESTS)
run("k_10", 500, 50, 10, -1.0, "v2", TESTS)

print("\n" + "="*80)
print("3️⃣  프롬프트 버전 비교 (chunk=500, k=3 고정)")
print("="*80)
run("v1", 500, 50, 3, -1.0, "v1", TESTS)
run("v2", 500, 50, 3, -1.0, "v2", TESTS)
run("v3", 500, 50, 3, -1.0, "v3", TESTS)
