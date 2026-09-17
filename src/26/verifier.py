import os
import sys
import warnings

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
warnings.filterwarnings("ignore")

sys.path.insert(0, SRC_DIR)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '25'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '13'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '24'))

import json, re
import config
from prompts import JUDGE_PROMPT
from generator import build_context, _llm
from langchain_core.output_parsers import StrOutputParser

_judge = JUDGE_PROMPT | _llm | StrOutputParser()

def _parse_json(raw: str) -> dict:
    # 모델이 앞뒤에 말을 붙여도 { } 블록만 뽑아낸다
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        raise ValueError("JSON 블록을 찾을 수 없음")
    return json.loads(m.group())

def verifier_node(state) -> dict:
    docs   = state.get("documents") or []
    answer = state.get("answer", "")
    
    # ── 1차: 규칙 기반 (비용 0) ──
    if state.get("gen_error"):
        return {"grade": "giveup", "reason": "생성 오류 발생",                 
                "log": ["검증: 생성 오류로 중단"]}
    if state.get("insufficient"):
        return {"grade": "research", "reason": "근거 부족 자가신고",                 
                "log": ["검증(규칙): 근거 부족"]}
    if not state.get("has_citation"):
        return {"grade": "retry", "reason": "출처 번호가 없거나 유효하지 않음",                 
                "log": ["검증(규칙): 인용 불량"]}
    if len(answer.strip()) < 10:
        return {"grade": "retry", "reason": "답변이 너무 짧음",                 
                "log": ["검증(규칙): 답변 길이 부족"]}
    
    # ── 2차: LLM 심판 ──
    try:
        raw = _judge.invoke({             
            "context":  build_context(docs),             
            "question": state["question"],             
            "answer":   answer,
        })
        v = _parse_json(raw)    
    except Exception as e:
        # 심판이 실패하면 통과시킨다 (검증 때문에 서비스가 막히면 안 됨)         
        return {
            "grade": "pass",
            "reason": f"검증 불가({type(e).__name__}) - 통과 처리",
            "log": [f"검증 오류: {type(e).__name__}"]
        }
        
    grounded = bool(v.get("grounded"))
    relevant = bool(v.get("relevant"))
    reason   = str(v.get("reason", ""))[:200]
    
    if grounded and relevant:
        grade = "pass"
    elif not grounded:
        grade = "retry"        # 근거 이탈 → 다시 생성
    else:
        grade = "research"     # 관련성 부족 → 다시 검색
    return {"grade": grade, "reason": reason,
            "log": [f"검증(LLM): g={grounded} r={relevant} -> {grade}"]}
    
if __name__ == "__main__":
    from retriever import retriever_node
    
    q = "환불은 며칠 이내인가요?"
    s = {"question": q, "query": q}
    s.update(retriever_node(s))
    
    CASES = [
        # (설명, answer, insufficient, has_citation)
        ("정상 답변",
         "환불은 상품 수령 후 7일 이내에 신청하실 수 있습니다[1].",          
         False, True),
        
        ("환각 포함",
         "환불은 7일 이내입니다[1]. 수수료는 상품가의 10%입니다[1].",          
         False, True),
        
        ("동문서답",
         "고객센터는 평일 09시부터 18시까지 운영합니다[1].",          
         False, True),
        
        ("인용 없음",
         "환불은 7일 이내에 신청하시면 됩니다.",
         False, False),
        
        ("근거 부족 신고",
         "자료에서 확인할 수 없습니다.",
         True, False),
    ]
    
    for desc, ans, insuf, cite in CASES:         
        s2 = dict(s, answer=ans, insufficient=insuf,
                  has_citation=cite)
        r = verifier_node(s2)
        print(f"\n[{desc}]")
        print(f"  판정: {r['grade']}")
        print(f"  이유: {r['reason'][:70]}")
        