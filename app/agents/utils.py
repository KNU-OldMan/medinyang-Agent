import json
import re
from datetime import datetime
from typing import Any, Optional


def get_current_time_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def clean_and_parse_json(text: str) -> Optional[Any]:
    try:
        match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            text = match.group(1)
        else:
            match = re.search(r"(\{.*\})", text, re.DOTALL)
            if match:
                text = match.group(1)

        return json.loads(text)
    except Exception:
        return None
