import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
import config
from indexer import get_store
from prompts import PROMPTS

load_dotenv()

_store = get_store()

_llm   = ChatOpenAI(model=config.LLM_MODEL,
                    temperature=config.TEMPERATURE)

_chain = PROMPTS[config.PROMPT_VER] | _llm | StrOutputParser() 

def _search(question, k=None):
    k = k or config.TOP_K
    pairs = _store.similarity_search_with_relevance_scores(
        question, k=k)
    # 기준(MIN_SCORE)을 넘는 것만 골라 담기
    docs = []
    for d, s in pairs:
        if s >= config.MIN_SCORE:
            docs.append(d)
    return docs

def _build_context(docs):
    parts = []

    for i, d in enumerate(docs, 1):
        filename = d.metadata.get("filename", "unknown")
        page_no = d.metadata.get(
            "page_no",
            d.metadata.get("page", 0) + 1
        )

        parts.append(
            f"[{i}] {filename} p.{page_no}\n"
            f"{d.page_content}"
        )

    return "\n\n---\n\n".join(parts)

def ask(question: str, k: int = None) -> dict:
    # 외부에 노출되는 유일한 함수
    if not question or not question.strip():
        return {"answer": "질문을 입력해주세요.",
                "sources": [], "ok": False}
    try:
        docs = _search(question, k)
    except Exception as e:
        print("[검색 오류]", e)
        return {"answer": config.MSG_ERROR, "sources": [], "ok": False}   
      
    if not docs:
        return {"answer": config.MSG_NO_DOC, "sources": [], "ok": True}    
    try:
        answer = _chain.invoke({
            "context": _build_context(docs),                                 
            "question": question
            })
    except Exception as e:
        print("[생성 오류]", e)
        return {"answer": config.MSG_ERROR, "sources": [], "ok": False}  
       
    # 인용 번호 [1][2]... 를 뽑아 문서 개수 범위 안인지 확인
    found = re.findall(r"\[(\d+)\]", answer)
    nums = []
    for n in found:
        nums.append(int(n))
    cited = len(nums) > 0
    for n in nums:
        if n < 1 or n > len(docs):
            cited = False
    
    sources = []

    for d in docs:
        sources.append({
            "file": d.metadata.get("filename", "unknown"),
            "page": d.metadata.get(
                "page_no",
                d.metadata.get("page", 0) + 1
            )
        }) 
          
    return {"answer": answer, "sources": sources,             
            "cited": cited, "ok": True}