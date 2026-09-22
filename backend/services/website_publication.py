from __future__ import annotations

import fcntl
import os
import re
import shutil
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PublicationState:
    public_dir: Path
    backup_dir: Path | None = None


_SAFE_PUBLICATION_IDENTIFIER = re.compile(
    r"^[A-Za-z0-9_-]+$"
)


def validate_publication_identifier(
    website_id: str,
) -> None:
    if (
        not website_id
        or _SAFE_PUBLICATION_IDENTIFIER.fullmatch(
            website_id
        )
        is None
    ):
        raise ValueError(
            "Unsafe website publication identifier: "
            f"{website_id}"
        )


def validate_generated_pages(
    pages: dict[str, str],
) -> None:
    # ------------------------------------------------
    # Container-level structural contract
    # ------------------------------------------------

    if (
        not isinstance(
            pages,
            dict,
        )
        or not pages
    ):
        raise ValueError(
            "Invalid generated site pages"
        )

    # ------------------------------------------------
    # Page-level structural and path contracts
    #
    # Validate individual entries before enforcing the
    # required index page so malformed paths retain the
    # more specific security failure contract.
    # ------------------------------------------------

    for filename, html_content in pages.items():
        if (
            not isinstance(
                filename,
                str,
            )
            or not filename
        ):
            raise ValueError(
                "Invalid generated page filename"
            )

        if not isinstance(
            html_content,
            str,
        ):
            raise ValueError(
                "Invalid generated page content"
            )

        relative_path = Path(
            filename
        )

        if (
            relative_path.is_absolute()
            or ".." in relative_path.parts
            or "\\" in filename
        ):
            raise ValueError(
                "Unsafe generated page path: "
                f"{filename}"
            )

    # ------------------------------------------------
    # Required site entry point
    # ------------------------------------------------

    if "index.html" not in pages:
        raise ValueError(
            "Invalid generated site pages"
        )


@contextmanager
def publication_lock(
    *,
    website_id: str,
    base_dir: str = "/app",
):
    validate_publication_identifier(
        website_id
    )

    lock_root = (
        Path(base_dir)
        / ".generated_sites_locks"
    )

    lock_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    lock_path = (
        lock_root
        / f"{website_id}.lock"
    )

    lock_file = lock_path.open(
        "a+",
    )

    try:
        fcntl.flock(
            lock_file.fileno(),
            fcntl.LOCK_EX,
        )

        yield

    finally:
        try:
            fcntl.flock(
                lock_file.fileno(),
                fcntl.LOCK_UN,
            )

        finally:
            lock_file.close()


def stage_generated_site(
    *,
    pages: dict[str, str],
    website_id: str,
    base_dir: str = "/app",
) -> Path:
    validate_publication_identifier(
        website_id
    )

    validate_generated_pages(
        pages
    )

    staging_root = Path(
        base_dir
    ) / ".generated_sites_staging"

    staging_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    staging_dir = Path(
        tempfile.mkdtemp(
            prefix=f"{website_id}-",
            dir=str(staging_root),
        )
    )

    try:
        for filename, html_content in pages.items():
            relative_path = Path(
                filename
            )

            file_path = (
                staging_dir
                / relative_path
            )

            file_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            file_path.write_text(
                html_content,
                encoding="utf-8",
            )

    except Exception:
        shutil.rmtree(
            staging_dir,
            ignore_errors=True,
        )
        raise

    return staging_dir


def publish_staged_site(
    *,
    staging_dir: Path,
    website_id: str,
    base_dir: str = "/app",
) -> PublicationState:
    validate_publication_identifier(
        website_id
    )

    public_root = (
        Path(base_dir)
        / "generated_sites"
    )

    public_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    public_dir = (
        public_root
        / website_id
    )

    backup_dir = None

    if public_dir.exists():
        backup_root = (
            Path(base_dir)
            / ".generated_sites_backup"
        )

        backup_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        backup_dir = Path(
            tempfile.mkdtemp(
                prefix=f"{website_id}-",
                dir=str(backup_root),
            )
        )

        # mkdtemp creates the directory itself.
        # os.replace requires the destination path
        # not to exist for directory replacement.
        backup_dir.rmdir()

        os.replace(
            public_dir,
            backup_dir,
        )

    try:
        os.replace(
            staging_dir,
            public_dir,
        )

    except Exception:
        if (
            backup_dir is not None
            and backup_dir.exists()
        ):
            os.replace(
                backup_dir,
                public_dir,
            )

        raise

    return PublicationState(
        public_dir=public_dir,
        backup_dir=backup_dir,
    )


def finalize_publication(
    state: PublicationState,
) -> None:
    if (
        state.backup_dir is not None
        and state.backup_dir.exists()
    ):
        shutil.rmtree(
            state.backup_dir,
        )


def rollback_publication(
    state: PublicationState,
) -> None:
    if state.public_dir.exists():
        shutil.rmtree(
            state.public_dir,
        )

    if (
        state.backup_dir is not None
        and state.backup_dir.exists()
    ):
        os.replace(
            state.backup_dir,
            state.public_dir,
        )


def cleanup_staging(
    staging_dir: Path | None,
) -> None:
    if (
        staging_dir is not None
        and staging_dir.exists()
    ):
        shutil.rmtree(
            staging_dir,
            ignore_errors=True,
        )
