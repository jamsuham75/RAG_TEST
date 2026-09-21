import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '10'))

from indexer import get_store          # 10차시 함수

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
         search_kwargs={"k": 3, "fetch_k": 10,                         
                        "lambda_mult": 0.5}))