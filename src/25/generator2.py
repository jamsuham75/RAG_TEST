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

    if not docs:
        return {
            "answer": config.MSG_NO_DOC,
            "insufficient": True,
            "has_citation": False,
            "log": ["생성: 근거 없음 - LLM 호출 생략"],
        }

    retries = state.get("retries", 0)
    reason = state.get("reason", "")

    context = build_context(docs)

    if retries > 0 and reason:
        chain = PROMPTS["retry"] | _llm | StrOutputParser()

        payload = {
            "context": context,
            "question": state.get("question", ""),
            "reason": reason,
        }
        prompt_type = "재시도 프롬프트"
    else:
        chain = _chain()

        payload = {
            "context": context,
            "question": state.get("question", ""),
        }
        prompt_type = "기본 프롬프트"

    try:
        answer = chain.invoke(payload)

    except Exception as e:
        return {
            "answer": config.MSG_ERROR,
            "insufficient": True,
            "has_citation": False,
            "gen_error": type(e).__name__,
            "log": [f"생성 오류: {type(e).__name__}"],
        }

    ok, msg = _check_citation(answer, len(docs))

    return {
        "answer": answer,
        "insufficient": NO_INFO in answer,
        "has_citation": ok,
        "log": [
                f"생성: {prompt_type}, "
                f"{len(answer)}자, {msg}"
            ],
    }
    
if __name__ == "__main__":
    from retriever import retriever_node

    question = "환불 방법과 수수료를 알려주세요"

    # 1단계: 검색
    state = {
        "question": question,
        "query": question,
        "retries": 0,
        "reason": "",
    }

    state.update(retriever_node(state))

    # 2단계: 첫 번째 생성
    result1 = generator_node(state)

    print("\n[1회차 결과]")
    print(result1["answer"])
    print(result1["log"])

    # 첫 번째 결과를 State에 반영
    state.update(result1)

    # 실제로는 Verifier가 아래 값을 기록함
    state["retries"] = 1
    state["reason"] = "답변을 1문장으로 줄이세요"

    # 3단계: 피드백을 반영한 재생성
    result2 = generator_node(state)

    print("\n[2회차 결과]")
    print(result2["answer"])
    print(result2["log"])