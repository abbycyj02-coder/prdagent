from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.services.llm_service import chat_completion, current_model, llm_enabled


def main() -> None:
    if not llm_enabled():
        print("LLM 未启用：请先在 .env 中设置 OPENAI_API_KEY。")
        return

    text = chat_completion(
        [
            {"role": "system", "content": "你是一个简洁的连接测试助手。"},
            {"role": "user", "content": "请只回复：连接成功"},
        ]
    )
    print(f"模型：{current_model()}")
    print(f"响应：{text.strip()}")


if __name__ == "__main__":
    main()
