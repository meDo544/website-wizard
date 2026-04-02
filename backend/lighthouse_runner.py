import subprocess
import json


def run_lighthouse(url: str):

    try:
        result = subprocess.run(
            [
                "lighthouse",
                url,
                "--output=json",
                "--output-path=stdout",
                "--chrome-flags=--headless"
            ],
            capture_output=True,
            text=True
        )

        data = json.loads(result.stdout)

        return {
            "performance": data["categories"]["performance"]["score"],
            "seo": data["categories"]["seo"]["score"],
            "accessibility": data["categories"]["accessibility"]["score"],
            "best_practices": data["categories"]["best-practices"]["score"]
        }

    except Exception as e:

        return {
            "error": str(e)
        }
