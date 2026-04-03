import os
import json
from datetime import datetime
from typing import Dict, List


# --------------------------------------------------
# BASE DIRECTORY (anchored to project root)
# --------------------------------------------------

BASE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "audits"
)


# --------------------------------------------------
# UTILITIES
# --------------------------------------------------

def safe_url_key(url: str) -> str:
    """
    Convert URL into a filesystem-safe key.
    """
    return (
        url.replace("https://", "")
           .replace("http://", "")
           .replace("/", "_")
           .replace(":", "")
    )


# --------------------------------------------------
# SAVE AUDIT
# --------------------------------------------------

def save_audit(audit: Dict, url: str, stage: str) -> str:
    """
    Save audit JSON to disk under:
    data/audits/{stage}/
    """

    if stage not in ["before", "after"]:
        raise ValueError("Stage must be 'before' or 'after'")

    url_key = safe_url_key(url)

    stage_dir = os.path.join(BASE_DIR, stage)
    os.makedirs(stage_dir, exist_ok=True)

    # Windows-safe timestamp
    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")

    filename = f"{url_key}_{timestamp}.json"
    filepath = os.path.join(stage_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2)

    return filepath


# --------------------------------------------------
# LOAD LATEST AUDIT
# --------------------------------------------------

def load_latest(url: str, stage: str) -> Dict:
    """
    Load the most recent audit file for a given URL and stage.
    """

    if stage not in ["before", "after"]:
        raise ValueError("Stage must be 'before' or 'after'")

    url_key = safe_url_key(url)
    stage_dir = os.path.join(BASE_DIR, stage)

    if not os.path.exists(stage_dir):
        raise FileNotFoundError("Stage directory not found")

    files = [
        f for f in os.listdir(stage_dir)
        if f.startswith(url_key) and f.endswith(".json")
    ]

    if not files:
        raise FileNotFoundError("No audits found")

    # Because filename contains timestamp, alphabetical sort works
    latest = sorted(files)[-1]

    with open(os.path.join(stage_dir, latest), encoding="utf-8") as f:
        return json.load(f)


# --------------------------------------------------
# LOAD TIMELINE
# --------------------------------------------------

def load_timeline(url: str) -> List[Dict]:
    """
    Load full audit history (before + after) for a URL.
    Returns structured timeline sorted newest first.
    """

    url_key = safe_url_key(url)
    timeline = []

    for stage in ["before", "after"]:
        stage_dir = os.path.join(BASE_DIR, stage)

        if not os.path.exists(stage_dir):
            continue

        for filename in os.listdir(stage_dir):
            if filename.startswith(url_key) and filename.endswith(".json"):

                filepath = os.path.join(stage_dir, filename)

                with open(filepath, encoding="utf-8") as f:
                    data = json.load(f)

                timestamp = filename.replace(
                    f"{url_key}_", ""
                ).replace(".json", "")

                timeline.append({
                    "stage": stage,
                    "timestamp": timestamp,
                    "score": data.get("score"),
                    "grade": data.get("grade")
                })

    # Sort newest first
    timeline.sort(key=lambda x: x["timestamp"], reverse=True)

    return timeline
