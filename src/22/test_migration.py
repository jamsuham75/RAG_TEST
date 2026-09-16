import os
import sys
import warnings
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'rag_app'))

warnings.filterwarnings("ignore")

import rag           # 15차시 함수 버전
import graph         # 22차시 그래프 버전

TESTS = [
    "환불은 며칠 이내에 신청해야 하나요?",
    "교환 기간은 얼마인가요?",
    "고객센터 운영 시간은?",
    "대표이사가 누구인가요?",       # 문서에 없는 질문     "반품하고 싶은데 언제까지?",     # 표현 변경
    # ... 12차시 질문 세트 20개
]

same, diff = 0, []
for q in TESTS:
    a = rag.ask(q)["answer"]
    b = graph.ask(q)["answer"]

    if a.strip() == b.strip():
        same += 1
        print(f"✓ {q[:28]}")
    else:
        diff.append(q)
        print(f"✗ {q[:28]}")         
        print(f"    [함수] {a[:60]}...")         
        print(f"    [그래프] {b[:60]}...")
        
print(f"\n일치: {same}/{len(TESTS)}") 
if diff:
    print("불일치 질문:", diff)