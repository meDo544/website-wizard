from contextlib import nullcontext
from types import SimpleNamespace
from uuid import uuid4

import pytest

import backend.tasks.website_generation as task_module
import backend.services.website_publication as publication_module


class FakeQuery:
    def __init__(self, website):
        self.website = website

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self.website

    def with_for_update(self):
        return self

    def update(
        self,
        values,
        synchronize_session=None,
    ):
        # Model successful token-conditioned generation
        # transitions. Eligibility and stale-owner behavior
        # are covered by the focused fencing contracts.
        column_attributes = (
            (
                task_module.GeneratedSite.generation_status,
                "generation_status",
            ),
            (
                task_module.GeneratedSite.generation_started_at,
                "generation_started_at",
            ),
            (
                task_module.GeneratedSite.generation_attempt_id,
                "generation_attempt_id",
            ),
            (
                task_module.GeneratedSite.error_message,
                "error_message",
            ),
        )

        for column, attribute in column_attributes:
            if column in values:
                setattr(
                    self.website,
                    attribute,
                    values[column],
                )

        return 1


def patch_publication_base(
    monkeypatch,
    tmp_path,
):
    real_stage = (
        publication_module.stage_generated_site
    )
    real_publish = (
        publication_module.publish_staged_site
    )
    real_publication_lock = (
        publication_module.publication_lock
    )

    def fake_stage_generated_site(
        *,
        pages,
        website_id,
    ):
        return real_stage(
            pages=pages,
            website_id=website_id,
            base_dir=str(tmp_path),
        )

    def fake_publish_staged_site(
        *,
        staging_dir,
        website_id,
    ):
        return real_publish(
            staging_dir=staging_dir,
            website_id=website_id,
            base_dir=str(tmp_path),
        )

    monkeypatch.setattr(
        task_module,
        "stage_generated_site",
        fake_stage_generated_site,
    )

    monkeypatch.setattr(
        task_module,
        "publish_staged_site",
        fake_publish_staged_site,
    )

    def fake_publication_lock(
        *,
        website_id,
    ):
        return real_publication_lock(
            website_id=website_id,
            base_dir=str(tmp_path),
        )

    monkeypatch.setattr(
        task_module,
        "publication_lock",
        fake_publication_lock,
    )


class FakeSession:
    def __init__(self, website):
        self.website = website
        self.commit_count = 0
        self.refresh_count = 0
        self.rollback_count = 0
        self.closed = False

    def query(self, model):
        return FakeQuery(
            self.website
        )

    def commit(self):
        self.commit_count += 1

    def rollback(self):
        self.rollback_count += 1

    def refresh(self, website):
        assert website is self.website
        self.refresh_count += 1

    def close(self):
        self.closed = True


@pytest.mark.unit
def test_generate_website_task_persists_generation_contract(
    monkeypatch,
    tmp_path,
):
    website_id = uuid4()

    website = SimpleNamespace(
        id=website_id,
        user_id=None,
        project_name="Persistence Contract",
        business_type="Pizza Shop",
        prompt="Create a neighborhood pizza website.",
        generation_status="queued",
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

    db = FakeSession(
        website
    )

    profile = {
        "business_name": "Test Pizza",
        "_model": "test-model",
        "_usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
        },
    }

    pages = {
        "index.html": "<html>HOME</html>",
        "about.html": "<html>ABOUT</html>",
        "services.html": "<html>SERVICES</html>",
        "contact.html": "<html>CONTACT</html>",
    }

    profile_calls = []
    page_calls = []

    def fake_generate_business_profile(
        *,
        prompt,
        business_type,
        user_id,
    ):
        profile_calls.append(
            {
                "prompt": prompt,
                "business_type": business_type,
                "user_id": user_id,
            }
        )

        return profile

    def fake_generate_multi_page_site(
        *,
        profile,
        theme,
    ):
        page_calls.append(
            {
                "profile": profile,
                "theme": theme,
            }
        )

        return pages

    monkeypatch.setattr(
        task_module,
        "SessionLocal",
        lambda: db,
    )

    monkeypatch.setattr(
        task_module,
        "generate_business_profile",
        fake_generate_business_profile,
    )

    monkeypatch.setattr(
        task_module,
        "generate_multi_page_site",
        fake_generate_multi_page_site,
    )

    patch_publication_base(
        monkeypatch,
        tmp_path,
    )

    # Call the underlying task function synchronously.
    task_module.generate_website_task.run(
        str(website_id),
        website.business_type,
    )

    assert profile_calls == [
        {
            "prompt": website.prompt,
            "business_type": "Pizza Shop",
            "user_id": "None",
        }
    ]

    assert page_calls == [
        {
            "profile": profile,
            "theme": "modern",
        }
    ]

    assert website.generation_status == "completed"
    assert website.error_message is None

    assert website.metadata_json == {
        "theme": "modern",
        "profile": profile,
        "pages": [
            "index.html",
            "about.html",
            "services.html",
            "contact.html",
        ],
    }

    assert website.html == "<html>HOME</html>"
    assert website.css == ""
    assert website.js == ""

    assert website.gpt_model == "test-model"
    assert website.gpt_tokens_prompt == 100
    assert website.gpt_tokens_completion == 50
    assert website.gpt_tokens_total == 150

    assert website.generated_url == (
        "http://34.27.91.3:8000/generated-sites/"
        f"{website_id}/index.html"
    )

    output_dir = (
        tmp_path
        / "generated_sites"
        / str(website_id)
    )

    for filename, expected in pages.items():
        assert (
            output_dir
            / filename
        ).read_text(
            encoding="utf-8"
        ) == expected

    # generating commit + completed persistence commit
    assert db.commit_count == 2
    assert db.refresh_count == 2
    assert db.closed is True


@pytest.mark.unit
def test_generate_website_task_persists_profile_generation_failure(
    monkeypatch,
):
    website_id = uuid4()

    website = SimpleNamespace(
        id=website_id,
        user_id=None,
        project_name="Profile Failure Contract",
        business_type="Pizza Shop",
        prompt="Create a neighborhood pizza website.",
        generation_status="queued",
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

    db = FakeSession(
        website
    )

    page_generator_called = False

    def fake_generate_business_profile(
        *,
        prompt,
        business_type,
        user_id,
    ):
        raise RuntimeError(
            "profile generation failed"
        )

    def fake_generate_multi_page_site(
        *,
        profile,
        theme,
    ):
        nonlocal page_generator_called
        page_generator_called = True

        raise AssertionError(
            "page generator must not run"
        )

    monkeypatch.setattr(
        task_module,
        "SessionLocal",
        lambda: db,
    )

    monkeypatch.setattr(
        task_module,
        "generate_business_profile",
        fake_generate_business_profile,
    )

    monkeypatch.setattr(
        task_module,
        "generate_multi_page_site",
        fake_generate_multi_page_site,
    )

    with pytest.raises(
        RuntimeError,
        match="profile generation failed",
    ):
        task_module.generate_website_task.run(
            str(website_id),
            website.business_type,
        )

    assert page_generator_called is False

    assert website.generation_status == "failed"
    assert (
        website.error_message
        == "profile generation failed"
    )

    # generating commit + failed commit
    assert db.commit_count == 2

    # Only the generating transition is refreshed.
    assert db.refresh_count == 1

    assert db.closed is True

    # No successful generation output was persisted.
    assert website.html is None
    assert website.css is None
    assert website.js is None
    assert website.generated_url is None

    assert website.gpt_model is None
    assert website.gpt_tokens_prompt is None
    assert website.gpt_tokens_completion is None
    assert website.gpt_tokens_total is None


@pytest.mark.unit
def test_generate_website_task_persists_page_generation_failure(
    monkeypatch,
):
    website_id = uuid4()

    website = SimpleNamespace(
        id=website_id,
        user_id=None,
        project_name="Page Failure Contract",
        business_type="Pizza Shop",
        prompt="Create a neighborhood pizza website.",
        generation_status="queued",
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

    db = FakeSession(
        website
    )

    profile = {
        "business_name": "Test Pizza",
        "_model": "test-model",
        "_usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
        },
    }

    profile_calls = []
    page_calls = []

    def fake_generate_business_profile(
        *,
        prompt,
        business_type,
        user_id,
    ):
        profile_calls.append(
            {
                "prompt": prompt,
                "business_type": business_type,
                "user_id": user_id,
            }
        )

        return profile

    def fake_generate_multi_page_site(
        *,
        profile,
        theme,
    ):
        page_calls.append(
            {
                "profile": profile,
                "theme": theme,
            }
        )

        raise RuntimeError(
            "page generation failed"
        )

    monkeypatch.setattr(
        task_module,
        "SessionLocal",
        lambda: db,
    )

    monkeypatch.setattr(
        task_module,
        "generate_business_profile",
        fake_generate_business_profile,
    )

    monkeypatch.setattr(
        task_module,
        "generate_multi_page_site",
        fake_generate_multi_page_site,
    )

    with pytest.raises(
        RuntimeError,
        match="page generation failed",
    ):
        task_module.generate_website_task.run(
            str(website_id),
            website.business_type,
        )

    assert profile_calls == [
        {
            "prompt": website.prompt,
            "business_type": "Pizza Shop",
            "user_id": "None",
        }
    ]

    assert page_calls == [
        {
            "profile": profile,
            "theme": "modern",
        }
    ]

    assert website.generation_status == "failed"
    assert (
        website.error_message
        == "page generation failed"
    )

    # generating commit + failed commit
    assert db.commit_count == 2

    # No refresh follows the failure commit.
    assert db.refresh_count == 1

    assert db.closed is True

    # Metadata is not replaced until page generation
    # succeeds.
    assert website.metadata_json == {
        "theme": "modern",
    }

    assert website.html is None
    assert website.css is None
    assert website.js is None
    assert website.generated_url is None

    assert website.gpt_model is None
    assert website.gpt_tokens_prompt is None
    assert website.gpt_tokens_completion is None
    assert website.gpt_tokens_total is None


@pytest.mark.unit
def test_generate_website_task_rolls_back_before_persisting_failure(
    monkeypatch,
):
    website_id = uuid4()

    website = SimpleNamespace(
        id=website_id,
        user_id=None,
        project_name="Rollback Failure Contract",
        business_type="Pizza Shop",
        prompt="Create a neighborhood pizza website.",
        generation_status="queued",
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

    class PoisonedSession(FakeSession):
        def __init__(self, website):
            super().__init__(website)
            self.failed_transaction = False
            self.events = []

        def commit(self):
            self.commit_count += 1
            self.events.append("commit")

            # First commit succeeds: queued -> generating.
            if self.commit_count == 1:
                return

            # Once poisoned, a commit is illegal until rollback.
            if self.failed_transaction:
                raise RuntimeError(
                    "transaction is aborted"
                )

        def rollback(self):
            self.rollback_count += 1
            self.events.append("rollback")
            self.failed_transaction = False

    db = PoisonedSession(
        website
    )

    def fake_generate_business_profile(
        *,
        prompt,
        business_type,
        user_id,
    ):
        # Simulate a failure that leaves the DB session
        # in an aborted transaction state.
        db.failed_transaction = True

        raise RuntimeError(
            "database-backed generation failure"
        )

    monkeypatch.setattr(
        task_module,
        "SessionLocal",
        lambda: db,
    )

    monkeypatch.setattr(
        task_module,
        "generate_business_profile",
        fake_generate_business_profile,
    )

    with pytest.raises(
        RuntimeError,
        match="database-backed generation failure",
    ):
        task_module.generate_website_task.run(
            str(website_id),
            website.business_type,
        )

    assert db.rollback_count == 1

    assert website.generation_status == "failed"
    assert (
        website.error_message
        == "database-backed generation failure"
    )

    assert db.closed is True

    # Required ordering:
    # generating commit -> rollback -> failed-state commit
    assert db.events == [
        "commit",
        "rollback",
        "commit",
    ]


@pytest.mark.unit
def test_generate_website_task_rolls_back_before_persisting_failure(
    monkeypatch,
):
    website_id = uuid4()

    website = SimpleNamespace(
        id=website_id,
        user_id=None,
        project_name="Rollback Failure Contract",
        business_type="Pizza Shop",
        prompt="Create a neighborhood pizza website.",
        generation_status="queued",
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

    class PoisonedSession(FakeSession):
        def __init__(self, website):
            super().__init__(website)
            self.failed_transaction = False
            self.events = []

        def commit(self):
            self.commit_count += 1
            self.events.append("commit")

            # First commit succeeds: queued -> generating.
            if self.commit_count == 1:
                return

            # Once poisoned, a commit is illegal until rollback.
            if self.failed_transaction:
                raise RuntimeError(
                    "transaction is aborted"
                )

        def rollback(self):
            self.rollback_count += 1
            self.events.append("rollback")
            self.failed_transaction = False

    db = PoisonedSession(
        website
    )

    def fake_generate_business_profile(
        *,
        prompt,
        business_type,
        user_id,
    ):
        # Simulate a failure that leaves the DB session
        # in an aborted transaction state.
        db.failed_transaction = True

        raise RuntimeError(
            "database-backed generation failure"
        )

    monkeypatch.setattr(
        task_module,
        "SessionLocal",
        lambda: db,
    )

    monkeypatch.setattr(
        task_module,
        "generate_business_profile",
        fake_generate_business_profile,
    )

    with pytest.raises(
        RuntimeError,
        match="database-backed generation failure",
    ):
        task_module.generate_website_task.run(
            str(website_id),
            website.business_type,
        )

    assert db.rollback_count == 1

    assert website.generation_status == "failed"
    assert (
        website.error_message
        == "database-backed generation failure"
    )

    assert db.closed is True

    # Required ordering:
    # generating commit -> rollback -> failed-state commit
    assert db.events == [
        "commit",
        "rollback",
        "commit",
    ]


@pytest.mark.unit
def test_generate_website_task_recovers_from_final_commit_failure(
    monkeypatch,
    tmp_path,
):
    website_id = uuid4()

    website = SimpleNamespace(
        id=website_id,
        user_id=None,
        project_name="Final Commit Failure Contract",
        business_type="Pizza Shop",
        prompt="Create a neighborhood pizza website.",
        generation_status="queued",
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

    class FinalCommitFailureSession(FakeSession):
        def __init__(self, website):
            super().__init__(website)
            self.events = []
            self.failure_commit_attempted = False

        def commit(self):
            self.commit_count += 1
            self.events.append("commit")

            # First commit succeeds:
            # queued -> generating.
            if self.commit_count == 1:
                return

            # Second commit is the intended
            # completed-state persistence and fails.
            if (
                self.commit_count == 2
                and not self.failure_commit_attempted
            ):
                self.failure_commit_attempted = True

                raise RuntimeError(
                    "final persistence commit failed"
                )

            # Third commit is the failed-state commit
            # after rollback and must succeed.
            return

        def rollback(self):
            self.rollback_count += 1
            self.events.append("rollback")

    db = FinalCommitFailureSession(
        website
    )

    profile = {
        "business_name": "Test Pizza",
        "_model": "test-model",
        "_usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
        },
    }

    pages = {
        "index.html": "<html>HOME</html>",
        "about.html": "<html>ABOUT</html>",
        "services.html": "<html>SERVICES</html>",
        "contact.html": "<html>CONTACT</html>",
    }

    def fake_generate_business_profile(
        *,
        prompt,
        business_type,
        user_id,
    ):
        return profile

    def fake_generate_multi_page_site(
        *,
        profile,
        theme,
    ):
        return pages

    monkeypatch.setattr(
        task_module,
        "SessionLocal",
        lambda: db,
    )

    monkeypatch.setattr(
        task_module,
        "generate_business_profile",
        fake_generate_business_profile,
    )

    monkeypatch.setattr(
        task_module,
        "generate_multi_page_site",
        fake_generate_multi_page_site,
    )

    patch_publication_base(
        monkeypatch,
        tmp_path,
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

    assert website.generation_status == "failed"
    assert (
        website.error_message
        == "final persistence commit failed"
    )

    assert db.closed is True

    # generating commit
    # -> failed completed-state commit
    # -> rollback
    # -> failed-state commit
    assert db.events == [
        "commit",
        "commit",
        "rollback",
        "commit",
    ]

    assert db.commit_count == 3

    # Rendering and assignment happened before the
    # persistence failure, so in-memory values exist.
    assert website.html == "<html>HOME</html>"
    assert website.css == ""
    assert website.js == ""

    assert website.gpt_model == "test-model"
    assert website.gpt_tokens_prompt == 100
    assert website.gpt_tokens_completion == 50
    assert website.gpt_tokens_total == 150

    assert website.generated_url == (
        "http://34.27.91.3:8000/generated-sites/"
        f"{website_id}/index.html"
    )

    # A failed generation must not leave publicly
    # addressable output behind.
    output_dir = (
        tmp_path
        / "generated_sites"
        / str(website_id)
    )

    assert not output_dir.exists()




@pytest.mark.unit
def test_generate_website_task_never_publishes_partial_site(
    monkeypatch,
    tmp_path,
):
    website_id = uuid4()

    website = SimpleNamespace(
        id=website_id,
        user_id=None,
        project_name="Partial Publication Contract",
        business_type="Pizza Shop",
        prompt="Create a neighborhood pizza website.",
        generation_status="queued",
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

    db = FakeSession(
        website
    )

    profile = {
        "business_name": "Test Pizza",
        "_model": "test-model",
        "_usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
        },
    }

    pages = {
        "index.html": "<html>HOME</html>",
        "about.html": "<html>ABOUT</html>",
        "services.html": "<html>SERVICES</html>",
    }

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

    def failing_stage_generated_site(
        *,
        pages,
        website_id,
    ):
        raise OSError(
            "simulated page write failure"
        )

    monkeypatch.setattr(
        task_module,
        "stage_generated_site",
        failing_stage_generated_site,
    )

    with pytest.raises(
        OSError,
        match="simulated page write failure",
    ):
        task_module.generate_website_task.run(
            str(website_id),
            website.business_type,
        )

    public_dir = (
        tmp_path
        / "generated_sites"
        / str(website_id)
    )

    assert not public_dir.exists()

    assert website.generation_status == "failed"
    assert (
        website.error_message
        == "simulated page write failure"
    )

    assert db.rollback_count == 1
    assert db.closed is True


@pytest.mark.unit
def test_generate_website_task_does_not_fail_after_completed_commit(
    monkeypatch,
):
    monkeypatch.setattr(
        task_module,
        "publication_lock",
        lambda **kwargs: nullcontext(),
    )

    website_id = uuid4()

    website = SimpleNamespace(
        id=website_id,
        user_id=None,
        project_name="Post Commit Finalization Contract",
        business_type="Pizza Shop",
        prompt="Create a neighborhood pizza website.",
        generation_status="queued",
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

    class TrackingSession(FakeSession):
        def __init__(self, website):
            super().__init__(website)
            self.events = []

        def commit(self):
            self.commit_count += 1
            self.events.append("commit")

        def rollback(self):
            self.rollback_count += 1
            self.events.append("rollback")

    db = TrackingSession(
        website
    )

    profile = {
        "business_name": "Test Pizza",
        "_model": "test-model",
        "_usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
        },
    }

    pages = {
        "index.html": "<html>HOME</html>",
    }

    publication_state = SimpleNamespace(
        public_dir=None,
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
        lambda **kwargs: "staging-dir",
    )

    monkeypatch.setattr(
        task_module,
        "publish_staged_site",
        lambda **kwargs: publication_state,
    )

    def failing_finalize_publication(
        state,
    ):
        assert state is publication_state

        raise OSError(
            "backup cleanup failed"
        )

    monkeypatch.setattr(
        task_module,
        "finalize_publication",
        failing_finalize_publication,
    )

    rollback_publication_called = False

    def fake_rollback_publication(
        state,
    ):
        nonlocal rollback_publication_called
        rollback_publication_called = True

    monkeypatch.setattr(
        task_module,
        "rollback_publication",
        fake_rollback_publication,
    )

    # Once the completed-state transaction has committed,
    # best-effort backup cleanup must not convert the
    # generation into a failed generation.
    task_module.generate_website_task.run(
        str(website_id),
        website.business_type,
    )

    assert website.generation_status == "completed"
    assert website.error_message is None

    assert db.commit_count == 2
    assert db.rollback_count == 0
    assert db.events == [
        "commit",
        "commit",
    ]

    assert rollback_publication_called is False
    assert db.closed is True


@pytest.mark.unit
def test_generate_website_task_does_not_fail_after_completed_commit_refresh(
    monkeypatch,
):
    monkeypatch.setattr(
        task_module,
        "publication_lock",
        lambda **kwargs: nullcontext(),
    )

    website_id = uuid4()

    website = SimpleNamespace(
        id=website_id,
        user_id=None,
        project_name="Post Commit Refresh Contract",
        business_type="Pizza Shop",
        prompt="Create a neighborhood pizza website.",
        generation_status="queued",
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

    class PostCommitRefreshFailureSession(
        FakeSession
    ):
        def __init__(self, website):
            super().__init__(website)
            self.events = []

        def commit(self):
            self.commit_count += 1
            self.events.append("commit")

        def refresh(self, website):
            assert website is self.website

            self.refresh_count += 1
            self.events.append("refresh")

            # First refresh follows the generating commit.
            if self.refresh_count == 1:
                return

            # Second refresh occurs only after the
            # completed-state transaction committed.
            raise RuntimeError(
                "post-commit refresh failed"
            )

        def rollback(self):
            self.rollback_count += 1
            self.events.append("rollback")

    db = PostCommitRefreshFailureSession(
        website
    )

    profile = {
        "business_name": "Test Pizza",
        "_model": "test-model",
        "_usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
        },
    }

    pages = {
        "index.html": "<html>HOME</html>",
    }

    publication_state = SimpleNamespace(
        public_dir=None,
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
        lambda **kwargs: "staging-dir",
    )

    monkeypatch.setattr(
        task_module,
        "publish_staged_site",
        lambda **kwargs: publication_state,
    )

    finalize_called = False

    def fake_finalize_publication(
        state,
    ):
        nonlocal finalize_called

        assert state is publication_state
        finalize_called = True

    monkeypatch.setattr(
        task_module,
        "finalize_publication",
        fake_finalize_publication,
    )

    rollback_publication_called = False

    def fake_rollback_publication(
        state,
    ):
        nonlocal rollback_publication_called
        rollback_publication_called = True

    monkeypatch.setattr(
        task_module,
        "rollback_publication",
        fake_rollback_publication,
    )

    # The completed-state commit is the success boundary.
    # A refresh failure after that point must not convert
    # the generation into failure or undo publication.
    task_module.generate_website_task.run(
        str(website_id),
        website.business_type,
    )

    assert website.generation_status == "completed"
    assert website.error_message is None

    assert db.commit_count == 2
    assert db.refresh_count == 2
    assert db.rollback_count == 0

    assert db.events == [
        "commit",
        "refresh",
        "commit",
        "refresh",
    ]

    assert rollback_publication_called is False

    # Backup cleanup must still be attempted even when
    # the optional post-commit refresh fails.
    assert finalize_called is True

    assert db.closed is True


@pytest.mark.unit
def test_generate_website_task_skips_already_completed_website(
    monkeypatch,
):
    website_id = uuid4()

    website = SimpleNamespace(
        id=website_id,
        user_id=None,
        project_name="Completed Idempotency Contract",
        business_type="Pizza Shop",
        prompt="Create a neighborhood pizza website.",
        generation_status="completed",
        error_message=None,
        metadata_json={
            "theme": "modern",
            "profile": {
                "business_name": "Existing Pizza",
            },
            "pages": [
                "index.html",
            ],
        },
        html="<html>EXISTING</html>",
        css="",
        js="",
        generated_url=(
            "http://34.27.91.3:8000/generated-sites/"
            f"{website_id}/index.html"
        ),
        gpt_model="existing-model",
        gpt_tokens_prompt=100,
        gpt_tokens_completion=50,
        gpt_tokens_total=150,
    )

    db = FakeSession(
        website
    )

    generation_called = False
    rendering_called = False
    staging_called = False
    publication_called = False

    def fail_generate_business_profile(
        **kwargs,
    ):
        nonlocal generation_called
        generation_called = True

        raise AssertionError(
            "Completed website must not be regenerated."
        )

    def fail_generate_multi_page_site(
        **kwargs,
    ):
        nonlocal rendering_called
        rendering_called = True

        raise AssertionError(
            "Completed website must not be rendered again."
        )

    def fail_stage_generated_site(
        **kwargs,
    ):
        nonlocal staging_called
        staging_called = True

        raise AssertionError(
            "Completed website must not be staged again."
        )

    def fail_publish_staged_site(
        **kwargs,
    ):
        nonlocal publication_called
        publication_called = True

        raise AssertionError(
            "Completed website must not be published again."
        )

    monkeypatch.setattr(
        task_module,
        "SessionLocal",
        lambda: db,
    )

    monkeypatch.setattr(
        task_module,
        "generate_business_profile",
        fail_generate_business_profile,
    )

    monkeypatch.setattr(
        task_module,
        "generate_multi_page_site",
        fail_generate_multi_page_site,
    )

    monkeypatch.setattr(
        task_module,
        "stage_generated_site",
        fail_stage_generated_site,
    )

    monkeypatch.setattr(
        task_module,
        "publish_staged_site",
        fail_publish_staged_site,
    )

    original_metadata = website.metadata_json.copy()
    original_html = website.html
    original_url = website.generated_url
    original_model = website.gpt_model
    original_total_tokens = website.gpt_tokens_total

    task_module.generate_website_task.run(
        str(website_id),
        website.business_type,
    )

    assert generation_called is False
    assert rendering_called is False
    assert staging_called is False
    assert publication_called is False

    assert website.generation_status == "completed"
    assert website.error_message is None

    assert website.metadata_json == original_metadata
    assert website.html == original_html
    assert website.generated_url == original_url
    assert website.gpt_model == original_model
    assert (
        website.gpt_tokens_total
        == original_total_tokens
    )

    # A duplicate delivery must not create a new
    # persistence transaction for completed work.
    assert db.commit_count == 0
    assert db.rollback_count == 0

    assert db.closed is True


@pytest.mark.unit
def test_generate_website_task_skips_already_generating_website(
    monkeypatch,
):
    from datetime import datetime, timedelta, timezone

    website_id = uuid4()

    now = datetime(
        2026,
        9,
        16,
        12,
        0,
        0,
        tzinfo=timezone.utc,
    )

    recent_started_at = (
        now
        - timedelta(minutes=5)
    )

    website = SimpleNamespace(
        id=website_id,
        user_id=None,
        project_name="Generating Idempotency Contract",
        business_type="Pizza Shop",
        prompt="Create a neighborhood pizza website.",
        generation_status="generating",
        generation_started_at=recent_started_at,
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

    db = FakeSession(
        website
    )

    generation_called = False
    rendering_called = False
    staging_called = False
    publication_called = False

    def fail_generate_business_profile(
        **kwargs,
    ):
        nonlocal generation_called
        generation_called = True

        raise AssertionError(
            "Active generation must not be duplicated."
        )

    def fail_generate_multi_page_site(
        **kwargs,
    ):
        nonlocal rendering_called
        rendering_called = True

        raise AssertionError(
            "Active generation must not be rendered twice."
        )

    def fail_stage_generated_site(
        **kwargs,
    ):
        nonlocal staging_called
        staging_called = True

        raise AssertionError(
            "Active generation must not be staged twice."
        )

    def fail_publish_staged_site(
        **kwargs,
    ):
        nonlocal publication_called
        publication_called = True

        raise AssertionError(
            "Active generation must not be published twice."
        )

    monkeypatch.setattr(
        task_module,
        "SessionLocal",
        lambda: db,
    )

    monkeypatch.setattr(
        task_module,
        "utc_now",
        lambda: now,
        raising=False,
    )

    monkeypatch.setattr(
        task_module,
        "generate_business_profile",
        fail_generate_business_profile,
    )

    monkeypatch.setattr(
        task_module,
        "generate_multi_page_site",
        fail_generate_multi_page_site,
    )

    monkeypatch.setattr(
        task_module,
        "stage_generated_site",
        fail_stage_generated_site,
    )

    monkeypatch.setattr(
        task_module,
        "publish_staged_site",
        fail_publish_staged_site,
    )

    task_module.generate_website_task.run(
        str(website_id),
        website.business_type,
    )

    assert website.generation_status == "generating"

    assert generation_called is False
    assert rendering_called is False
    assert staging_called is False
    assert publication_called is False

    assert db.commit_count == 0
    assert db.refresh_count == 0
    assert db.rollback_count == 0
    assert db.closed is True


@pytest.mark.unit
def test_generate_website_task_recovers_stale_generating_website(
    monkeypatch,
):
    monkeypatch.setattr(
        task_module,
        "publication_lock",
        lambda **kwargs: nullcontext(),
    )

    from datetime import datetime, timedelta, timezone

    website_id = uuid4()

    now = datetime(
        2026,
        9,
        16,
        12,
        0,
        0,
        tzinfo=timezone.utc,
    )

    stale_started_at = (
        now
        - timedelta(hours=2)
    )

    website = SimpleNamespace(
        id=website_id,
        user_id=None,
        project_name="Stale Generation Recovery Contract",
        business_type="Pizza Shop",
        prompt="Create a neighborhood pizza website.",
        generation_status="generating",
        generation_started_at=stale_started_at,
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

    db = FakeSession(
        website
    )

    generation_called = False

    def fake_generate_business_profile(
        **kwargs,
    ):
        nonlocal generation_called
        generation_called = True

        return {
            "business_name": "Recovered Pizza",
            "_model": "test-model",
            "_usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150,
            },
        }

    monkeypatch.setattr(
        task_module,
        "SessionLocal",
        lambda: db,
    )

    monkeypatch.setattr(
        task_module,
        "utc_now",
        lambda: now,
        raising=False,
    )

    monkeypatch.setattr(
        task_module,
        "generate_business_profile",
        fake_generate_business_profile,
    )

    monkeypatch.setattr(
        task_module,
        "generate_multi_page_site",
        lambda **kwargs: {
            "index.html": "<html>RECOVERED</html>",
        },
    )

    publication_state = SimpleNamespace(
        public_dir=None,
        backup_dir=None,
    )

    monkeypatch.setattr(
        task_module,
        "stage_generated_site",
        lambda **kwargs: "staging-dir",
    )

    monkeypatch.setattr(
        task_module,
        "publish_staged_site",
        lambda **kwargs: publication_state,
    )

    monkeypatch.setattr(
        task_module,
        "finalize_publication",
        lambda state: None,
    )

    # A generation lease that is older than the allowed
    # recovery window must not permanently block the site.
    #
    # This is intentionally a RED contract. The task does
    # not yet have generation_started_at lease semantics.
    task_module.generate_website_task.run(
        str(website_id),
        website.business_type,
    )

    assert generation_called is True


@pytest.mark.unit
def test_generate_website_task_claims_generation_lease(
    monkeypatch,
):
    monkeypatch.setattr(
        task_module,
        "publication_lock",
        lambda **kwargs: nullcontext(),
    )

    from datetime import datetime, timezone

    website_id = uuid4()

    now = datetime(
        2026,
        9,
        16,
        12,
        0,
        0,
        tzinfo=timezone.utc,
    )

    website = SimpleNamespace(
        id=website_id,
        user_id=None,
        project_name="Generation Lease Claim Contract",
        business_type="Pizza Shop",
        prompt="Create a neighborhood pizza website.",
        generation_status="queued",
        generation_started_at=None,
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

    class LeaseClaimSession(
        FakeSession
    ):
        def __init__(self, website):
            super().__init__(website)
            self.claimed_started_at = None
            self.claimed_status = None

        def commit(self):
            self.commit_count += 1

            # Capture the first persistence boundary:
            # this is where the generation lease must
            # already have been established.
            if self.commit_count == 1:
                self.claimed_status = (
                    self.website.generation_status
                )
                self.claimed_started_at = (
                    self.website.generation_started_at
                )

    db = LeaseClaimSession(
        website
    )

    profile = {
        "business_name": "Lease Pizza",
        "_model": "test-model",
        "_usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
        },
    }

    publication_state = SimpleNamespace(
        public_dir=None,
        backup_dir=None,
    )

    monkeypatch.setattr(
        task_module,
        "SessionLocal",
        lambda: db,
    )

    monkeypatch.setattr(
        task_module,
        "utc_now",
        lambda: now,
    )

    monkeypatch.setattr(
        task_module,
        "generate_business_profile",
        lambda **kwargs: profile,
    )

    monkeypatch.setattr(
        task_module,
        "generate_multi_page_site",
        lambda **kwargs: {
            "index.html": "<html>LEASE</html>",
        },
    )

    monkeypatch.setattr(
        task_module,
        "stage_generated_site",
        lambda **kwargs: "staging-dir",
    )

    monkeypatch.setattr(
        task_module,
        "publish_staged_site",
        lambda **kwargs: publication_state,
    )

    monkeypatch.setattr(
        task_module,
        "finalize_publication",
        lambda state: None,
    )

    task_module.generate_website_task.run(
        str(website_id),
        website.business_type,
    )

    assert db.claimed_status == "generating"
    assert db.claimed_started_at == now

    # The lease existed at the claim persistence
    # boundary above, but successful completion releases
    # it before the terminal completed-state commit.
    assert website.generation_status == "completed"
    assert website.generation_started_at is None
    assert website.generation_status == "completed"

    # First commit claims the lease.
    # Second commit persists completed generation.
    assert db.commit_count == 2
    assert db.closed is True


@pytest.mark.unit
def test_generate_website_task_clears_generation_lease_on_success(
    monkeypatch,
):
    monkeypatch.setattr(
        task_module,
        "publication_lock",
        lambda **kwargs: nullcontext(),
    )

    from datetime import datetime, timezone

    website_id = uuid4()

    now = datetime(
        2026,
        9,
        16,
        12,
        0,
        0,
        tzinfo=timezone.utc,
    )

    website = SimpleNamespace(
        id=website_id,
        user_id=None,
        project_name="Successful Lease Release Contract",
        business_type="Pizza Shop",
        prompt="Create a neighborhood pizza website.",
        generation_status="queued",
        generation_started_at=None,
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

    db = FakeSession(
        website
    )

    profile = {
        "business_name": "Lease Pizza",
        "_model": "test-model",
        "_usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
        },
    }

    pages = {
        "index.html": "<html>HOME</html>",
    }

    publication_state = SimpleNamespace(
        public_dir=None,
        backup_dir=None,
    )

    monkeypatch.setattr(
        task_module,
        "SessionLocal",
        lambda: db,
    )

    monkeypatch.setattr(
        task_module,
        "utc_now",
        lambda: now,
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
        lambda **kwargs: "staging-dir",
    )

    monkeypatch.setattr(
        task_module,
        "publish_staged_site",
        lambda **kwargs: publication_state,
    )

    monkeypatch.setattr(
        task_module,
        "finalize_publication",
        lambda state: None,
    )

    task_module.generate_website_task.run(
        str(website_id),
        website.business_type,
    )

    assert website.generation_status == "completed"

    # Terminal success releases the generation lease.
    assert website.generation_started_at is None

    assert db.closed is True


@pytest.mark.unit
def test_generate_website_task_clears_generation_lease_on_failure(
    monkeypatch,
):
    from datetime import datetime, timezone

    website_id = uuid4()

    now = datetime(
        2026,
        9,
        16,
        12,
        0,
        0,
        tzinfo=timezone.utc,
    )

    website = SimpleNamespace(
        id=website_id,
        user_id=None,
        project_name="Failed Lease Release Contract",
        business_type="Pizza Shop",
        prompt="Create a neighborhood pizza website.",
        generation_status="queued",
        generation_started_at=None,
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

    db = FakeSession(
        website
    )

    monkeypatch.setattr(
        task_module,
        "SessionLocal",
        lambda: db,
    )

    monkeypatch.setattr(
        task_module,
        "utc_now",
        lambda: now,
    )

    def failing_generate_business_profile(
        **kwargs,
    ):
        raise RuntimeError(
            "simulated generation failure"
        )

    monkeypatch.setattr(
        task_module,
        "generate_business_profile",
        failing_generate_business_profile,
    )

    with pytest.raises(
        RuntimeError,
        match="simulated generation failure",
    ):
        task_module.generate_website_task.run(
            str(website_id),
            website.business_type,
        )

    assert website.generation_status == "failed"

    assert (
        website.error_message
        == "simulated generation failure"
    )

    # Terminal failure releases the generation lease.
    assert website.generation_started_at is None

    assert db.rollback_count == 1

    # Lease claim + failed-state persistence.
    assert db.commit_count == 2

    assert db.closed is True


@pytest.mark.unit
def test_generate_website_task_requires_atomic_lease_claim(
    monkeypatch,
):
    from datetime import datetime, timezone

    website_id = uuid4()

    now = datetime(
        2026,
        9,
        16,
        12,
        0,
        0,
        tzinfo=timezone.utc,
    )

    website = SimpleNamespace(
        id=website_id,
        user_id=None,
        project_name="Atomic Lease Claim Contract",
        business_type="Pizza Shop",
        prompt="Create a neighborhood pizza website.",
        generation_status="queued",
        generation_started_at=None,
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

    db = FakeSession(
        website
    )

    generation_called = False
    atomic_claim_called = False

    def fake_claim_generation_lease(
        *,
        db,
        website_id,
        now,
        attempt_id,
    ):
        nonlocal atomic_claim_called

        atomic_claim_called = True

        # Simulate losing the atomic database race to
        # another worker.
        return False

    def fail_generate_business_profile(
        **kwargs,
    ):
        nonlocal generation_called

        generation_called = True

        raise AssertionError(
            "Generation must not begin when the "
            "atomic generation lease claim is lost."
        )

    monkeypatch.setattr(
        task_module,
        "SessionLocal",
        lambda: db,
    )

    monkeypatch.setattr(
        task_module,
        "utc_now",
        lambda: now,
    )

    monkeypatch.setattr(
        task_module,
        "claim_generation_lease",
        fake_claim_generation_lease,
        raising=False,
    )

    monkeypatch.setattr(
        task_module,
        "generate_business_profile",
        fail_generate_business_profile,
    )

    task_module.generate_website_task.run(
        str(website_id),
        website.business_type,
    )

    assert atomic_claim_called is True
    assert generation_called is False

    # Losing the lease is an idempotent no-op, not a
    # generation failure.
    assert website.generation_status == "queued"
    assert website.generation_started_at is None

    assert db.rollback_count == 0
    assert db.closed is True


@pytest.mark.unit
def test_claim_generation_lease_commits_only_when_claim_wins():
    from datetime import datetime, timezone

    now = datetime(
        2026,
        9,
        16,
        12,
        0,
        0,
        tzinfo=timezone.utc,
    )

    website_id = uuid4()

    class AtomicClaimQuery:
        def __init__(self):
            self.filters = None
            self.values = None
            self.synchronize_session = None

        def filter(self, *expressions):
            self.filters = expressions
            return self

        def update(
            self,
            values,
            synchronize_session=None,
        ):
            self.values = values
            self.synchronize_session = (
                synchronize_session
            )
            return 1

    class AtomicClaimSession:
        def __init__(self):
            self.query_object = AtomicClaimQuery()
            self.commit_count = 0
            self.rollback_count = 0

        def query(self, model):
            assert model is task_module.GeneratedSite
            return self.query_object

        def commit(self):
            self.commit_count += 1

        def rollback(self):
            self.rollback_count += 1

    db = AtomicClaimSession()

    claimed = task_module.claim_generation_lease(
        db=db,
        website_id=str(website_id),
        now=now,
    )

    assert claimed is True
    assert db.commit_count == 1
    assert db.rollback_count == 0

    query = db.query_object

    # ID + completed exclusion + active/stale lease
    # eligibility expression.
    assert len(query.filters) == 3

    assert (
        query.values[
            task_module.GeneratedSite.generation_status
        ]
        == "generating"
    )

    assert (
        query.values[
            task_module.GeneratedSite.generation_started_at
        ]
        == now
    )

    assert query.synchronize_session is False


@pytest.mark.unit
def test_claim_generation_lease_rolls_back_when_claim_loses():
    from datetime import datetime, timezone

    now = datetime(
        2026,
        9,
        16,
        12,
        0,
        0,
        tzinfo=timezone.utc,
    )

    website_id = uuid4()

    class LostClaimQuery:
        def filter(self, *expressions):
            return self

        def update(
            self,
            values,
            synchronize_session=None,
        ):
            # PostgreSQL affected no row because another
            # worker owns the active lease, the website
            # completed, or the record disappeared.
            return 0

    class LostClaimSession:
        def __init__(self):
            self.commit_count = 0
            self.rollback_count = 0

        def query(self, model):
            assert model is task_module.GeneratedSite
            return LostClaimQuery()

        def commit(self):
            self.commit_count += 1

        def rollback(self):
            self.rollback_count += 1

    db = LostClaimSession()

    claimed = task_module.claim_generation_lease(
        db=db,
        website_id=str(website_id),
        now=now,
    )

    assert claimed is False
    assert db.commit_count == 0
    assert db.rollback_count == 1




@pytest.mark.unit
def test_generate_website_task_does_not_fail_after_completed_commit_close(
    monkeypatch,
):
    monkeypatch.setattr(
        task_module,
        "publication_lock",
        lambda **kwargs: nullcontext(),
    )

    website_id = uuid4()

    website = SimpleNamespace(
        id=website_id,
        user_id=None,
        project_name="Post Commit Close Contract",
        business_type="Pizza Shop",
        prompt="Create a neighborhood pizza website.",
        generation_status="queued",
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

    class PostCommitCloseFailureSession(FakeSession):
        def __init__(self, website):
            super().__init__(website)
            self.close_count = 0

        def close(self):
            self.close_count += 1
            self.closed = True
            raise OSError(
                "post-commit database close failed"
            )

    db = PostCommitCloseFailureSession(
        website
    )

    profile = {
        "business_name": "Test Pizza",
        "_model": "test-model",
        "_usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
        },
    }

    pages = {
        "index.html": "<html>HOME</html>",
    }

    publication_state = SimpleNamespace(
        public_dir=None,
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
        lambda **kwargs: "staging-dir",
    )

    monkeypatch.setattr(
        task_module,
        "publish_staged_site",
        lambda **kwargs: publication_state,
    )

    finalize_called = False

    def fake_finalize_publication(state):
        nonlocal finalize_called
        assert state is publication_state
        finalize_called = True

    monkeypatch.setattr(
        task_module,
        "finalize_publication",
        fake_finalize_publication,
    )

    rollback_publication_called = False

    def fake_rollback_publication(state):
        nonlocal rollback_publication_called
        rollback_publication_called = True

    monkeypatch.setattr(
        task_module,
        "rollback_publication",
        fake_rollback_publication,
    )

    # The completed-state commit is authoritative. A session
    # close failure after that boundary is cleanup failure only.
    task_module.generate_website_task.run(
        str(website_id),
        website.business_type,
    )

    assert website.generation_status == "completed"
    assert website.error_message is None

    assert db.commit_count == 2
    assert db.rollback_count == 0
    assert db.close_count == 1
    assert db.closed is True

    assert finalize_called is True
    assert rollback_publication_called is False
