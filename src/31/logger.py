import json
import os
import time


def log_query(question, state, elapsed):

    # logs 폴더가 없으면 생성
    os.makedirs("logs", exist_ok=True)

    # 저장할 내용
    record = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "question": question,
        "intent": state.get("intent", ""),
        "grade": state.get("grade", ""),
        "retries": state.get("retries", 0),
        "rewrites": state.get("rewrites", 0),
        "node_error": state.get("node_error", ""),
        "elapsed": round(elapsed, 2)
    }

    # 파일에 한 줄 추가
    with open("logs/queries.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return record