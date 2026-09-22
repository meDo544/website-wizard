import threading
from uuid import uuid4

import pytest

from backend.db.session import SessionLocal
from backend.models.generated_sites import GeneratedSite
from backend.tasks.website_generation import (
    claim_generation_lease,
    utc_now,
)


@pytest.mark.integration
def test_only_one_worker_can_claim_generation_lease():
    website_id = uuid4()
    worker_a_attempt_id = uuid4()
    worker_b_attempt_id = uuid4()

    setup_db = SessionLocal()

    try:
        setup_db.add(
            GeneratedSite(
                id=website_id,
                prompt=(
                    "Atomic generation lease "
                    "integration contract."
                ),
                generation_status="queued",
            )
        )
        setup_db.commit()
    finally:
        setup_db.close()

    worker_a_db = SessionLocal()
    worker_b_db = SessionLocal()

    worker_a_reached_commit = threading.Event()
    allow_worker_a_commit = threading.Event()
    worker_b_started = threading.Event()
    worker_b_finished = threading.Event()

    results = {}
    errors = {}

    original_a_commit = worker_a_db.commit

    def paused_a_commit():
        worker_a_reached_commit.set()

        if not allow_worker_a_commit.wait(
            timeout=10
        ):
            raise TimeoutError(
                "Timed out waiting to release "
                "worker A commit."
            )

        original_a_commit()

    worker_a_db.commit = paused_a_commit

    def worker_a():
        try:
            results["a"] = claim_generation_lease(
                db=worker_a_db,
                website_id=str(website_id),
                now=utc_now(),
                attempt_id=worker_a_attempt_id,
            )
        except Exception as exc:
            errors["a"] = exc

    def worker_b():
        try:
            worker_b_started.set()

            results["b"] = claim_generation_lease(
                db=worker_b_db,
                website_id=str(website_id),
                now=utc_now(),
                attempt_id=worker_b_attempt_id,
            )
        except Exception as exc:
            errors["b"] = exc
        finally:
            worker_b_finished.set()

    thread_a = threading.Thread(
        target=worker_a,
        daemon=True,
    )

    thread_b = threading.Thread(
        target=worker_b,
        daemon=True,
    )

    try:
        thread_a.start()

        assert worker_a_reached_commit.wait(
            timeout=10
        ), (
            "Worker A never reached its lease "
            "commit boundary."
        )

        thread_b.start()

        assert worker_b_started.wait(
            timeout=10
        ), (
            "Worker B never started its claim."
        )

        # A still owns the uncommitted row update.
        # B must therefore remain blocked rather than
        # successfully claiming the same lease.
        assert not worker_b_finished.wait(
            timeout=0.5
        ), (
            "Worker B finished before worker A "
            "committed; row serialization was not "
            "observed."
        )

        allow_worker_a_commit.set()

        thread_a.join(
            timeout=10
        )
        thread_b.join(
            timeout=10
        )

        assert not thread_a.is_alive()
        assert not thread_b.is_alive()

        assert errors == {}

        assert results == {
            "a": True,
            "b": False,
        }

        verification_db = SessionLocal()

        try:
            website = (
                verification_db
                .query(GeneratedSite)
                .filter(
                    GeneratedSite.id
                    == website_id
                )
                .one()
            )

            assert (
                website.generation_status
                == "generating"
            )

            assert (
                website.generation_started_at
                is not None
            )

            assert (
                website.generation_attempt_id
                == worker_a_attempt_id
            )

            assert (
                website.generation_attempt_id
                != worker_b_attempt_id
            )
        finally:
            verification_db.close()

    finally:
        allow_worker_a_commit.set()

        thread_a.join(
            timeout=2
        )
        thread_b.join(
            timeout=2
        )

        worker_a_db.close()
        worker_b_db.close()

        cleanup_db = SessionLocal()

        try:
            (
                cleanup_db
                .query(GeneratedSite)
                .filter(
                    GeneratedSite.id
                    == website_id
                )
                .delete(
                    synchronize_session=False
                )
            )
            cleanup_db.commit()
        finally:
            cleanup_db.close()
