import re
import os
import sys
import warnings
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '11'))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser 
from retriever import search, build_context
from prompts import RAG_PROMPT_V3

load_dotenv()
llm    = ChatOpenAI(model="gpt-4o-mini", temperature=0)
_chain = RAG_PROMPT_V3 | llm | StrOutputParser()
NO_INFO = "자료에서 확인할 수 없습니다"

def ask(question, k=3, verbose=True):
    docs = search(question, k=k)
    
    # verbose 먼저 처리하고 시작
    if verbose:
        print("Q:", question)
    
    # docs가 없는 경우 처리
    if not docs:
        result = {
            "answer": "관련 자료를 찾지 못했습니다.",
            "sources": [],
            "cited": False
        }
        if verbose:
            print("A:", result["answer"])
            print("⚠️  검색 결과 없음")
            print("-" * 55)
        return result
    
    # docs가 있는 경우 (기존 코드)
    answer = _chain.invoke({
        "context": build_context(docs),
        "question": question
    })
    
    found = re.findall(r"\[(\d+)\]", answer)
    nums = [int(n) for n in found]
    
    cited = len(nums) > 0
    for n in nums:
        if n < 1 or n > len(docs):
            cited = False
    
    if verbose:
        print("A:", answer)
        pages = [f"p.{d.metadata['page_no']}" for d in docs]
        print("  ", pages)
        if not cited:
            print("⚠️  인용 검증 실패 — 확인 필요")
        print("-" * 55)
    
    sources = [d.metadata for d in docs]
    return {
        "answer": answer,
        "sources": sources,
        "cited": cited,
        "insufficient": NO_INFO in answer
    }

if __name__ == "__main__":
    ask("환불은 며칠 이내에 신청해야 하나요?")     
    ask("대표이사가 누구인가요?")
    ask("환불 방법과 수수료를 알려주세요")