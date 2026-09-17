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
from generator import build_context, _llm

from prompts import CLASSIFY_PROMPT
from langchain_core.output_parsers import StrOutputParser


GREETING_WORDS = [
    "안녕", "반가", "하이", "헬로",
    "고마", "감사", "수고", "잘 부탁"
]

CALC_PATTERN = re.compile(
    r"^[\d\s+\-*/().,]+[=?]?$"
)

OUT_OF_SCOPE = [
    "날씨", "주가", "환율", "로또", "뉴스",
    "맛집", "영화", "축구"
]


def _has_any(text, words):
    """목록의 단어 중 하나라도 포함되어 있으면 True"""
    for w in words:
        if w in text:
            return True
    return False


def _rule_classify(q: str) -> str:
    text = q.strip()

    if not text:
        return "scope"

    # 1차 분류: 짧은 인사말
    if len(text) <= 20 and _has_any(text, GREETING_WORDS):
        return "greeting"

    # 1차 분류: 순수 계산식
    has_op = False

    for op in "+-*/":
        if op in text:
            has_op = True
            break

    if CALC_PATTERN.match(text) and has_op:
        return "calc"

    # 1차 분류: 문서 범위 밖 주제
    if _has_any(text, OUT_OF_SCOPE):
        return "scope"

    # 판단하지 못함 → LLM으로 전달
    return ""


# 2차 LLM 분류 체인
_classify_chain = CLASSIFY_PROMPT | _llm | StrOutputParser()

VALID = {
    "greeting",
    "calc",
    "scope",
    "document"
}


def classifier_node(state) -> dict:
    q = state.get("question", "")

    # 1차: 규칙 기반 분류
    intent = _rule_classify(q)

    if intent:
        return {
            "intent": intent,
            "log": [f"분류(규칙): {intent}"]
        }

    # LLM 분류를 사용하지 않는 경우
    if not getattr(config, "USE_LLM_CLASSIFY", False):
        return {
            "intent": "document",
            "log": ["분류: 기본값 document"]
        }

    # 2차: LLM 분류
    try:
        raw = _classify_chain.invoke({
            "question": q
        }).strip().lower()

        intent = raw if raw in VALID else "document"

    except Exception as e:
        intent = "document"

        return {
            "intent": intent,
            "log": [
                f"분류 오류({type(e).__name__}) -> document"
            ]
        }

    return {
        "intent": intent,
        "log": [f"분류(LLM): {intent}"]
    }