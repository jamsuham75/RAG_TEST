import os
import sys

from graph27 import app

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "18"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "19"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "25"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "26"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "24"))

from langgraph.graph import StateGraph, START, END

from graph_state import RAGState
from graph_state2 import make_initial_state

from retriever import retriever_node
from generator import generator_node
from verifier import verifier_node
from fallback import fallback_node

import config


MAX_RETRY = getattr(config, "MAX_RETRY", 2)


q = "환불 방법과 대표이사를 알려주세요"

for step in app.stream(
    make_initial_state(q),
    {"recursion_limit": 25},
):
    for node, update in step.items():
        # log를 제외한 State 변경 키만 출력
        keys = [
            key
            for key in update.keys()
            if key != "log"
        ]

        print(f"[{node}] {keys}")

        for line in update.get("log", []):
            print(f"        {line}")