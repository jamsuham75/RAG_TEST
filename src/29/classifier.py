import os
import sys
import re

# ============================================================
# 다른 차시의 파일을 import하기 위한 경로 설정
# ============================================================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

sys.path.insert(0, SRC_DIR)
sys.path.insert(0, os.path.join(CURRENT_DIR, "..", "25"))
sys.path.insert(0, os.path.join(CURRENT_DIR, "..", "13"))
sys.path.insert(0, os.path.join(CURRENT_DIR, "..", "24"))


import config
from generator import _llm
from prompts import CLASSIFY_PROMPT
from langchain_core.output_parsers import StrOutputParser


# ============================================================
# 분류에 사용할 단어들
# ============================================================

GREETING_WORDS = [
    "안녕", "반가", "하이", "헬로",
    "고마", "감사", "수고", "잘 부탁"
]

OUT_OF_SCOPE_WORDS = [
    "날씨", "주가", "환율", "로또",
    "뉴스", "맛집", "영화", "축구"
]

CALC_PATTERN = re.compile(r"^[\d\s+\-*/().,]+[=?]?$")


# ============================================================
# 1차 분류 : 규칙으로 판단
# ============================================================

def rule_classify(question):

    question = question.strip()


    # 질문이 비어 있는 경우
    if question == "":
        return "scope"


    # ---------------------------------------------
    # 1. 인사말인지 확인
    # ---------------------------------------------
    if len(question) <= 20:

        for word in GREETING_WORDS:
            if word in question:
                return "greeting"


    # ---------------------------------------------
    # 2. 계산식인지 확인
    # ---------------------------------------------
    has_operator = False

    for op in "+-*/":
        if op in question:
            has_operator = True
            break

    if CALC_PATTERN.match(question) and has_operator:
        return "calc"


    # ---------------------------------------------
    # 3. 문서 범위 밖 질문인지 확인
    # ---------------------------------------------
    for word in OUT_OF_SCOPE_WORDS:
        if word in question:
            return "scope"


    # 규칙으로 판단하지 못함
    return None


# ============================================================
# 2차 분류 : LLM 사용
# ============================================================

classify_chain = CLASSIFY_PROMPT | _llm | StrOutputParser()


# ============================================================
# LangGraph에서 사용하는 분류 노드
# ============================================================

def classifier_node(state):

    question = state.get("question", "")


    # --------------------------------------------------------
    # 1단계 : 규칙으로 분류
    # --------------------------------------------------------
    intent = rule_classify(question)

    if intent is not None:
        return {
            "intent": intent,
            "log": [f"분류(규칙): {intent}"]
        }


    # --------------------------------------------------------
    # 2단계 : LLM 분류를 사용하지 않는 경우
    # --------------------------------------------------------
    if config.USE_LLM_CLASSIFY == False:

        return {
            "intent": "document",
            "log": ["분류: 기본값 document"]
        }


    # --------------------------------------------------------
    # 3단계 : LLM에게 분류 요청
    # --------------------------------------------------------
    try:

        result = classify_chain.invoke({
            "question": question
        })

        intent = result.strip().lower()


        # 이상한 결과가 나오면 document로 처리
        if intent not in [
            "greeting",
            "calc",
            "scope",
            "document"
        ]:
            intent = "document"


    except Exception:

        intent = "document"


    return {
        "intent": intent,
        "log": [f"분류(LLM): {intent}"]
    }