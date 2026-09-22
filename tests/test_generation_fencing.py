from types import SimpleNamespace
from uuid import uuid4

import pytest

from backend.models.generated_sites import GeneratedSite


@pytest.mark.unit
def test_generated_site_exposes_generation_attempt_id():
    column = (
        GeneratedSite.__table__
        .columns
        .get("generation_attempt_id")
    )

    assert column is not None
    assert column.nullable is True


@pytest.mark.unit
def test_generation_lease_claim_persists_attempt_id(
    monkeypatch,
):
    from uuid import uuid4

    import backend.tasks.website_generation as task_module

    attempt_id = uuid4()
    captured = {}

    class FakeQuery:
        def filter(self, *args):
            return self

        def update(
            self,
            values,
            synchronize_session=None,
        ):
            captured["values"] = values
            captured["synchronize_session"] = (
                synchronize_session
            )
            return 1

    class FakeDB:
        def __init__(self):
            self.commit_count = 0
            self.rollback_count = 0

        def query(self, model):
            return FakeQuery()

        def commit(self):
            self.commit_count += 1

        def rollback(self):
            self.rollback_count += 1

    db = FakeDB()

    claimed = task_module.claim_generation_lease(
        db=db,
        website_id="website-id",
        now=task_module.utc_now(),
        attempt_id=attempt_id,
    )

    assert claimed is True

    assert (
        captured["values"][
            task_module.GeneratedSite
            .generation_attempt_id
        ]
        == attempt_id
    )

    assert (
        captured["synchronize_session"]
        is False
    )

    assert db.commit_count == 1
    assert db.rollback_count == 0


@pytest.mark.unit
def test_generation_task_supplies_unique_attempt_id_to_claim(
    monkeypatch,
):
    from uuid import UUID, uuid4

    import backend.tasks.website_generation as task_module

    website_id = uuid4()

    class Website:
        id = website_id
        generation_status = "queued"
        generation_started_at = None

    website = Website()

    class FakeQuery:
        def filter(self, *args):
            return self

        def first(self):
            return website

    class FakeDB:
        def __init__(self):
            self.closed = False

        def query(self, model):
            return FakeQuery()

        def close(self):
            self.closed = True

    db = FakeDB()
    captured = {}

    monkeypatch.setattr(
        task_module,
        "SessionLocal",
        lambda: db,
    )

    def fake_claim_generation_lease(
        *,
        db,
        website_id,
        now,
        attempt_id,
    ):
        captured["attempt_id"] = attempt_id
        return False

    monkeypatch.setattr(
        task_module,
        "claim_generation_lease",
        fake_claim_generation_lease,
    )

    task_module.generate_website_task(
        str(website_id),
        "test-business",
    )

    assert isinstance(
        captured["attempt_id"],
        UUID,
    )

    assert db.closed is True


@pytest.mark.unit
def test_generation_attempt_ownership_requires_matching_token():
    from uuid import uuid4

    import backend.tasks.website_generation as task_module

    attempt_id = uuid4()
    captured = {}

    class FakeQuery:
        def filter(self, *criteria):
            captured["criteria"] = criteria
            return self

        def first(self):
            return object()

    class FakeDB:
        def query(self, model):
            captured["model"] = model
            return FakeQuery()

    owned = task_module.generation_attempt_is_current(
        db=FakeDB(),
        website_id="website-id",
        attempt_id=attempt_id,
    )

    assert owned is True
    assert (
        captured["model"]
        is task_module.GeneratedSite
    )

    # id + generating status + attempt token
    # must all participate in the ownership predicate.
    assert len(captured["criteria"]) == 3


@pytest.mark.unit
def test_generation_attempt_ownership_rejects_stale_token():
    from uuid import uuid4

    import backend.tasks.website_generation as task_module

    class FakeQuery:
        def filter(self, *criteria):
            return self

        def first(self):
            return None

    class FakeDB:
        def query(self, model):
            return FakeQuery()

    owned = task_module.generation_attempt_is_current(
        db=FakeDB(),
        website_id="website-id",
        attempt_id=uuid4(),
    )

    assert owned is False


@pytest.mark.unit
def test_lock_generation_attempt_requires_token_and_row_lock():
    from uuid import uuid4

    import backend.tasks.website_generation as task_module

    attempt_id = uuid4()
    captured = {}

    class FakeQuery:
        def filter(self, *criteria):
            captured["criteria"] = criteria
            return self

        def with_for_update(self):
            captured["for_update"] = True
            return self

        def first(self):
            return object()

    class FakeDB:
        def query(self, model):
            captured["model"] = model
            return FakeQuery()

    locked = task_module.lock_generation_attempt(
        db=FakeDB(),
        website_id="website-id",
        attempt_id=attempt_id,
    )

    assert locked is True
    assert (
        captured["model"]
        is task_module.GeneratedSite
    )
    assert len(captured["criteria"]) == 3
    assert captured["for_update"] is True


@pytest.mark.unit
def test_lock_generation_attempt_rejects_stale_token():
    from uuid import uuid4

    import backend.tasks.website_generation as task_module

    captured = {}

    class FakeQuery:
        def filter(self, *criteria):
            return self

        def with_for_update(self):
            captured["for_update"] = True
            return self

        def first(self):
            return None

    class FakeDB:
        def query(self, model):
            return FakeQuery()

    locked = task_module.lock_generation_attempt(
        db=FakeDB(),
        website_id="website-id",
        attempt_id=uuid4(),
    )

    assert locked is False
    assert captured["for_update"] is True


@pytest.mark.unit
def test_stale_generation_attempt_cannot_publish(
    monkeypatch,
    tmp_path,
):
    from types import SimpleNamespace
    from uuid import uuid4

    import backend.tasks.website_generation as task_module

    website_id = uuid4()

    website = SimpleNamespace(
        id=website_id,
        user_id=None,
        business_type="Pizza Shop",
        prompt="Create a pizza website.",
        generation_status="queued",
        generation_started_at=None,
        generation_attempt_id=None,
        error_message=None,
        metadata_json={
            "theme": "modern",
        },
        html=None,
        css=None,
        js=None,
        generated_url=None,
        gpt_model=None,
        gpt_tokens_prompt=None,
        gpt_tokens_completion=None,
        gpt_tokens_total=None,
    )

    class FakeQuery:
        def filter(self, *criteria):
            return self

        def first(self):
            return website

        def update(
            self,
            values,
            synchronize_session=None,
        ):
            website.generation_status = "generating"

            website.generation_started_at = values[
                task_module.GeneratedSite.generation_started_at
            ]

            website.generation_attempt_id = values[
                task_module.GeneratedSite.generation_attempt_id
            ]

            return 1

    class FakeDB:
        def __init__(self):
            self.commit_count = 0
            self.rollback_count = 0
            self.closed = False

        def query(self, model):
            return FakeQuery()

        def commit(self):
            self.commit_count += 1

        def rollback(self):
            self.rollback_count += 1

        def refresh(self, obj):
            pass

        def close(self):
            self.closed = True

    db = FakeDB()

    profile = {
        "business_name": "Fence Test",
        "_model": "test-model",
        "_usage": {},
    }

    pages = {
        "index.html": "<html>HOME</html>",
    }

    staging_dir = tmp_path / "staging"
    staging_dir.mkdir()

    published = False

    monkeypatch.setattr(
        task_module,
        "SessionLocal",
        lambda: db,
    )

    monkeypatch.setattr(
        task_module,
        "generate_business_profile",
        lambda **kwargs: profile,
    )

    monkeypatch.setattr(
        task_module,
        "generate_multi_page_site",
        lambda **kwargs: pages,
    )

    monkeypatch.setattr(
        task_module,
        "stage_generated_site",
        lambda **kwargs: staging_dir,
    )

    # Simulate another worker reclaiming this generation
    # after rendering/staging but before publication.
    monkeypatch.setattr(
        task_module,
        "lock_generation_attempt",
        lambda **kwargs: False,
    )

    def fail_if_published(**kwargs):
        nonlocal published
        published = True

        raise AssertionError(
            "A stale generation attempt must not publish."
        )

    monkeypatch.setattr(
        task_module,
        "publish_staged_site",
        fail_if_published,
    )

    task_module.generate_website_task.run(
        str(website_id),
        website.business_type,
    )

    assert published is False

    # The stale worker must not overwrite the newer
    # owner's terminal state.
    assert website.generation_status != "completed"
    assert website.generation_status != "failed"

    # Its private staging output must be discarded.
    assert not staging_dir.exists()

    # Only the successful initial lease claim commits.
    assert db.commit_count == 1

    assert db.closed is True


@pytest.mark.unit
def test_stale_generation_attempt_cannot_persist_failure(
    monkeypatch,
):
    from types import SimpleNamespace
    from uuid import uuid4

    import backend.tasks.website_generation as task_module

    website_id = uuid4()
    newer_attempt_id = uuid4()

    website = SimpleNamespace(
        id=website_id,
        user_id=None,
        business_type="Pizza Shop",
        prompt="Create a pizza website.",
        generation_status="queued",
        generation_started_at=None,
        generation_attempt_id=None,
        error_message=None,
        metadata_json={
            "theme": "modern",
        },
    )

    class FakeQuery:
        def filter(self, *criteria):
            return self

        def first(self):
            return website

        def update(
            self,
            values,
            synchronize_session=None,
        ):
            new_status = values.get(
                task_module.GeneratedSite.generation_status
            )

            # Initial lease claim succeeds.
            if new_status == "generating":
                website.generation_status = "generating"

                website.generation_started_at = values[
                    task_module.GeneratedSite.generation_started_at
                ]

                website.generation_attempt_id = values[
                    task_module.GeneratedSite.generation_attempt_id
                ]

                return 1

            # The later failure transition belongs to the
            # stale worker. Simulate PostgreSQL rejecting
            # its token-conditioned UPDATE after worker B
            # has reclaimed ownership.
            if new_status == "failed":
                return 0

            raise AssertionError(
                f"Unexpected generation update: {new_status!r}"
            )

    class FakeDB:
        def __init__(self):
            self.commit_count = 0
            self.rollback_count = 0
            self.closed = False

        def query(self, model):
            return FakeQuery()

        def commit(self):
            self.commit_count += 1

        def rollback(self):
            self.rollback_count += 1

        def refresh(self, obj):
            pass

        def close(self):
            self.closed = True

    db = FakeDB()

    monkeypatch.setattr(
        task_module,
        "SessionLocal",
        lambda: db,
    )

    def fail_after_reclaim(**kwargs):
        # Simulate worker B reclaiming the row before
        # worker A encounters its generation error.
        website.generation_status = "generating"
        website.generation_attempt_id = newer_attempt_id

        raise RuntimeError(
            "stale worker generation failure"
        )

    monkeypatch.setattr(
        task_module,
        "generate_business_profile",
        fail_after_reclaim,
    )

    with pytest.raises(
        RuntimeError,
        match="stale worker generation failure",
    ):
        task_module.generate_website_task.run(
            str(website_id),
            website.business_type,
        )

    # Worker A must not overwrite worker B's ownership
    # with a terminal failed state.
    assert website.generation_status == "generating"
    assert website.generation_attempt_id == newer_attempt_id
    assert website.error_message is None

    # Only worker A's initial lease claim committed.
    assert db.commit_count == 1

    assert db.closed is True


@pytest.mark.unit
def test_fail_generation_attempt_updates_only_current_owner():
    from uuid import uuid4

    import backend.tasks.website_generation as task_module

    attempt_id = uuid4()
    captured = {}

    class FakeQuery:
        def filter(self, *criteria):
            captured["criteria"] = criteria
            return self

        def update(
            self,
            values,
            synchronize_session=None,
        ):
            captured["values"] = values
            captured["synchronize_session"] = (
                synchronize_session
            )
            return 1

    class FakeDB:
        def __init__(self):
            self.commit_count = 0
            self.rollback_count = 0

        def query(self, model):
            captured["model"] = model
            return FakeQuery()

        def commit(self):
            self.commit_count += 1

        def rollback(self):
            self.rollback_count += 1

    db = FakeDB()

    failed = task_module.fail_generation_attempt(
        db=db,
        website_id="website-id",
        attempt_id=attempt_id,
        error_message="generation failed",
    )

    assert failed is True
    assert captured["model"] is task_module.GeneratedSite

    # website id + generating status + ownership token
    assert len(captured["criteria"]) == 3

    assert (
        captured["values"][
            task_module.GeneratedSite.generation_status
        ]
        == "failed"
    )
    assert (
        captured["values"][
            task_module.GeneratedSite.generation_started_at
        ]
        is None
    )
    assert (
        captured["values"][
            task_module.GeneratedSite.generation_attempt_id
        ]
        is None
    )
    assert (
        captured["values"][
            task_module.GeneratedSite.error_message
        ]
        == "generation failed"
    )

    assert captured["synchronize_session"] is False
    assert db.commit_count == 1
    assert db.rollback_count == 0


@pytest.mark.unit
def test_fail_generation_attempt_does_not_commit_when_fenced_out():
    from uuid import uuid4

    import backend.tasks.website_generation as task_module

    class FakeQuery:
        def filter(self, *criteria):
            return self

        def update(
            self,
            values,
            synchronize_session=None,
        ):
            return 0

    class FakeDB:
        def __init__(self):
            self.commit_count = 0
            self.rollback_count = 0

        def query(self, model):
            return FakeQuery()

        def commit(self):
            self.commit_count += 1

        def rollback(self):
            self.rollback_count += 1

    db = FakeDB()

    failed = task_module.fail_generation_attempt(
        db=db,
        website_id="website-id",
        attempt_id=uuid4(),
        error_message="stale failure",
    )

    assert failed is False
    assert db.commit_count == 0
    assert db.rollback_count == 1


@pytest.mark.unit
def test_generated_orm_fields_are_not_mutated_before_terminal_lock(
    monkeypatch,
    tmp_path,
):
    from types import SimpleNamespace
    from uuid import uuid4

    import backend.tasks.website_generation as task_module

    website_id = uuid4()

    original_metadata = {
        "theme": "modern",
    }

    website = SimpleNamespace(
        id=website_id,
        user_id=None,
        business_type="Pizza Shop",
        prompt="Create a pizza website.",
        generation_status="queued",
        generation_started_at=None,
        generation_attempt_id=None,
        error_message=None,
        metadata_json=original_metadata.copy(),
        html=None,
        css=None,
        js=None,
        generated_url=None,
        gpt_model=None,
        gpt_tokens_prompt=None,
        gpt_tokens_completion=None,
        gpt_tokens_total=None,
    )

    class FakeQuery:
        def filter(self, *criteria):
            return self

        def first(self):
            return website

        def update(
            self,
            values,
            synchronize_session=None,
        ):
            website.generation_status = "generating"
            website.generation_started_at = values[
                task_module.GeneratedSite.generation_started_at
            ]
            website.generation_attempt_id = values[
                task_module.GeneratedSite.generation_attempt_id
            ]
            return 1

    class FakeDB:
        def __init__(self):
            self.commit_count = 0
            self.rollback_count = 0
            self.closed = False

        def query(self, model):
            return FakeQuery()

        def commit(self):
            self.commit_count += 1

        def rollback(self):
            self.rollback_count += 1

        def refresh(self, obj):
            pass

        def close(self):
            self.closed = True

    db = FakeDB()

    profile = {
        "business_name": "Autoflush Fence Test",
        "_model": "test-model",
        "_usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30,
        },
    }

    pages = {
        "index.html": "<html>HOME</html>",
    }

    staging_dir = tmp_path / "staging"
    staging_dir.mkdir()

    observed = {}

    monkeypatch.setattr(
        task_module,
        "SessionLocal",
        lambda: db,
    )

    monkeypatch.setattr(
        task_module,
        "generate_business_profile",
        lambda **kwargs: profile,
    )

    monkeypatch.setattr(
        task_module,
        "generate_multi_page_site",
        lambda **kwargs: pages,
    )

    monkeypatch.setattr(
        task_module,
        "stage_generated_site",
        lambda **kwargs: staging_dir,
    )

    def inspect_before_lock(**kwargs):
        observed["metadata_json"] = website.metadata_json
        observed["html"] = website.html
        observed["generated_url"] = website.generated_url
        observed["gpt_model"] = website.gpt_model

        # Simulate ownership having been reclaimed.
        return False

    monkeypatch.setattr(
        task_module,
        "lock_generation_attempt",
        inspect_before_lock,
    )

    task_module.generate_website_task.run(
        str(website_id),
        website.business_type,
    )

    assert observed["metadata_json"] == original_metadata
    assert observed["html"] is None
    assert observed["generated_url"] is None
    assert observed["gpt_model"] is None

    assert not staging_dir.exists()
    assert db.closed is True


@pytest.mark.unit
def test_publication_failure_cleans_filesystem_before_releasing_fence(
    monkeypatch,
    tmp_path,
):
    from types import SimpleNamespace
    from uuid import uuid4

    import backend.tasks.website_generation as task_module

    website_id = uuid4()

    website = SimpleNamespace(
        id=website_id,
        user_id=None,
        business_type="Pizza Shop",
        prompt="Create a pizza website.",
        generation_status="queued",
        generation_started_at=None,
        generation_attempt_id=None,
        error_message=None,
        metadata_json={
            "theme": "modern",
        },
        html=None,
        css=None,
        js=None,
        generated_url=None,
        gpt_model=None,
        gpt_tokens_prompt=None,
        gpt_tokens_completion=None,
        gpt_tokens_total=None,
    )

    events = []

    class FakeQuery:
        def filter(self, *criteria):
            return self

        def first(self):
            return website

        def with_for_update(self):
            events.append("terminal_lock")
            return self

        def update(
            self,
            values,
            synchronize_session=None,
        ):
            new_status = values.get(
                task_module.GeneratedSite.generation_status
            )

            if new_status == "generating":
                website.generation_status = "generating"
                website.generation_started_at = values[
                    task_module.GeneratedSite.generation_started_at
                ]
                website.generation_attempt_id = values[
                    task_module.GeneratedSite.generation_attempt_id
                ]
                return 1

            if new_status == "failed":
                website.generation_status = "failed"
                website.generation_started_at = None
                website.generation_attempt_id = None
                website.error_message = values[
                    task_module.GeneratedSite.error_message
                ]
                return 1

            raise AssertionError(
                f"Unexpected generation update: {new_status!r}"
            )

    class FakeDB:
        def __init__(self):
            self.commit_count = 0

        def query(self, model):
            return FakeQuery()

        def commit(self):
            self.commit_count += 1
            events.append("commit")

        def rollback(self):
            events.append("db_rollback")

        def refresh(self, obj):
            pass

        def close(self):
            events.append("close")

    db = FakeDB()

    profile = {
        "business_name": "Publication Fence Test",
        "_model": "test-model",
        "_usage": {},
    }

    pages = {
        "index.html": "<html>HOME</html>",
    }

    staging_dir = tmp_path / "staging"
    staging_dir.mkdir()

    monkeypatch.setattr(
        task_module,
        "SessionLocal",
        lambda: db,
    )

    monkeypatch.setattr(
        task_module,
        "generate_business_profile",
        lambda **kwargs: profile,
    )

    monkeypatch.setattr(
        task_module,
        "generate_multi_page_site",
        lambda **kwargs: pages,
    )

    monkeypatch.setattr(
        task_module,
        "stage_generated_site",
        lambda **kwargs: staging_dir,
    )

    from contextlib import nullcontext

    monkeypatch.setattr(
        task_module,
        "publication_lock",
        lambda **kwargs: nullcontext(),
    )

    def failing_publish_staged_site(**kwargs):
        events.append("publish")
        raise OSError(
            "simulated publication failure"
        )

    monkeypatch.setattr(
        task_module,
        "publish_staged_site",
        failing_publish_staged_site,
    )

    real_cleanup = task_module.cleanup_staging

    def tracked_cleanup(path):
        events.append("filesystem_cleanup")
        real_cleanup(path)

    monkeypatch.setattr(
        task_module,
        "cleanup_staging",
        tracked_cleanup,
    )

    with pytest.raises(
        OSError,
        match="simulated publication failure",
    ):
        task_module.generate_website_task.run(
            str(website_id),
            website.business_type,
        )

    assert "terminal_lock" in events
    assert "publish" in events
    assert "filesystem_cleanup" in events
    assert "db_rollback" in events

    # While publication has not committed successfully,
    # filesystem recovery must finish before the database
    # rollback releases the terminal fencing row lock.
    assert events.index(
        "filesystem_cleanup"
    ) < events.index(
        "db_rollback"
    )


@pytest.mark.unit
def test_final_commit_failure_rolls_back_publication_before_releasing_lock(
    monkeypatch,
    tmp_path,
):
    from contextlib import contextmanager
    from types import SimpleNamespace
    from uuid import uuid4

    import backend.tasks.website_generation as task_module

    website_id = uuid4()

    website = SimpleNamespace(
        id=website_id,
        user_id=None,
        business_type="Pizza Shop",
        prompt="Create a pizza website.",
        generation_status="queued",
        generation_started_at=None,
        generation_attempt_id=None,
        error_message=None,
        metadata_json={"theme": "modern"},
        html=None,
        css=None,
        js=None,
        generated_url=None,
        gpt_model=None,
        gpt_tokens_prompt=None,
        gpt_tokens_completion=None,
        gpt_tokens_total=None,
    )

    events = []
    publication_lock_held = False

    class FakeQuery:
        def filter(self, *criteria):
            return self

        def first(self):
            return website

        def with_for_update(self):
            events.append("terminal_db_lock")
            return self

        def update(
            self,
            values,
            synchronize_session=None,
        ):
            new_status = values.get(
                task_module.GeneratedSite.generation_status
            )

            if new_status == "generating":
                website.generation_status = "generating"
                website.generation_started_at = values[
                    task_module.GeneratedSite.generation_started_at
                ]
                website.generation_attempt_id = values[
                    task_module.GeneratedSite.generation_attempt_id
                ]
                return 1

            if new_status == "failed":
                website.generation_status = "failed"
                website.generation_started_at = None
                website.generation_attempt_id = None
                website.error_message = values[
                    task_module.GeneratedSite.error_message
                ]
                return 1

            raise AssertionError(
                f"Unexpected generation update: {new_status!r}"
            )

    class FakeDB:
        def __init__(self):
            self.commit_count = 0

        def query(self, model):
            return FakeQuery()

        def commit(self):
            self.commit_count += 1
            events.append(
                f"commit_{self.commit_count}"
            )

            # Commit 1 = successful lease claim.
            # Commit 2 = authoritative completed commit.
            # Commit 3 = fenced failed-state persistence.
            if self.commit_count == 2:
                raise RuntimeError(
                    "final persistence commit failed"
                )

        def rollback(self):
            events.append("db_rollback")

        def refresh(self, obj):
            pass

        def close(self):
            events.append("close")

    db = FakeDB()

    profile = {
        "business_name": "Publication Lock Test",
        "_model": "test-model",
        "_usage": {},
    }

    pages = {
        "index.html": "<html>HOME</html>",
    }

    staging_dir = tmp_path / "staging"
    staging_dir.mkdir()

    publication_state = SimpleNamespace(
        public_dir=tmp_path / "public",
        backup_dir=None,
    )

    monkeypatch.setattr(
        task_module,
        "SessionLocal",
        lambda: db,
    )

    monkeypatch.setattr(
        task_module,
        "generate_business_profile",
        lambda **kwargs: profile,
    )

    monkeypatch.setattr(
        task_module,
        "generate_multi_page_site",
        lambda **kwargs: pages,
    )

    monkeypatch.setattr(
        task_module,
        "stage_generated_site",
        lambda **kwargs: staging_dir,
    )

    @contextmanager
    def tracked_publication_lock(**kwargs):
        nonlocal publication_lock_held

        publication_lock_held = True
        events.append("publication_lock_acquired")

        try:
            yield
        finally:
            events.append("publication_lock_released")
            publication_lock_held = False

    # This monkeypatch is expected to fail in the RED
    # state because the task does not import/use the
    # publication lock yet.
    monkeypatch.setattr(
        task_module,
        "publication_lock",
        tracked_publication_lock,
    )

    def tracked_publish(**kwargs):
        assert publication_lock_held
        events.append("publish")
        return publication_state

    monkeypatch.setattr(
        task_module,
        "publish_staged_site",
        tracked_publish,
    )

    def tracked_rollback(state):
        assert state is publication_state
        assert publication_lock_held
        events.append("publication_rollback")

    monkeypatch.setattr(
        task_module,
        "rollback_publication",
        tracked_rollback,
    )

    monkeypatch.setattr(
        task_module,
        "finalize_publication",
        lambda state: None,
    )

    with pytest.raises(
        RuntimeError,
        match="final persistence commit failed",
    ):
        task_module.generate_website_task.run(
            str(website_id),
            website.business_type,
        )

    assert events.index(
        "publication_lock_acquired"
    ) < events.index(
        "publish"
    )

    assert events.index(
        "db_rollback"
    ) < events.index(
        "publication_rollback"
    )

    assert events.index(
        "publication_rollback"
    ) < events.index(
        "publication_lock_released"
    )


@pytest.mark.unit
def test_final_commit_failure_rolls_back_publication_before_releasing_lock(
    monkeypatch,
    tmp_path,
):
    from contextlib import contextmanager
    from types import SimpleNamespace
    from uuid import uuid4

    import backend.tasks.website_generation as task_module

    website_id = uuid4()

    website = SimpleNamespace(
        id=website_id,
        user_id=None,
        business_type="Pizza Shop",
        prompt="Create a pizza website.",
        generation_status="queued",
        generation_started_at=None,
        generation_attempt_id=None,
        error_message=None,
        metadata_json={"theme": "modern"},
        html=None,
        css=None,
        js=None,
        generated_url=None,
        gpt_model=None,
        gpt_tokens_prompt=None,
        gpt_tokens_completion=None,
        gpt_tokens_total=None,
    )

    events = []
    publication_lock_held = False

    class FakeQuery:
        def filter(self, *criteria):
            return self

        def first(self):
            return website

        def with_for_update(self):
            events.append("terminal_db_lock")
            return self

        def update(
            self,
            values,
            synchronize_session=None,
        ):
            new_status = values.get(
                task_module.GeneratedSite.generation_status
            )

            if new_status == "generating":
                website.generation_status = "generating"
                website.generation_started_at = values[
                    task_module.GeneratedSite.generation_started_at
                ]
                website.generation_attempt_id = values[
                    task_module.GeneratedSite.generation_attempt_id
                ]
                return 1

            if new_status == "failed":
                website.generation_status = "failed"
                website.generation_started_at = None
                website.generation_attempt_id = None
                website.error_message = values[
                    task_module.GeneratedSite.error_message
                ]
                return 1

            raise AssertionError(
                f"Unexpected generation update: {new_status!r}"
            )

    class FakeDB:
        def __init__(self):
            self.commit_count = 0

        def query(self, model):
            return FakeQuery()

        def commit(self):
            self.commit_count += 1
            events.append(
                f"commit_{self.commit_count}"
            )

            # Commit 1 = successful lease claim.
            # Commit 2 = authoritative completed commit.
            # Commit 3 = fenced failed-state persistence.
            if self.commit_count == 2:
                raise RuntimeError(
                    "final persistence commit failed"
                )

        def rollback(self):
            events.append("db_rollback")

        def refresh(self, obj):
            pass

        def close(self):
            events.append("close")

    db = FakeDB()

    profile = {
        "business_name": "Publication Lock Test",
        "_model": "test-model",
        "_usage": {},
    }

    pages = {
        "index.html": "<html>HOME</html>",
    }

    staging_dir = tmp_path / "staging"
    staging_dir.mkdir()

    publication_state = SimpleNamespace(
        public_dir=tmp_path / "public",
        backup_dir=None,
    )

    monkeypatch.setattr(
        task_module,
        "SessionLocal",
        lambda: db,
    )

    monkeypatch.setattr(
        task_module,
        "generate_business_profile",
        lambda **kwargs: profile,
    )

    monkeypatch.setattr(
        task_module,
        "generate_multi_page_site",
        lambda **kwargs: pages,
    )

    monkeypatch.setattr(
        task_module,
        "stage_generated_site",
        lambda **kwargs: staging_dir,
    )

    @contextmanager
    def tracked_publication_lock(**kwargs):
        nonlocal publication_lock_held

        publication_lock_held = True
        events.append("publication_lock_acquired")

        try:
            yield
        finally:
            events.append("publication_lock_released")
            publication_lock_held = False

    # This monkeypatch is expected to fail in the RED
    # state because the task does not import/use the
    # publication lock yet.
    monkeypatch.setattr(
        task_module,
        "publication_lock",
        tracked_publication_lock,
    )

    def tracked_publish(**kwargs):
        assert publication_lock_held
        events.append("publish")
        return publication_state

    monkeypatch.setattr(
        task_module,
        "publish_staged_site",
        tracked_publish,
    )

    def tracked_rollback(state):
        assert state is publication_state
        assert publication_lock_held
        events.append("publication_rollback")

    monkeypatch.setattr(
        task_module,
        "rollback_publication",
        tracked_rollback,
    )

    monkeypatch.setattr(
        task_module,
        "finalize_publication",
        lambda state: None,
    )

    with pytest.raises(
        RuntimeError,
        match="final persistence commit failed",
    ):
        task_module.generate_website_task.run(
            str(website_id),
            website.business_type,
        )

    assert events.index(
        "publication_lock_acquired"
    ) < events.index(
        "publish"
    )

    assert events.index(
        "db_rollback"
    ) < events.index(
        "publication_rollback"
    )

    assert events.index(
        "publication_rollback"
    ) < events.index(
        "publication_lock_released"
    )


@pytest.mark.unit
def test_publication_lock_release_failure_does_not_fail_completed_generation(
    monkeypatch,
    tmp_path,
):
    from types import SimpleNamespace
    from uuid import uuid4

    import backend.tasks.website_generation as task_module

    website_id = uuid4()

    website = SimpleNamespace(
        id=website_id,
        user_id=None,
        business_type="Pizza Shop",
        prompt="Create a pizza website.",
        generation_status="queued",
        generation_started_at=None,
        generation_attempt_id=None,
        error_message=None,
        metadata_json={"theme": "modern"},
        html=None,
        css=None,
        js=None,
        generated_url=None,
        gpt_model=None,
        gpt_tokens_prompt=None,
        gpt_tokens_completion=None,
        gpt_tokens_total=None,
    )

    events = []

    class FakeQuery:
        def filter(self, *criteria):
            return self

        def first(self):
            return website

        def with_for_update(self):
            events.append("terminal_db_lock")
            return self

        def update(
            self,
            values,
            synchronize_session=None,
        ):
            new_status = values.get(
                task_module.GeneratedSite.generation_status
            )

            if new_status == "generating":
                website.generation_status = "generating"
                website.generation_started_at = values[
                    task_module.GeneratedSite.generation_started_at
                ]
                website.generation_attempt_id = values[
                    task_module.GeneratedSite.generation_attempt_id
                ]
                return 1

            if new_status == "failed":
                events.append("failed_state_update")
                website.generation_status = "failed"
                return 1

            raise AssertionError(
                f"Unexpected generation update: {new_status!r}"
            )

    class FakeDB:
        def __init__(self):
            self.commit_count = 0
            self.rollback_count = 0

        def query(self, model):
            return FakeQuery()

        def commit(self):
            self.commit_count += 1
            events.append(
                f"commit_{self.commit_count}"
            )

        def rollback(self):
            self.rollback_count += 1
            events.append("db_rollback")

        def refresh(self, obj):
            events.append("refresh")

        def close(self):
            events.append("close")

    class FailingReleaseLock:
        def __enter__(self):
            events.append(
                "publication_lock_acquired"
            )
            return self

        def __exit__(
            self,
            exc_type,
            exc,
            traceback,
        ):
            events.append(
                "publication_lock_release_attempt"
            )
            raise OSError(
                "simulated publication lock release failure"
            )

    db = FakeDB()

    profile = {
        "business_name": "Lock Release Test",
        "_model": "test-model",
        "_usage": {},
    }

    pages = {
        "index.html": "<html>HOME</html>",
    }

    staging_dir = tmp_path / "staging"
    staging_dir.mkdir()

    publication_state = SimpleNamespace(
        public_dir=tmp_path / "public",
        backup_dir=None,
    )

    monkeypatch.setattr(
        task_module,
        "SessionLocal",
        lambda: db,
    )

    monkeypatch.setattr(
        task_module,
        "generate_business_profile",
        lambda **kwargs: profile,
    )

    monkeypatch.setattr(
        task_module,
        "generate_multi_page_site",
        lambda **kwargs: pages,
    )

    monkeypatch.setattr(
        task_module,
        "stage_generated_site",
        lambda **kwargs: staging_dir,
    )

    monkeypatch.setattr(
        task_module,
        "publication_lock",
        lambda **kwargs: FailingReleaseLock(),
    )

    def tracked_publish(**kwargs):
        events.append("publish")
        return publication_state

    monkeypatch.setattr(
        task_module,
        "publish_staged_site",
        tracked_publish,
    )

    def tracked_finalize(state):
        assert state is publication_state
        events.append("finalize")

    monkeypatch.setattr(
        task_module,
        "finalize_publication",
        tracked_finalize,
    )

    def forbidden_rollback(state):
        raise AssertionError(
            "completed publication must not be rolled back"
        )

    monkeypatch.setattr(
        task_module,
        "rollback_publication",
        forbidden_rollback,
    )

    # Once commit_2 succeeds, lock-release failure is a
    # post-commit cleanup failure and must not escape.
    task_module.generate_website_task.run(
        str(website_id),
        website.business_type,
    )

    assert website.generation_status == "completed"
    assert db.commit_count == 2
    assert db.rollback_count == 0
    assert "failed_state_update" not in events

    assert events.index(
        "commit_2"
    ) < events.index(
        "publication_lock_release_attempt"
    )


@pytest.mark.unit
def test_publication_lock_acquisition_failure_does_not_release_unentered_context(
    monkeypatch,
    tmp_path,
):
    import backend.tasks.website_generation as task_module

    website_id = uuid4()
    events = []

    website = SimpleNamespace(
        id=website_id,
        user_id=None,
        project_name="Lock Acquisition Failure Contract",
        business_type="Pizza Shop",
        prompt="Create a neighborhood pizza website.",
        generation_status="queued",
        generation_started_at=None,
        generation_attempt_id=None,
        error_message=None,
        metadata_json={"theme": "modern"},
        html=None,
        css=None,
        js=None,
        generated_url=None,
        gpt_model=None,
        gpt_tokens_prompt=None,
        gpt_tokens_completion=None,
        gpt_tokens_total=None,
    )

    class FakeQuery:
        def filter(self, *criteria):
            return self

        def first(self):
            return website

        def with_for_update(self):
            events.append("terminal_db_lock")
            return self

        def update(
            self,
            values,
            synchronize_session=None,
        ):
            new_status = values.get(
                task_module.GeneratedSite.generation_status
            )

            if new_status == "generating":
                website.generation_status = "generating"
                website.generation_started_at = values[
                    task_module.GeneratedSite.generation_started_at
                ]
                website.generation_attempt_id = values[
                    task_module.GeneratedSite.generation_attempt_id
                ]
                return 1

            if new_status == "failed":
                events.append("failed_state_update")
                website.generation_status = "failed"
                website.generation_started_at = None
                website.generation_attempt_id = None
                website.error_message = values[
                    task_module.GeneratedSite.error_message
                ]
                return 1

            raise AssertionError(
                f"Unexpected generation update: {new_status!r}"
            )

    class FakeDB:
        def __init__(self):
            self.commit_count = 0
            self.rollback_count = 0

        def query(self, model):
            return FakeQuery()

        def commit(self):
            self.commit_count += 1
            events.append(
                f"commit_{self.commit_count}"
            )

        def rollback(self):
            self.rollback_count += 1
            events.append("db_rollback")

        def refresh(self, obj):
            events.append("refresh")

        def close(self):
            events.append("close")

    class FailingAcquireLock:
        def __enter__(self):
            events.append(
                "publication_lock_acquire_attempt"
            )
            raise OSError(
                "simulated publication lock acquisition failure"
            )

        def __exit__(
            self,
            exc_type,
            exc,
            traceback,
        ):
            events.append(
                "publication_lock_release_attempt"
            )
            raise RuntimeError(
                "unentered publication lock was released"
            )

    db = FakeDB()

    profile = {
        "business_name": "Lock Acquisition Test",
        "_model": "test-model",
        "_usage": {},
    }

    pages = {
        "index.html": "<html>HOME</html>",
    }

    staging_dir = tmp_path / "staging"
    staging_dir.mkdir()

    monkeypatch.setattr(
        task_module,
        "SessionLocal",
        lambda: db,
    )

    monkeypatch.setattr(
        task_module,
        "generate_business_profile",
        lambda **kwargs: profile,
    )

    monkeypatch.setattr(
        task_module,
        "generate_multi_page_site",
        lambda **kwargs: pages,
    )

    monkeypatch.setattr(
        task_module,
        "stage_generated_site",
        lambda **kwargs: staging_dir,
    )

    monkeypatch.setattr(
        task_module,
        "publication_lock",
        lambda **kwargs: FailingAcquireLock(),
    )

    def forbidden_publish(**kwargs):
        raise AssertionError(
            "publication must not run when lock acquisition fails"
        )

    monkeypatch.setattr(
        task_module,
        "publish_staged_site",
        forbidden_publish,
    )

    with pytest.raises(
        OSError,
        match="simulated publication lock acquisition failure",
    ):
        task_module.generate_website_task.run(
            str(website_id),
            website.business_type,
        )

    assert (
        "publication_lock_acquire_attempt"
        in events
    )
    assert (
        "publication_lock_release_attempt"
        not in events
    )
    assert "failed_state_update" in events
    assert website.generation_status == "failed"
    assert db.rollback_count == 1
    assert db.commit_count == 2


@pytest.mark.unit
def test_publication_lock_release_failure_does_not_mask_generation_failure(
    monkeypatch,
    tmp_path,
):
    import backend.tasks.website_generation as task_module

    website_id = uuid4()
    events = []

    website = SimpleNamespace(
        id=website_id,
        user_id=None,
        business_type="Pizza Shop",
        prompt="Create a pizza website.",
        generation_status="queued",
        generation_started_at=None,
        generation_attempt_id=None,
        error_message=None,
        metadata_json={"theme": "modern"},
        html=None,
        css=None,
        js=None,
        generated_url=None,
        gpt_model=None,
        gpt_tokens_prompt=None,
        gpt_tokens_completion=None,
        gpt_tokens_total=None,
    )

    class FakeQuery:
        def filter(self, *criteria):
            return self

        def first(self):
            return website

        def with_for_update(self):
            events.append("terminal_db_lock")
            return self

        def update(
            self,
            values,
            synchronize_session=None,
        ):
            new_status = values.get(
                task_module.GeneratedSite.generation_status
            )

            if new_status == "generating":
                website.generation_status = "generating"
                website.generation_started_at = values[
                    task_module.GeneratedSite.generation_started_at
                ]
                website.generation_attempt_id = values[
                    task_module.GeneratedSite.generation_attempt_id
                ]
                return 1

            if new_status == "failed":
                events.append("failed_state_update")
                website.generation_status = "failed"
                website.generation_started_at = None
                website.generation_attempt_id = None
                website.error_message = values[
                    task_module.GeneratedSite.error_message
                ]
                return 1

            raise AssertionError(
                f"Unexpected generation update: {new_status!r}"
            )

    class FakeDB:
        def __init__(self):
            self.commit_count = 0
            self.rollback_count = 0

        def query(self, model):
            return FakeQuery()

        def commit(self):
            self.commit_count += 1
            events.append(
                f"commit_{self.commit_count}"
            )

        def rollback(self):
            self.rollback_count += 1
            events.append("db_rollback")

        def refresh(self, obj):
            events.append("refresh")

        def close(self):
            events.append("close")

    class FailingReleaseLock:
        def __enter__(self):
            events.append("publication_lock_acquired")
            return self

        def __exit__(
            self,
            exc_type,
            exc,
            traceback,
        ):
            events.append("publication_lock_release_attempt")
            raise OSError(
                "simulated publication lock release failure"
            )

    db = FakeDB()

    profile = {
        "business_name": "Failure Release Test",
        "_model": "test-model",
        "_usage": {},
    }

    pages = {
        "index.html": "<html>HOME</html>",
    }

    staging_dir = tmp_path / "staging"
    staging_dir.mkdir()

    monkeypatch.setattr(
        task_module,
        "SessionLocal",
        lambda: db,
    )

    monkeypatch.setattr(
        task_module,
        "generate_business_profile",
        lambda **kwargs: profile,
    )

    monkeypatch.setattr(
        task_module,
        "generate_multi_page_site",
        lambda **kwargs: pages,
    )

    monkeypatch.setattr(
        task_module,
        "stage_generated_site",
        lambda **kwargs: staging_dir,
    )

    monkeypatch.setattr(
        task_module,
        "publication_lock",
        lambda **kwargs: FailingReleaseLock(),
    )

    def failing_publish(**kwargs):
        events.append("publish")
        raise ValueError(
            "original publication failure"
        )

    monkeypatch.setattr(
        task_module,
        "publish_staged_site",
        failing_publish,
    )

    with pytest.raises(
        ValueError,
        match="original publication failure",
    ):
        task_module.generate_website_task.run(
            str(website_id),
            website.business_type,
        )

    assert website.generation_status == "failed"
    assert website.error_message == (
        "original publication failure"
    )

    assert db.rollback_count == 1
    assert db.commit_count == 2

    assert events.count(
        "publication_lock_release_attempt"
    ) == 1

    assert events.index(
        "failed_state_update"
    ) < events.index(
        "publication_lock_release_attempt"
    )


@pytest.mark.unit
def test_failure_persistence_error_releases_lock_and_preserves_original_error(
    monkeypatch,
    tmp_path,
):
    import backend.tasks.website_generation as task_module

    website_id = uuid4()
    events = []

    website = SimpleNamespace(
        id=website_id,
        user_id=None,
        business_type="Pizza Shop",
        prompt="Create a pizza website.",
        generation_status="queued",
        generation_started_at=None,
        generation_attempt_id=None,
        error_message=None,
        metadata_json={"theme": "modern"},
        html=None,
        css=None,
        js=None,
        generated_url=None,
        gpt_model=None,
        gpt_tokens_prompt=None,
        gpt_tokens_completion=None,
        gpt_tokens_total=None,
    )

    class FakeQuery:
        def filter(self, *criteria):
            return self

        def first(self):
            return website

    class FakeDB:
        def __init__(self):
            self.rollback_count = 0
            self.closed = False

        def query(self, model):
            return FakeQuery()

        def refresh(self, obj):
            pass

        def rollback(self):
            self.rollback_count += 1
            events.append("db_rollback")

        def close(self):
            self.closed = True
            events.append("db_close")

    class TrackingLock:
        def __enter__(self):
            events.append("publication_lock_acquired")
            return self

        def __exit__(
            self,
            exc_type,
            exc,
            traceback,
        ):
            events.append("publication_lock_released")
            return False

    db = FakeDB()
    staging_dir = tmp_path / "staging"
    staging_dir.mkdir()

    monkeypatch.setattr(
        task_module,
        "SessionLocal",
        lambda: db,
    )

    def fake_claim_generation_lease(**kwargs):
        website.generation_status = "generating"
        website.generation_attempt_id = kwargs["attempt_id"]
        return True

    monkeypatch.setattr(
        task_module,
        "claim_generation_lease",
        fake_claim_generation_lease,
    )

    monkeypatch.setattr(
        task_module,
        "generate_business_profile",
        lambda **kwargs: {
            "business_name": "Failure Persistence Test",
            "_model": "test-model",
            "_usage": {},
        },
    )

    monkeypatch.setattr(
        task_module,
        "generate_multi_page_site",
        lambda **kwargs: {
            "index.html": "<html>HOME</html>",
        },
    )

    monkeypatch.setattr(
        task_module,
        "stage_generated_site",
        lambda **kwargs: staging_dir,
    )

    monkeypatch.setattr(
        task_module,
        "lock_generation_attempt",
        lambda **kwargs: True,
    )

    monkeypatch.setattr(
        task_module,
        "publication_lock",
        lambda **kwargs: TrackingLock(),
    )

    def failing_publish(**kwargs):
        events.append("publish")
        raise ValueError(
            "original publication failure"
        )

    monkeypatch.setattr(
        task_module,
        "publish_staged_site",
        failing_publish,
    )

    def failing_failure_persistence(**kwargs):
        events.append("failed_state_persistence")
        raise RuntimeError(
            "failure-state persistence failed"
        )

    monkeypatch.setattr(
        task_module,
        "fail_generation_attempt",
        failing_failure_persistence,
    )

    with pytest.raises(
        ValueError,
        match="original publication failure",
    ):
        task_module.generate_website_task.run(
            str(website_id),
            website.business_type,
        )

    assert events.count(
        "publication_lock_released"
    ) == 1

    assert events.index(
        "failed_state_persistence"
    ) < events.index(
        "publication_lock_released"
    )

    assert db.rollback_count == 1
    assert db.closed is True


@pytest.mark.unit
def test_publication_rollback_failure_releases_lock_and_preserves_original_error(
    monkeypatch,
    tmp_path,
):
    import backend.tasks.website_generation as task_module

    website_id = uuid4()
    events = []

    website = SimpleNamespace(
        id=website_id,
        user_id=None,
        business_type="Pizza Shop",
        prompt="Create a pizza website.",
        generation_status="queued",
        generation_started_at=None,
        generation_attempt_id=None,
        error_message=None,
        metadata_json={"theme": "modern"},
        html=None,
        css=None,
        js=None,
        generated_url=None,
        gpt_model=None,
        gpt_tokens_prompt=None,
        gpt_tokens_completion=None,
        gpt_tokens_total=None,
    )

    class FakeQuery:
        def filter(self, *criteria):
            return self

        def first(self):
            return website

    class FakeDB:
        def __init__(self):
            self.commit_count = 0
            self.rollback_count = 0
            self.closed = False

        def query(self, model):
            return FakeQuery()

        def refresh(self, obj):
            pass

        def commit(self):
            self.commit_count += 1
            events.append(
                f"commit_{self.commit_count}"
            )

            if self.commit_count == 1:
                raise RuntimeError(
                    "final persistence commit failed"
                )

        def rollback(self):
            self.rollback_count += 1
            events.append("db_rollback")

        def close(self):
            self.closed = True
            events.append("db_close")

    class TrackingLock:
        def __enter__(self):
            events.append("publication_lock_acquired")
            return self

        def __exit__(
            self,
            exc_type,
            exc,
            traceback,
        ):
            events.append("publication_lock_released")
            return False

    db = FakeDB()

    staging_dir = tmp_path / "staging"
    staging_dir.mkdir()

    publication_state = SimpleNamespace(
        public_dir=tmp_path / "public",
        backup_dir=None,
    )

    monkeypatch.setattr(
        task_module,
        "SessionLocal",
        lambda: db,
    )

    def fake_claim_generation_lease(**kwargs):
        website.generation_status = "generating"
        website.generation_attempt_id = kwargs["attempt_id"]
        return True

    monkeypatch.setattr(
        task_module,
        "claim_generation_lease",
        fake_claim_generation_lease,
    )

    monkeypatch.setattr(
        task_module,
        "generate_business_profile",
        lambda **kwargs: {
            "business_name": "Rollback Failure Test",
            "_model": "test-model",
            "_usage": {},
        },
    )

    monkeypatch.setattr(
        task_module,
        "generate_multi_page_site",
        lambda **kwargs: {
            "index.html": "<html>HOME</html>",
        },
    )

    monkeypatch.setattr(
        task_module,
        "stage_generated_site",
        lambda **kwargs: staging_dir,
    )

    monkeypatch.setattr(
        task_module,
        "lock_generation_attempt",
        lambda **kwargs: True,
    )

    monkeypatch.setattr(
        task_module,
        "publication_lock",
        lambda **kwargs: TrackingLock(),
    )

    def tracked_publish(**kwargs):
        events.append("publish")
        return publication_state

    monkeypatch.setattr(
        task_module,
        "publish_staged_site",
        tracked_publish,
    )

    def failing_rollback(state):
        assert state is publication_state
        events.append("publication_rollback")
        raise OSError(
            "publication rollback failed"
        )

    monkeypatch.setattr(
        task_module,
        "rollback_publication",
        failing_rollback,
    )

    monkeypatch.setattr(
        task_module,
        "finalize_publication",
        lambda state: None,
    )

    def tracked_failure_persistence(**kwargs):
        events.append("failed_state_persistence")
        return True

    monkeypatch.setattr(
        task_module,
        "fail_generation_attempt",
        tracked_failure_persistence,
    )

    with pytest.raises(
        RuntimeError,
        match="final persistence commit failed",
    ):
        task_module.generate_website_task.run(
            str(website_id),
            website.business_type,
        )

    assert events.count(
        "publication_lock_released"
    ) == 1

    assert events.index(
        "publication_rollback"
    ) < events.index(
        "publication_lock_released"
    )

    assert "failed_state_persistence" in events
    assert db.rollback_count == 1
    assert db.closed is True


@pytest.mark.unit
def test_db_rollback_failure_releases_lock_and_preserves_original_error(
    monkeypatch,
    tmp_path,
):
    import backend.tasks.website_generation as task_module

    website_id = uuid4()
    events = []

    website = SimpleNamespace(
        id=website_id,
        user_id=None,
        business_type="Pizza Shop",
        prompt="Create a pizza website.",
        generation_status="queued",
        generation_started_at=None,
        generation_attempt_id=None,
        error_message=None,
        metadata_json={"theme": "modern"},
        html=None,
        css=None,
        js=None,
        generated_url=None,
        gpt_model=None,
        gpt_tokens_prompt=None,
        gpt_tokens_completion=None,
        gpt_tokens_total=None,
    )

    class FakeQuery:
        def filter(self, *criteria):
            return self

        def first(self):
            return website

    class FakeDB:
        def __init__(self):
            self.commit_count = 0
            self.rollback_count = 0
            self.closed = False

        def query(self, model):
            return FakeQuery()

        def refresh(self, obj):
            pass

        def commit(self):
            self.commit_count += 1
            events.append(
                f"commit_{self.commit_count}"
            )

            if self.commit_count == 1:
                raise RuntimeError(
                    "final persistence commit failed"
                )

        def rollback(self):
            self.rollback_count += 1
            events.append("db_rollback")
            raise OSError(
                "database rollback failed"
            )

        def close(self):
            self.closed = True
            events.append("db_close")

    class TrackingLock:
        def __enter__(self):
            events.append("publication_lock_acquired")
            return self

        def __exit__(
            self,
            exc_type,
            exc,
            traceback,
        ):
            events.append("publication_lock_released")
            return False

    db = FakeDB()

    staging_dir = tmp_path / "staging"
    staging_dir.mkdir()

    publication_state = SimpleNamespace(
        public_dir=tmp_path / "public",
        backup_dir=None,
    )

    monkeypatch.setattr(
        task_module,
        "SessionLocal",
        lambda: db,
    )

    def fake_claim_generation_lease(**kwargs):
        website.generation_status = "generating"
        website.generation_attempt_id = kwargs["attempt_id"]
        return True

    monkeypatch.setattr(
        task_module,
        "claim_generation_lease",
        fake_claim_generation_lease,
    )

    monkeypatch.setattr(
        task_module,
        "generate_business_profile",
        lambda **kwargs: {
            "business_name": "DB Rollback Failure Test",
            "_model": "test-model",
            "_usage": {},
        },
    )

    monkeypatch.setattr(
        task_module,
        "generate_multi_page_site",
        lambda **kwargs: {
            "index.html": "<html>HOME</html>",
        },
    )

    monkeypatch.setattr(
        task_module,
        "stage_generated_site",
        lambda **kwargs: staging_dir,
    )

    monkeypatch.setattr(
        task_module,
        "lock_generation_attempt",
        lambda **kwargs: True,
    )

    monkeypatch.setattr(
        task_module,
        "publication_lock",
        lambda **kwargs: TrackingLock(),
    )

    def tracked_publish(**kwargs):
        events.append("publish")
        return publication_state

    monkeypatch.setattr(
        task_module,
        "publish_staged_site",
        tracked_publish,
    )

    def tracked_publication_rollback(state):
        assert state is publication_state
        events.append("publication_rollback")

    monkeypatch.setattr(
        task_module,
        "rollback_publication",
        tracked_publication_rollback,
    )

    monkeypatch.setattr(
        task_module,
        "finalize_publication",
        lambda state: None,
    )

    def tracked_failure_persistence(**kwargs):
        events.append("failed_state_persistence")
        return True

    monkeypatch.setattr(
        task_module,
        "fail_generation_attempt",
        tracked_failure_persistence,
    )

    with pytest.raises(
        RuntimeError,
        match="final persistence commit failed",
    ):
        task_module.generate_website_task.run(
            str(website_id),
            website.business_type,
        )

    assert db.rollback_count == 1

    assert "publication_rollback" in events
    assert "failed_state_persistence" in events

    assert events.count(
        "publication_lock_released"
    ) == 1

    assert events.index(
        "db_rollback"
    ) < events.index(
        "publication_rollback"
    )

    assert events.index(
        "publication_rollback"
    ) < events.index(
        "failed_state_persistence"
    )

    assert events.index(
        "failed_state_persistence"
    ) < events.index(
        "publication_lock_released"
    )

    assert db.closed is True


@pytest.mark.unit
def test_db_close_failure_does_not_mask_original_generation_failure(
    monkeypatch,
    tmp_path,
):
    import backend.tasks.website_generation as task_module

    website_id = uuid4()
    events = []

    website = SimpleNamespace(
        id=website_id,
        user_id=None,
        business_type="Pizza Shop",
        prompt="Create a pizza website.",
        generation_status="queued",
        generation_started_at=None,
        generation_attempt_id=None,
        error_message=None,
        metadata_json={"theme": "modern"},
        html=None,
        css=None,
        js=None,
        generated_url=None,
        gpt_model=None,
        gpt_tokens_prompt=None,
        gpt_tokens_completion=None,
        gpt_tokens_total=None,
    )

    class FakeQuery:
        def filter(self, *criteria):
            return self

        def first(self):
            return website

    class FakeDB:
        def __init__(self):
            self.commit_count = 0
            self.rollback_count = 0
            self.close_count = 0

        def query(self, model):
            return FakeQuery()

        def refresh(self, obj):
            pass

        def commit(self):
            self.commit_count += 1
            events.append(
                f"commit_{self.commit_count}"
            )

            if self.commit_count == 1:
                raise RuntimeError(
                    "final persistence commit failed"
                )

        def rollback(self):
            self.rollback_count += 1
            events.append("db_rollback")

        def close(self):
            self.close_count += 1
            events.append("db_close")
            raise OSError(
                "database close failed"
            )

    class TrackingLock:
        def __enter__(self):
            events.append("publication_lock_acquired")
            return self

        def __exit__(
            self,
            exc_type,
            exc,
            traceback,
        ):
            events.append("publication_lock_released")
            return False

    db = FakeDB()

    staging_dir = tmp_path / "staging"
    staging_dir.mkdir()

    publication_state = SimpleNamespace(
        public_dir=tmp_path / "public",
        backup_dir=None,
    )

    monkeypatch.setattr(
        task_module,
        "SessionLocal",
        lambda: db,
    )

    def fake_claim_generation_lease(**kwargs):
        website.generation_status = "generating"
        website.generation_attempt_id = kwargs["attempt_id"]
        return True

    monkeypatch.setattr(
        task_module,
        "claim_generation_lease",
        fake_claim_generation_lease,
    )

    monkeypatch.setattr(
        task_module,
        "generate_business_profile",
        lambda **kwargs: {
            "business_name": "DB Close Failure Test",
            "_model": "test-model",
            "_usage": {},
        },
    )

    monkeypatch.setattr(
        task_module,
        "generate_multi_page_site",
        lambda **kwargs: {
            "index.html": "<html>HOME</html>",
        },
    )

    monkeypatch.setattr(
        task_module,
        "stage_generated_site",
        lambda **kwargs: staging_dir,
    )

    monkeypatch.setattr(
        task_module,
        "lock_generation_attempt",
        lambda **kwargs: True,
    )

    monkeypatch.setattr(
        task_module,
        "publication_lock",
        lambda **kwargs: TrackingLock(),
    )

    def tracked_publish(**kwargs):
        events.append("publish")
        return publication_state

    monkeypatch.setattr(
        task_module,
        "publish_staged_site",
        tracked_publish,
    )

    def tracked_publication_rollback(state):
        assert state is publication_state
        events.append("publication_rollback")

    monkeypatch.setattr(
        task_module,
        "rollback_publication",
        tracked_publication_rollback,
    )

    monkeypatch.setattr(
        task_module,
        "finalize_publication",
        lambda state: None,
    )

    def tracked_failure_persistence(**kwargs):
        events.append("failed_state_persistence")
        return True

    monkeypatch.setattr(
        task_module,
        "fail_generation_attempt",
        tracked_failure_persistence,
    )

    with pytest.raises(
        RuntimeError,
        match="final persistence commit failed",
    ):
        task_module.generate_website_task.run(
            str(website_id),
            website.business_type,
        )

    assert db.rollback_count == 1
    assert db.close_count == 1

    assert "publication_rollback" in events
    assert "failed_state_persistence" in events

    assert events.count(
        "publication_lock_released"
    ) == 1

    assert events.index(
        "publication_lock_released"
    ) < events.index(
        "db_close"
    )
