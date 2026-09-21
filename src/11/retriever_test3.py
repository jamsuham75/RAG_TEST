import os
import sys
import warnings
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '10'))
from indexer import get_store

warnings.filterwarnings("ignore", message="Relevance scores must be between 0 and 1")

store = get_store()
QUESTION = "환불과 교환은 어떻게 다른가요?"

def show(name, retriever):
    docs = retriever.invoke(QUESTION)
    print(f"■ {name}  ({len(docs)}개)")
    for d in docs:
        preview = d.page_content[:55].replace("\n", " ")         
        print(f"   p.{d.metadata['page_no']}  {preview}...")     
        print()

# ① 기본 유사도 검색
show("similarity k=3",
     store.as_retriever(search_kwargs={"k": 3}))

# ② MMR — 다양성 확보
show("MMR k=3 fetch_k=10",
     store.as_retriever(search_type="mmr",
         search_kwargs={"k": 3, "fetch_k": 10}))

# ③ k값에 따른 점수 비교 분석
print("\n" + "=" * 58)
print("k값에 따른 유사도 점수 비교")
print("=" * 58 + "\n")

def compare_k(question, ks=(1, 3, 5)):
    print(f"질문: {question}")
    print("=" * 58)

    for k in ks:
        pairs = store.similarity_search_with_relevance_scores(question, k=k)
        scores = [s for _, s in pairs]
        low = sum(1 for s in scores if s < 0.1)

        print(f"k={k:<3} 점수={[round(float(s), 3) for s in scores]}")
        print(f"     기준 미달(0.1) 조각: {low}개")
        print()

compare_k("환불은 며칠 이내인가요?")
compare_k("환불과 교환은 어떻게 다른가요?")

# ④ 메타데이터 필터링 ← 여기부터 추가
print("\n" + "=" * 58)
print("메타데이터 필터링")
print("=" * 58 + "\n")

# 특정 파일에서만 검색
show("filename 필터 - manual.pdf만",
     store.as_retriever(
         search_kwargs={
             "k": 3,
             "filter": {"filename": "manual.pdf"}
         }
     ))