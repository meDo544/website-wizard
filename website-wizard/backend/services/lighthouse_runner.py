import json
import subprocess
import tempfile
import os

def run_lighthouse(url: str) -> dict:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        output_path = tmp.name

    try:
        cmd = [
            "lighthouse",
            url,
            "--quiet",
            "--chrome-flags=--headless --no-sandbox --disable-gpu",
            "--output=json",
            f"--output-path={output_path}",
        ]
        subprocess.run(cmd, check=True)

        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        categories = data.get("categories", {})
        normalized = {
            "performance_score": int((categories.get("performance", {}).get("score") or 0) * 100),
            "seo_score": int((categories.get("seo", {}).get("score") or 0) * 100),
            "accessibility_score": int((categories.get("accessibility", {}).get("score") or 0) * 100),
            "best_practices_score": int((categories.get("best-practices", {}).get("score") or 0) * 100),
            "raw": data,
        }
        return normalized
    finally:
        if os.path.exists(output_path):
            os.remove(output_path)