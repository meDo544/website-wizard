import pytest

from backend.services.website_publication import (
    cleanup_staging,
    finalize_publication,
    publish_staged_site,
    rollback_publication,
    stage_generated_site,
)


@pytest.mark.unit
def test_stage_generated_site_is_not_public(
    tmp_path,
):
    pages = {
        "index.html": "<html>HOME</html>",
        "about.html": "<html>ABOUT</html>",
    }

    staging_dir = stage_generated_site(
        pages=pages,
        website_id="site-1",
        base_dir=str(tmp_path),
    )

    public_dir = (
        tmp_path
        / "generated_sites"
        / "site-1"
    )

    assert staging_dir.exists()
    assert not public_dir.exists()

    assert (
        staging_dir
        / "index.html"
    ).read_text(
        encoding="utf-8"
    ) == "<html>HOME</html>"

    assert (
        staging_dir
        / "about.html"
    ).read_text(
        encoding="utf-8"
    ) == "<html>ABOUT</html>"

    cleanup_staging(
        staging_dir
    )

    assert not staging_dir.exists()


@pytest.mark.unit
def test_publish_staged_site_makes_complete_site_public(
    tmp_path,
):
    pages = {
        "index.html": "<html>HOME</html>",
        "about.html": "<html>ABOUT</html>",
    }

    staging_dir = stage_generated_site(
        pages=pages,
        website_id="site-1",
        base_dir=str(tmp_path),
    )

    state = publish_staged_site(
        staging_dir=staging_dir,
        website_id="site-1",
        base_dir=str(tmp_path),
    )

    assert not staging_dir.exists()
    assert state.public_dir.exists()

    assert (
        state.public_dir
        / "index.html"
    ).read_text(
        encoding="utf-8"
    ) == "<html>HOME</html>"

    assert (
        state.public_dir
        / "about.html"
    ).read_text(
        encoding="utf-8"
    ) == "<html>ABOUT</html>"

    assert state.backup_dir is None

    finalize_publication(
        state
    )


@pytest.mark.unit
def test_rollback_publication_removes_new_site(
    tmp_path,
):
    staging_dir = stage_generated_site(
        pages={
            "index.html": "NEW",
        },
        website_id="site-1",
        base_dir=str(tmp_path),
    )

    state = publish_staged_site(
        staging_dir=staging_dir,
        website_id="site-1",
        base_dir=str(tmp_path),
    )

    assert state.public_dir.exists()

    rollback_publication(
        state
    )

    assert not state.public_dir.exists()


@pytest.mark.unit
def test_rollback_publication_restores_previous_site(
    tmp_path,
):
    public_dir = (
        tmp_path
        / "generated_sites"
        / "site-1"
    )

    public_dir.mkdir(
        parents=True,
    )

    (
        public_dir
        / "index.html"
    ).write_text(
        "OLD",
        encoding="utf-8",
    )

    staging_dir = stage_generated_site(
        pages={
            "index.html": "NEW",
        },
        website_id="site-1",
        base_dir=str(tmp_path),
    )

    state = publish_staged_site(
        staging_dir=staging_dir,
        website_id="site-1",
        base_dir=str(tmp_path),
    )

    assert state.backup_dir is not None
    assert state.backup_dir.exists()

    assert (
        public_dir
        / "index.html"
    ).read_text(
        encoding="utf-8"
    ) == "NEW"

    rollback_publication(
        state
    )

    assert (
        public_dir
        / "index.html"
    ).read_text(
        encoding="utf-8"
    ) == "OLD"

    assert not state.backup_dir.exists()


@pytest.mark.unit
def test_finalize_publication_discards_previous_backup(
    tmp_path,
):
    public_dir = (
        tmp_path
        / "generated_sites"
        / "site-1"
    )

    public_dir.mkdir(
        parents=True,
    )

    (
        public_dir
        / "index.html"
    ).write_text(
        "OLD",
        encoding="utf-8",
    )

    staging_dir = stage_generated_site(
        pages={
            "index.html": "NEW",
        },
        website_id="site-1",
        base_dir=str(tmp_path),
    )

    state = publish_staged_site(
        staging_dir=staging_dir,
        website_id="site-1",
        base_dir=str(tmp_path),
    )

    backup_dir = state.backup_dir

    assert backup_dir is not None
    assert backup_dir.exists()

    finalize_publication(
        state
    )

    assert not backup_dir.exists()

    assert (
        public_dir
        / "index.html"
    ).read_text(
        encoding="utf-8"
    ) == "NEW"


@pytest.mark.unit
def test_staging_failure_removes_partial_staging_directory(
    monkeypatch,
    tmp_path,
):
    from pathlib import Path

    real_write_text = Path.write_text
    write_count = 0

    def failing_write_text(
        self,
        data,
        *args,
        **kwargs,
    ):
        nonlocal write_count

        write_count += 1

        if write_count == 2:
            raise OSError(
                "simulated staging write failure"
            )

        return real_write_text(
            self,
            data,
            *args,
            **kwargs,
        )

    monkeypatch.setattr(
        Path,
        "write_text",
        failing_write_text,
    )

    with pytest.raises(
        OSError,
        match="simulated staging write failure",
    ):
        stage_generated_site(
            pages={
                "index.html": "HOME",
                "about.html": "ABOUT",
            },
            website_id="site-1",
            base_dir=str(tmp_path),
        )

    staging_root = (
        tmp_path
        / ".generated_sites_staging"
    )

    assert staging_root.exists()
    assert list(
        staging_root.iterdir()
    ) == []

    public_dir = (
        tmp_path
        / "generated_sites"
        / "site-1"
    )

    assert not public_dir.exists()


@pytest.mark.unit
@pytest.mark.parametrize(
    "filename",
    [
        "../outside.html",
        "../../outside.html",
        "/tmp/outside.html",
    ],
)
def test_stage_generated_site_rejects_unsafe_page_paths(
    tmp_path,
    filename,
):
    pages = {
        filename: "<html>UNSAFE</html>",
    }

    with pytest.raises(
        ValueError,
        match="Unsafe generated page path",
    ):
        stage_generated_site(
            pages=pages,
            website_id="site-unsafe",
            base_dir=str(tmp_path),
        )

    # Rejected input must never become public.
    public_dir = (
        tmp_path
        / "generated_sites"
        / "site-unsafe"
    )

    assert not public_dir.exists()

    # Failed staging must not leave a per-site
    # staging directory behind.
    staging_root = (
        tmp_path
        / ".generated_sites_staging"
    )

    if staging_root.exists():
        assert list(
            staging_root.iterdir()
        ) == []


@pytest.mark.unit
def test_stage_generated_site_allows_safe_nested_page_paths(
    tmp_path,
):
    pages = {
        "index.html": "<html>HOME</html>",
        "about/index.html": "<html>ABOUT</html>",
        "products/widget.html": "<html>WIDGET</html>",
    }

    staging_dir = stage_generated_site(
        pages=pages,
        website_id="site-nested",
        base_dir=str(tmp_path),
    )

    try:
        for filename, expected in pages.items():
            file_path = (
                staging_dir
                / filename
            )

            assert file_path.is_file()

            assert (
                file_path.read_text(
                    encoding="utf-8",
                )
                == expected
            )

        public_dir = (
            tmp_path
            / "generated_sites"
            / "site-nested"
        )

        assert not public_dir.exists()

    finally:
        cleanup_staging(
            staging_dir
        )

    assert not staging_dir.exists()


@pytest.mark.unit
@pytest.mark.parametrize(
    "filename",
    [
        r"..\outside.html",
        r"folder\outside.html",
        r"C:\temp\outside.html",
    ],
)
def test_stage_generated_site_rejects_backslash_page_paths(
    tmp_path,
    filename,
):
    pages = {
        filename: "<html>UNSAFE</html>",
    }

    with pytest.raises(
        ValueError,
        match="Unsafe generated page path",
    ):
        stage_generated_site(
            pages=pages,
            website_id="site-backslash",
            base_dir=str(tmp_path),
        )

    public_dir = (
        tmp_path
        / "generated_sites"
        / "site-backslash"
    )

    assert not public_dir.exists()

    staging_root = (
        tmp_path
        / ".generated_sites_staging"
    )

    if staging_root.exists():
        assert list(
            staging_root.iterdir()
        ) == []


@pytest.mark.unit
@pytest.mark.parametrize(
    "website_id",
    [
        "../outside",
        "../../outside",
        "/tmp/outside",
        r"..\outside",
        r"C:\temp\outside",
        "site/child",
    ],
)
def test_stage_generated_site_rejects_unsafe_website_id(
    tmp_path,
    website_id,
):
    with pytest.raises(
        ValueError,
        match="Unsafe website publication identifier",
    ):
        stage_generated_site(
            pages={
                "index.html": "<html>HOME</html>",
            },
            website_id=website_id,
            base_dir=str(tmp_path),
        )


@pytest.mark.unit
@pytest.mark.parametrize(
    "website_id",
    [
        "../outside",
        "../../outside",
        "/tmp/outside",
        r"..\outside",
        r"C:\temp\outside",
        "site/child",
    ],
)
def test_publish_staged_site_rejects_unsafe_website_id(
    tmp_path,
    website_id,
):
    staging_dir = (
        tmp_path
        / "safe-staging"
    )

    staging_dir.mkdir()

    (
        staging_dir
        / "index.html"
    ).write_text(
        "<html>HOME</html>",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Unsafe website publication identifier",
    ):
        publish_staged_site(
            staging_dir=staging_dir,
            website_id=website_id,
            base_dir=str(tmp_path),
        )

    # Validation must happen before publication mutates
    # the supplied staging directory.
    assert staging_dir.exists()

    assert (
        staging_dir
        / "index.html"
    ).is_file()


@pytest.mark.unit
@pytest.mark.parametrize(
    "website_id",
    [
        "site-1",
        "site_1",
        "4637703f-6b17-4ab5-b6f1-b623caf05f91",
    ],
)
def test_publication_allows_safe_website_identifiers(
    tmp_path,
    website_id,
):
    pages = {
        "index.html": "<html>HOME</html>",
        "about/index.html": "<html>ABOUT</html>",
    }

    staging_dir = stage_generated_site(
        pages=pages,
        website_id=website_id,
        base_dir=str(tmp_path),
    )

    assert staging_dir.exists()

    state = publish_staged_site(
        staging_dir=staging_dir,
        website_id=website_id,
        base_dir=str(tmp_path),
    )

    public_dir = (
        tmp_path
        / "generated_sites"
        / website_id
    )

    assert state.public_dir == public_dir
    assert public_dir.is_dir()

    for filename, expected in pages.items():
        assert (
            public_dir
            / filename
        ).read_text(
            encoding="utf-8"
        ) == expected

    finalize_publication(
        state
    )

    assert public_dir.is_dir()


@pytest.mark.unit
@pytest.mark.parametrize(
    "pages",
    [
        {},
        {
            "about.html": "<html>ABOUT</html>",
        },
    ],
)
def test_stage_generated_site_rejects_incomplete_page_sets(
    tmp_path,
    pages,
):
    with pytest.raises(
        ValueError,
        match="Invalid generated site pages",
    ):
        stage_generated_site(
            pages=pages,
            website_id="site-pages",
            base_dir=str(tmp_path),
        )

    public_dir = (
        tmp_path
        / "generated_sites"
        / "site-pages"
    )

    assert not public_dir.exists()


@pytest.mark.unit
@pytest.mark.parametrize(
    "filename",
    [
        "",
        123,
        None,
    ],
)
def test_stage_generated_site_rejects_invalid_page_filenames(
    tmp_path,
    filename,
):
    pages = {
        "index.html": "<html>HOME</html>",
    }

    # Build malformed mappings without relying on the
    # function's type annotation as runtime validation.
    pages[filename] = "<html>INVALID</html>"

    with pytest.raises(
        ValueError,
        match="Invalid generated page filename",
    ):
        stage_generated_site(
            pages=pages,
            website_id="site-filename",
            base_dir=str(tmp_path),
        )

    public_dir = (
        tmp_path
        / "generated_sites"
        / "site-filename"
    )

    assert not public_dir.exists()


@pytest.mark.unit
@pytest.mark.parametrize(
    "html_content",
    [
        None,
        123,
        [],
        {},
    ],
)
def test_stage_generated_site_rejects_non_string_page_content(
    tmp_path,
    html_content,
):
    pages = {
        "index.html": html_content,
    }

    with pytest.raises(
        ValueError,
        match="Invalid generated page content",
    ):
        stage_generated_site(
            pages=pages,
            website_id="site-content",
            base_dir=str(tmp_path),
        )

    public_dir = (
        tmp_path
        / "generated_sites"
        / "site-content"
    )

    assert not public_dir.exists()


@pytest.mark.unit
def test_stage_generated_site_allows_empty_string_page_content(
    tmp_path,
):
    pages = {
        "index.html": "",
    }

    staging_dir = stage_generated_site(
        pages=pages,
        website_id="site-empty-content",
        base_dir=str(tmp_path),
    )

    try:
        index_file = (
            staging_dir
            / "index.html"
        )

        assert index_file.is_file()
        assert (
            index_file.read_text(
                encoding="utf-8",
            )
            == ""
        )

    finally:
        cleanup_staging(
            staging_dir
        )


@pytest.mark.unit
def test_publication_lock_serializes_same_website_across_processes(
    tmp_path,
):
    import multiprocessing
    import time

    from backend.services.website_publication import (
        publication_lock,
    )

    website_id = "same-site"

    first_acquired = multiprocessing.Event()
    release_first = multiprocessing.Event()
    second_acquired = multiprocessing.Event()

    def first_worker():
        with publication_lock(
            website_id=website_id,
            base_dir=str(tmp_path),
        ):
            first_acquired.set()
            release_first.wait(timeout=5)

    def second_worker():
        first_acquired.wait(timeout=5)

        with publication_lock(
            website_id=website_id,
            base_dir=str(tmp_path),
        ):
            second_acquired.set()

    first = multiprocessing.Process(
        target=first_worker,
    )
    second = multiprocessing.Process(
        target=second_worker,
    )

    first.start()
    second.start()

    try:
        assert first_acquired.wait(timeout=5)

        time.sleep(0.2)

        # Same website ID must remain blocked while the
        # first process owns its publication lock.
        assert not second_acquired.is_set()

        release_first.set()

        assert second_acquired.wait(timeout=5)

    finally:
        release_first.set()

        first.join(timeout=5)
        second.join(timeout=5)

        if first.is_alive():
            first.terminate()
            first.join(timeout=5)

        if second.is_alive():
            second.terminate()
            second.join(timeout=5)

    assert first.exitcode == 0
    assert second.exitcode == 0


@pytest.mark.unit
def test_publication_lock_does_not_serialize_different_websites(
    tmp_path,
):
    import multiprocessing

    from backend.services.website_publication import (
        publication_lock,
    )

    first_acquired = multiprocessing.Event()
    release_first = multiprocessing.Event()
    second_acquired = multiprocessing.Event()

    def first_worker():
        with publication_lock(
            website_id="site-a",
            base_dir=str(tmp_path),
        ):
            first_acquired.set()
            release_first.wait(timeout=5)

    def second_worker():
        first_acquired.wait(timeout=5)

        with publication_lock(
            website_id="site-b",
            base_dir=str(tmp_path),
        ):
            second_acquired.set()

    first = multiprocessing.Process(
        target=first_worker,
    )
    second = multiprocessing.Process(
        target=second_worker,
    )

    first.start()
    second.start()

    try:
        assert first_acquired.wait(timeout=5)

        # Different website IDs must be independently
        # publishable.
        assert second_acquired.wait(timeout=5)

    finally:
        release_first.set()

        first.join(timeout=5)
        second.join(timeout=5)

        if first.is_alive():
            first.terminate()
            first.join(timeout=5)

        if second.is_alive():
            second.terminate()
            second.join(timeout=5)

    assert first.exitcode == 0
    assert second.exitcode == 0
