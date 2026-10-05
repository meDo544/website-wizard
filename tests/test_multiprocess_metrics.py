import os
import subprocess
import sys

from prometheus_client import multiprocess


def test_multiprocess_generation_metric_is_scraped(tmp_path):
    env = os.environ.copy()
    env["PROMETHEUS_MULTIPROC_DIR"] = str(tmp_path)
    code = (
        "from backend.core.metrics import "
        "GENERATION_QUALITY_GATE_TOTAL; "
        "GENERATION_QUALITY_GATE_TOTAL.labels(decision=\"pass\").inc()"
    )
    subprocess.run([sys.executable, "-c", code], env=env, check=True)

    registry = __import__("prometheus_client").CollectorRegistry()
    multiprocess.MultiProcessCollector(registry, path=str(tmp_path))
    output = __import__("prometheus_client").generate_latest(registry).decode()

    assert "website_wizard_generation_quality_gate_total" in output
    assert "decision=\"pass\"" in output


def test_worker_shutdown_marks_process_dead(monkeypatch):
    from backend.tasks import celery_metrics

    calls = []
    monkeypatch.setattr(
        celery_metrics.multiprocess,
        "mark_process_dead",
        lambda pid: calls.append(pid),
    )

    celery_metrics.celery_worker_process_shutdown(pid=43210)

    assert calls == [43210]
