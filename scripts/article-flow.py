#!/usr/bin/env python3
"""文章生产Flow状态管理工具"""

import json
import sys
from datetime import datetime
from pathlib import Path

STATE_DIR = Path.home() / ".openclaw" / "workspace" / "data" / "article-flow"
STATE_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE = STATE_DIR / "state.json"


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return None


def save_state(state):
    state["updated_at"] = datetime.now().isoformat()
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2))


def create(topic, angle=""):
    flow_id = f"flow-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    slug = topic.replace(" ", "-").lower()[:30]
    state = {
        "id": flow_id,
        "topic": topic,
        "angle": angle,
        "status": "collecting",
        "step": 1,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "files": {
            "materials": f"data/articles/{slug}-materials.md",
            "article": f"data/articles/{slug}-final.md",
            "cover": f"data/articles/imgs/{slug}-cover.png",
        },
        "media_id": None,
        "errors": [],
    }
    save_state(state)
    print(json.dumps(state, ensure_ascii=False, indent=2))


def advance(step_name):
    status_map = {
        "1": ("collecting", 1),
        "2": ("writing", 2),
        "3": ("cover", 3),
        "4": ("publishing", 4),
        "done": ("done", 5),
    }
    state = load_state()
    if not state:
        print("ERROR: No active flow")
        sys.exit(1)

    if step_name in status_map:
        state["status"], state["step"] = status_map[step_name]
    save_state(state)
    print(f"Flow {state['id']} → step {state['step']} ({state['status']})")


def fail(error_msg):
    state = load_state()
    if not state:
        print("ERROR: No active flow")
        sys.exit(1)
    state["status"] = "failed"
    state["errors"].append(f"{datetime.now().isoformat()}: {error_msg}")
    save_state(state)
    print(f"Flow FAILED: {error_msg}")


def show():
    state = load_state()
    if not state:
        print("No active flow")
        return
    print(json.dumps(state, ensure_ascii=False, indent=2))


def main():
    if len(sys.argv) < 2:
        print("Usage: article-flow.py <create|advance|fail|show> [args]")
        print("  create <topic> [angle]   - 创建新Flow")
        print("  advance <1|2|3|4|done>   - 推进到下一步")
        print("  fail <error_msg>         - 标记失败")
        print("  show                     - 查看当前状态")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "create":
        topic = sys.argv[2] if len(sys.argv) > 2 else "未命名"
        angle = sys.argv[3] if len(sys.argv) > 3 else ""
        create(topic, angle)
    elif cmd == "advance":
        advance(sys.argv[2])
    elif cmd == "fail":
        fail(" ".join(sys.argv[2:]))
    elif cmd == "show":
        show()
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
