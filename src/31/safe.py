import functools
import traceback


def safe_node(default_updates=None, name=None):
    # 노드에서 예외가 나도 그래프가 중단되지 않게 감싼다
    def deco(fn):
        node_name = name or fn.__name__

        @functools.wraps(fn)
        def wrapper(state):
            try:
                return fn(state)

            except Exception as e:
                err = f"{type(e).__name__}: {str(e)[:80]}"

                print(f"[ERROR] {node_name}: {err}")
                print(traceback.format_exc()[:400])

                updates = dict(default_updates or {})
                updates.setdefault("node_error", err)
                updates.setdefault(
                    "log",
                    [f"{node_name} 오류: {err}"]
                )

                return updates

        return wrapper

    return deco