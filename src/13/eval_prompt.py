import os
import sys
import warnings
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '11'))

from retriever import search, build_context
from prompts import PROMPTS
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser 

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 12차시 과제에서 만든 질문 세트를 여기에
TESTS = [
    {"q": "환불은 며칠 이내인가요?",  "keys": ["7일", "일주일"]},     
    {"q": "교환 기간은?",             "keys": ["30일"]},
    {"q": "대표이사 이름은?",         "keys": ["확인할 수 없"]},     
    # ... 20개까지
]

def evaluate(version):
    chain = PROMPTS[version] | llm | StrOutputParser()
    hit, fails = 0, []
    for t in TESTS:
        docs = search(t["q"])
        ctx  = build_context(docs) if docs else "(자료 없음)"         
        ans  = chain.invoke({"context": ctx, "question": t["q"]})         
        # 정답 키워드 중 하나라도 들어있으면 정답
        ok = False
        for key in t["keys"]:
            if key in ans:
                ok = True
                break
        if ok:
            hit += 1
        else:
            fails.append(t["q"])
    rate = hit / len(TESTS) * 100
    print(f"[{version}] 정답 {hit}/{len(TESTS)} = {rate:.0f}%")     
    if fails:
        print("   실패:", ", ".join(fails[:5]))     
    return rate

print("■ 프롬프트 버전별 정답률") 

for v in ("v1", "v2", "v3"):     
    evaluate(v)