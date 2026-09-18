import json
import time
import uuid
from pathlib import Path


LOG_PATH = Path("logs/queries.jsonl")
LOG_PATH.parent.mkdir(exist_ok=True)


def log_query(question, final_state, elapsed):

    scores = final_state.get("scores") or []

    # numpy.float32 등이 들어올 수 있으므로
    # 일반 Python float로 변환
    top_score = float(scores[0]) if scores else None

    record = {
        "id": str(uuid.uuid4())[:8],

        "ts": time.strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "question": question,

        "intent": final_state.get("intent"),

        "grade": final_state.get("grade"),

        "verified":
            final_state.get("grade") == "pass",

        "retries":
            final_state.get("retries", 0),

        "rewrites":
            final_state.get("rewrites", 0),

        "n_docs":
            len(final_state.get("documents", [])),

        # ★ float32 → float 변환
        "top_score": top_score,

        "fail_reason":
            final_state.get("fail_reason", ""),

        "fallback_kind":
            final_state.get("fallback_kind", ""),

        "node_error":
            final_state.get("node_error", ""),

        "elapsed":
            round(elapsed, 2),

        "answer_len":
            len(final_state.get("answer", "")),
    }

    with LOG_PATH.open(
        "a",
        encoding="utf-8"
    ) as f:

        f.write(
            json.dumps(
                record,
                ensure_ascii=False
            ) + "\n"
        )

    return record