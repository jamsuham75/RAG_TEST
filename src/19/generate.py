import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
import config
import os
import sys
import warnings
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '13'))

from prompts import PROMPTS

load_dotenv()

_chain = (PROMPTS[config.PROMPT_VER]
          | ChatOpenAI(model=config.LLM_MODEL,                        
                       temperature=config.TEMPERATURE)
          | StrOutputParser())

NO_INFO = "자료에서 확인할 수 없습니다"

def _build_context(docs):
    return "\n\n---\n\n".join(
        f"[{i}] {d.metadata['filename']} p.{d.metadata['page_no']}\n"         
        f"{d.page_content}"
        for i, d in enumerate(docs, 1))

def generate_node(state: dict) -> dict:
    # 생성만 담당한다.
    docs = state.get("documents") or []
    if not docs:
        return {"answer": config.MSG_NO_DOC,
                "insufficient": True,
                "has_citation": False,
                "log": ["[generate] 근거 없음 — 생성 생략"]}
        
    answer = _chain.invoke({"context": _build_context(docs),                             
                            "question": state["question"]})
    
    nums  = [int(n) for n in re.findall(r"\[(\d+)\]", answer)]     
    cited = bool(nums) and all(1 <= n <= len(docs) for n in nums)
    
    return {
        "answer":       answer,
        "insufficient": NO_INFO in answer,
        "has_citation": cited,
        "log":          [f"[generate] {len(answer)}자 생성 "                          
                         f"(인용 {'정상' if cited else '미확인'})"],     
        }
if __name__ == "__main__":
    from retrieve import retrieve_node
    s = {"question": "환불은 며칠 이내인가요?"}     
    s.update(retrieve_node(s))          # 검색 먼저     
    print(generate_node(s)["answer"])   # 생성 테스트