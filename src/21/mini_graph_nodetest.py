from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, START, END 
import operator

class MiniState(TypedDict):
    question: str
    documents: List[str]
    answer: str
    grade: str
    retries: int
    log: Annotated[List[str], operator.add]

def init(q: str) -> MiniState:
    return {"question": q, "documents": [], "answer": "",
            "grade": "", "retries": 0, "log": []}
    
def retrieve(state: MiniState):
    # 질문에 '없는'이 들어가면 검색 실패로 흉내
    q = state["question"]
    docs = [] if "없는" in q else ["조각A", "조각B", "조각C"]     
    print(f"   → retrieve: {len(docs)}건")
    return {"documents": docs, "log": [f"검색 {len(docs)}건"]}

def generate(state: MiniState):
    n = len(state["documents"])
    # 재시도할수록 답변이 좋아지는 상황을 흉내
    quality = "좋은" if state["retries"] >= 1 else "부실한"     
    print(f"   → generate: {quality} 답변")
    return {"answer": f"{n}건 근거로 만든 {quality} 답변",             
            "log": [f"생성({quality})"]}

def verify(state: MiniState):
    ok = "좋은" in state["answer"]
    print(f"   → verify: {'통과' if ok else '재시도'}")     
    return {"grade": "pass" if ok else "retry",             
            "log": ["검증 " + ("통과" if ok else "실패")]}

def bump(state: MiniState):
    n = state["retries"] + 1
    print(f"   → bump: {n}회차")
    return {"retries": n, "log": [f"재시도 {n}"]}

def fallback(state: MiniState):
    print("   → fallback")
    return {"answer": "자료를 찾지 못했습니다.",             
            "grade": "giveup", "log": ["fallback"]}    

if __name__ == "__main__":
    print("■ 노드 단독 테스트")
    s = init("환불 규정은?")
    print("1) retrieve:", retrieve(s))
    
    s["documents"] = ["조각A", "조각B"]     
    print("2) generate:", generate(s))
    
    s["answer"] = "부실한 답변"     
    print("3) verify:  ", verify(s))
         
    print("4) bump:    ", bump(s))