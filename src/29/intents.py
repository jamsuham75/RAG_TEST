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
    """
    간단한 사칙연산 질문을 처리합니다.
    """

    expr = state.get("question", "").strip()

    # 끝에 =, ?가 있으면 제거
    expr = expr.rstrip("=?").strip()

    try:
        # 안전을 위해 허용된 문자만 검사
        if not re.fullmatch(r"[\d\s+\-*/().,]+", expr):
            raise ValueError("허용되지 않은 계산식")

        # 쉼표 제거
        clean_expr = expr.replace(",", "")

        # 계산
        result = eval(
            clean_expr,
            {"__builtins__": {}},
            {}
        )

        return {
            "answer": f"{expr} = {result}",
            "grade": "pass",
            "reason": "계산식 직접 처리",
            "log": [f"계산: {expr} = {result}"],
        }

    except Exception as e:

        return {
            "answer": "계산식을 처리하지 못했습니다.",
            "grade": "giveup",
            "reason": f"계산 오류: {type(e).__name__}",
            "log": [
                f"계산 오류({type(e).__name__})"
            ],
        }
    
def scope_node(state) -> dict:
    return {
        "answer": ("죄송합니다. 저는 사내 문서에 관한 질문에만 "
                   "답변할 수 있습니다.\n"
                   "문서와 관련된 내용을 물어봐 주세요."),
        "grade": "pass",
        "log": ["scope: 범위 밖 안내"],     
}