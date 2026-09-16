import warnings
from retrieve import retrieve_node
from generate import generate_node
from fallback import fallback_node

# ✅ 경고 메시지 모두 제거
warnings.filterwarnings('ignore')

def manual_run(question: str):
    # 그래프 없이 손으로 노드를 이어본다
    state = {"question": question, "query": question,              
             "retries": 0, "log": [], "tried_queries": []}
    # ① 검색
    upd = retrieve_node(state)
    state = {**state, **upd, "log": state["log"] + upd["log"]}
    # ② 분기 (나중에 Edge가 될 부분)
    if state["retrieval_ok"]:
        upd = generate_node(state)
    else:
        upd = fallback_node(state)
    state = {**state, **upd, "log": state["log"] + upd["log"]}     
    
    return state

for q in ["환불은 며칠 이내인가요?", "대표이사 이름은?"]:     
    s = manual_run(q)
    print("Q:", q)
    print("A:", s["answer"][:80])     
    for line in s["log"]:         
        print("   ", line)
    print("-" * 55)