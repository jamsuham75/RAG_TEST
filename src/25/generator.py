import os
import sys
import warnings

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

sys.path.insert(0, SRC_DIR)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '13'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '24'))
warnings.filterwarnings("ignore")

import re
import config
from prompts import PROMPTS
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser 
from dotenv import load_dotenv

load_dotenv()

NO_INFO = "자료에서 확인할 수 없습니다"

_llm = ChatOpenAI(model=config.LLM_MODEL,                   
                  temperature=config.TEMPERATURE)

def _chain(version=None):
    ver = version or config.PROMPT_VER
    return PROMPTS[ver] | _llm | StrOutputParser()

def build_context(docs):
    # 근거를 번호와 출처를 붙여 하나의 문자열로
    parts = []
    for i, d in enumerate(docs, 1):
        head = (f"[{i}] {d.metadata.get('filename','?')} "                 
                f"p.{d.metadata.get('page_no','?')}")
        parts.append(f"{head}\n{d.page_content}")
    return "\n\n---\n\n".join(parts)

def _check_citation(answer, n_docs):
    nums = [int(n) for n in re.findall(r"\[(\d+)\]", answer)]     
    if not nums:
        return False, "인용 없음"
    bad = []
    for n in nums:
        if n < 1 or n > n_docs:
            bad.append(n)
    if bad:
        return False, f"존재하지 않는 근거 번호 {bad}"     
    return True, f"인용 {len(nums)}건 정상"

def generator_node(state) -> dict:
    docs = state.get("documents") or []
    # 근거가 없으면 LLM을 부르지 않는다 (비용 절약)
    if not docs:
        return {"answer": config.MSG_NO_DOC,
                "insufficient": True,
                "has_citation": False,
                "log": ["생성: 근거 없음 - LLM 호출 생략"]}
    try:
        answer = _chain().invoke({
            "context":  build_context(docs),             
            "question": state["question"],
        })
    except Exception as e:
        return {"answer": config.MSG_ERROR,                 
                "insufficient": True,
                "has_citation": False,                 
                "gen_error": type(e).__name__,
                "log": [f"생성 오류: {type(e).__name__}"]}
        
    ok, msg = _check_citation(answer, len(docs))
    
    return {
        "answer":       answer,
        "insufficient": NO_INFO in answer,
        "has_citation": ok,
        "log": [f"생성: {len(answer)}자, {msg}"],
    }
    
if __name__ == "__main__":
    from retriever import retriever_node
    CASES = [
        "환불은 며칠 이내에 신청해야 하나요?",   # 정상
        "환불 방법과 수수료를 알려주세요",       # 일부만 있음
        "대표이사가 누구인가요?",                # 근거 없음
    ]
    
    for q in CASES:
        s = {"question": q, "query": q}         
        s.update(retriever_node(s))          # 검색
        r = generator_node(s)                # 생성
        
        print(f"\n{'='*55}")
        print(f"Q: {q}")
        print(f"근거 {len(s['documents'])}건")
        print(f"A: {r['answer'][:110]}")
        print(f"   부족신고={r['insufficient']} "
              f"인용정상={r['has_citation']}")         
        print(f"   {r['log'][0]}")