# backend/services/lighthouse_runner.py

"""
Lighthouse runner service.

Provides production-grade Lighthouse observability:
- Run count
- Execution duration
- Active run gauge
- Timeout/failure/invalid JSON classification
- Structured logs for incident debugging

URLs are logged, but never used as Prometheus labels.
"""

from __future__ import annotations

import json
import subprocess
from typing import Any

import structlog

from backend.core.metrics import track_lighthouse_duration

logger = structlog.get_logger(__name__)

LIGHTHOUSE_TIMEOUT_SECONDS = 120


def run_lighthouse_audit(url: str) -> dict[str, Any]:
    """
    Execute Lighthouse for a target URL.

    Args:
        url: Website URL to audit.

    Returns:
        Parsed Lighthouse JSON output.
    """
    logger.info(
        "Lighthouse audit started",
        url=url,
        timeout_seconds=LIGHTHOUSE_TIMEOUT_SECONDS,
    )

    with track_lighthouse_duration() as metrics:
        try:
            completed = subprocess.run(
                [
                    "lighthouse",
                    url,
                    "--output=json",
                    "--quiet",
                    "--chrome-flags=--headless --no-sandbox",
                ],
                check=True,
                capture_output=True,
                text=True,
                timeout=LIGHTHOUSE_TIMEOUT_SECONDS,
            )

            result = json.loads(completed.stdout)

            metrics["status"] = "success"

            logger.info(
                "Lighthouse audit completed",
                url=url,
            )

            return result

        except subprocess.TimeoutExpired as exc:
            metrics["status"] = "timeout"

            logger.exception(
                "Lighthouse audit timed out",
                url=url,
                timeout_seconds=LIGHTHOUSE_TIMEOUT_SECONDS,
                failure_type=exc.__class__.__name__,
            )

            raise

        except subprocess.CalledProcessError as exc:
            metrics["status"] = "failure"

            logger.exception(
                "Lighthouse audit process failed",
                url=url,
                returncode=exc.returncode,
                stderr=exc.stderr,
                failure_type=exc.__class__.__name__,
            )

            raise

        except json.JSONDecodeError as exc:
            metrics["status"] = "invalid_json"

            logger.exception(
                "Lighthouse returned invalid JSON",
                url=url,
                failure_type=exc.__class__.__name__,
            )

            raise

        except Exception as exc:
            metrics["status"] = "failure"

            logger.exception(
                "Unexpected Lighthouse failure",
                url=url,
                failure_type=exc.__class__.__name__,
            )

            raise
