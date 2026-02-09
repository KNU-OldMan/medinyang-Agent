import json
import re
from datetime import datetime
from typing import Any, Optional, Dict


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


def now_iso():
    return datetime.now().isoformat(timespec="seconds")

def normalize_metadata(
    *,
    source: str,
    domain: str = "unknown",
    title: str = "",
    query: str = "",
    fetched_at: Optional[str] = None,
    extra: Optional[Dict] = None,
) -> Dict:
    meta = {
        "source": source,          # 예: "google_serper" / "internal" / "kcdc"
        "domain": domain,          # 예: "kdca.go.kr"
        "title": title,            # 문서/페이지 제목(가능하면)
        "query": query,            # 검색 쿼리
        "fetched_at": fetched_at or now_iso(),
    }
    if extra:
        meta.update(extra)
    return meta