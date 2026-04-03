import os
import json
from datetime import datetime
from typing import List, Dict

BASE_DIR = os.path.join("data", "audits")


def _safe_url_key(url: str) -> str:
    return url.replace("https://", "").replace("http://", "").replace("/", "_")


def load_audit_timeline(url: str) -> List[Dict]:
    url_key = _safe_url_key(url)
    timeline = []

    for stage in ("before", "after"):
        stage_dir = os.path.join(BASE_DIR, stage)
        if not os.path.exists(stage_dir):
            continue

        for filename in os.listdir(stage_dir):
            if not filename.startswith(url_key):
                continue

            file_path = os.path.join(stage_dir, filename)

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Extract timestamp from filename
                parts = filename.replace(".json", "").split("_")
                timestamp_str = parts[-2] + "_" + parts[-1]
                timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")

                timeline.append({
                    "timestamp": timestamp.isoformat(),
                    "stage": stage,
                    "score": data.get("score"),
                    "grade": data.get("grade"),
                    "category_scores": data.get("category_scores", {}),
                })

            except Exception:
                continue

    # Sort chronologically
    timeline.sort(key=lambda x: x["timestamp"])

    return timeline
