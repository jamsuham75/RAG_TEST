import re
import config

def greeting_node(state) -> dict:
    return {
        "answer": ("안녕하세요! 사내 문서에 관한 질문을 도와드립니다.\n"
                   "예: 환불 규정, 휴가 신청 방법, 고객센터 운영 시간 등"),         
        "grade": "pass",
        "log": ["greeting 응답"],
    }
    
def calc_node(state) -> dict:
    expr = state["question"].strip().rstrip("=?").strip()
    
    # 안전 검사: 숫자와 연산자만 허용 (eval 사용 시 필수)
    if not re.fullmatch(r"[\d\s\+\-\*/\(\)\.]+", expr):
        return {"answer": "계산할 수 없는 식입니다.",
                "grade": "pass", "log": ["calc: 형식 오류"]}
        try:
            result = eval(expr, {"__builtins__": {}}, {})
        except Exception:    
            return {"answer": "계산할 수 없는 식입니다.",                 
                "grade": "pass", "log": ["calc: 계산 실패"]}
    
    return {"answer": f"{expr} = {result}",
            "grade": "pass", "log": [f"calc: {result}"]}
    
def scope_node(state) -> dict:
    return {
        "answer": ("죄송합니다. 저는 사내 문서에 관한 질문에만 "
                   "답변할 수 있습니다.\n"
                   "문서와 관련된 내용을 물어봐 주세요."),
        "grade": "pass",
        "log": ["scope: 범위 밖 안내"],     
}