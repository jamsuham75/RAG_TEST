import re


# ============================================================
# 1. 인사말 처리 노드
# ============================================================
def greeting_node(state):

    answer = """
안녕하세요! 사내 문서에 관한 질문을 도와드립니다.
예: 환불 규정, 휴가 신청 방법, 고객센터 운영 시간 등
"""

    return {
        "answer": answer.strip(),
        "grade": "pass",
        "log": ["인사말 응답"]
    }


# ============================================================
# 2. 계산 처리 노드
# ============================================================
def calc_node(state):

    # 사용자가 입력한 질문 가져오기
    question = state.get("question", "")

    # 앞뒤 공백 제거
    expr = question.strip()

    # 마지막의 = 또는 ? 제거
    expr = expr.rstrip("=?").strip()


    # 계산식에 사용할 수 없는 문자가 있는지 검사
    if not re.fullmatch(r"[\d\s+\-*/().,]+", expr):

        return {
            "answer": "계산식을 처리하지 못했습니다.",
            "grade": "giveup",
            "reason": "허용되지 않은 문자가 있습니다.",
            "log": ["계산 실패"]
        }


    try:
        # 1,000 + 2,000 같은 경우 쉼표 제거
        clean_expr = expr.replace(",", "")

        # 실제 계산
        result = eval(clean_expr)

        return {
            "answer": f"{expr} = {result}",
            "grade": "pass",
            "reason": "계산 완료",
            "log": [f"계산 완료: {expr} = {result}"]
        }

    except:

        return {
            "answer": "계산식을 처리하지 못했습니다.",
            "grade": "giveup",
            "reason": "계산 중 오류 발생",
            "log": ["계산 실패"]
        }


# ============================================================
# 3. 문서 범위 밖 질문 처리 노드
# ============================================================
def scope_node(state):

    answer = """
죄송합니다.
저는 사내 문서에 관한 질문에만 답변할 수 있습니다.
문서와 관련된 내용을 물어봐 주세요.
"""

    return {
        "answer": answer.strip(),
        "grade": "pass",
        "log": ["문서 범위 밖 질문"]
    }