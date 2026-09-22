import logging
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import or_

from backend.celery_app import celery_app
from backend.db.session import SessionLocal

from backend.models.generated_sites import GeneratedSite

from backend.services.gpt_website_generator import (
    generate_business_profile,
)

from backend.services.multi_page_generator import (
    generate_multi_page_site,
)

from backend.services.website_publication import (
    cleanup_staging,
    finalize_publication,
    publication_lock,
    publish_staged_site,
    rollback_publication,
    stage_generated_site,
)


logger = logging.getLogger(__name__)


GENERATION_LEASE_TIMEOUT = timedelta(
    minutes=30,
)


def utc_now() -> datetime:
    return datetime.now(
        timezone.utc
    )


def claim_generation_lease(
    *,
    db,
    website_id: str,
    now: datetime,
    attempt_id=None,
) -> bool:
    stale_before = (
        now
        - GENERATION_LEASE_TIMEOUT
    )

    updated_rows = (
        db.query(GeneratedSite)
        .filter(
            GeneratedSite.id == website_id,
            GeneratedSite.generation_status
            != "completed",
            or_(
                GeneratedSite.generation_status
                != "generating",
                GeneratedSite.generation_started_at
                .is_(None),
                GeneratedSite.generation_started_at
                <= stale_before,
            ),
        )
        .update(
            {
                GeneratedSite.generation_status:
                    "generating",
                GeneratedSite.generation_started_at:
                    now,
                GeneratedSite.generation_attempt_id:
                    attempt_id,
            },
            synchronize_session=False,
        )
    )

    if updated_rows != 1:
        db.rollback()
        return False

    db.commit()
    return True


def fail_generation_attempt(
    *,
    db,
    website_id: str,
    attempt_id,
    error_message: str,
) -> bool:
    updated_rows = (
        db.query(GeneratedSite)
        .filter(
            GeneratedSite.id == website_id,
            GeneratedSite.generation_status
            == "generating",
            GeneratedSite.generation_attempt_id
            == attempt_id,
        )
        .update(
            {
                GeneratedSite.generation_status:
                    "failed",
                GeneratedSite.generation_started_at:
                    None,
                GeneratedSite.generation_attempt_id:
                    None,
                GeneratedSite.error_message:
                    error_message,
            },
            synchronize_session=False,
        )
    )

    if updated_rows != 1:
        db.rollback()
        return False

    db.commit()
    return True


def lock_generation_attempt(
    *,
    db,
    website_id: str,
    attempt_id,
) -> bool:
    website = (
        db.query(GeneratedSite)
        .filter(
            GeneratedSite.id == website_id,
            GeneratedSite.generation_status
            == "generating",
            GeneratedSite.generation_attempt_id
            == attempt_id,
        )
        .with_for_update()
        .first()
    )

    return website is not None


def generation_attempt_is_current(
    *,
    db,
    website_id: str,
    attempt_id,
) -> bool:
    website = (
        db.query(GeneratedSite)
        .filter(
            GeneratedSite.id == website_id,
            GeneratedSite.generation_status
            == "generating",
            GeneratedSite.generation_attempt_id
            == attempt_id,
        )
        .first()
    )

    return website is not None


@celery_app.task
def generate_website_task(
    website_id: str,
    business_type: str,
):
    db = SessionLocal()

    website = None
    staging_dir = None
    publication_state = None
    publication_lock_context = None
    attempt_id = None

    try:

        # ------------------------------------------------
        # Retrieve website record
        # ------------------------------------------------

        website = (
            db.query(GeneratedSite)
            .filter(
                GeneratedSite.id == website_id
            )
            .first()
        )

        if not website:
            return

        # ------------------------------------------------
        # Idempotency boundary
        #
        # A completed generation is terminal. Celery may
        # redeliver a task, but completed work must not
        # cross the generation or publication boundary
        # again.
        # ------------------------------------------------

        if website.generation_status == "completed":
            return

        if website.generation_status == "generating":
            generation_started_at = getattr(
                website,
                "generation_started_at",
                None,
            )

            if (
                generation_started_at is not None
                and (
                    utc_now()
                    - generation_started_at
                )
                < GENERATION_LEASE_TIMEOUT
            ):
                return

        # ------------------------------------------------
        # Claim generation lease
        #
        # New work and stale generating work both cross
        # this boundary. Refreshing generation_started_at
        # establishes ownership of the current attempt.
        # ------------------------------------------------

        claim_time = utc_now()
        attempt_id = uuid4()

        if not claim_generation_lease(
            db=db,
            website_id=website_id,
            now=claim_time,
            attempt_id=attempt_id,
        ):
            return

        db.refresh(website)

        # ------------------------------------------------
        # Resolve selected theme
        # ------------------------------------------------

        theme = (
            website.metadata_json or {}
        ).get(
            "theme",
            "modern",
        )

        # ------------------------------------------------
        # Generate GPT business profile
        # ------------------------------------------------

        profile = generate_business_profile(
            prompt=website.prompt,
            business_type=website.business_type,
            user_id=str(website.user_id),
        )

        # ------------------------------------------------
        # Generate multi-page website
        # ------------------------------------------------

        pages = generate_multi_page_site(
            profile=profile,
            theme=theme,
        )

        # ------------------------------------------------
        # Stage generated pages outside the public tree
        # ------------------------------------------------

        staging_dir = stage_generated_site(
            pages=pages,
            website_id=str(website.id),
        )

        # ------------------------------------------------
        # Terminal fencing boundary
        #
        # Hold a token-conditioned row lock across
        # persistence, publication, and the authoritative
        # completed commit. No generated ORM fields are
        # mutated before ownership is verified.
        # ------------------------------------------------

        if not lock_generation_attempt(
            db=db,
            website_id=website_id,
            attempt_id=attempt_id,
        ):
            db.rollback()

            cleanup_staging(
                staging_dir
            )

            staging_dir = None
            return

        # ------------------------------------------------
        # Acquire the per-site filesystem publication
        # fence while the terminal database row fence is
        # still held. It remains held through publication
        # and the authoritative completed commit.
        # ------------------------------------------------

        pending_publication_lock_context = publication_lock(
            website_id=str(website.id),
        )
        pending_publication_lock_context.__enter__()
        publication_lock_context = (
            pending_publication_lock_context
        )

        # ------------------------------------------------
        # Persist metadata and generated output only after
        # the terminal ownership fence has been acquired.
        # ------------------------------------------------

        website.metadata_json = {
            "theme": theme,
            "profile": profile,
            "pages": list(pages.keys()),
        }

        usage = profile.get(
            "_usage",
            {},
        )

        website.html = pages.get(
            "index.html",
            "",
        )

        website.css = ""

        website.js = ""

        website.gpt_model = profile.get(
            "_model"
        )

        website.gpt_tokens_prompt = usage.get(
            "prompt_tokens",
            0,
        )

        website.gpt_tokens_completion = usage.get(
            "completion_tokens",
            0,
        )

        website.gpt_tokens_total = usage.get(
            "total_tokens",
            0,
        )

        website.generated_url = (
            f"http://34.27.91.3:8000/generated-sites/"
            f"{website.id}/index.html"
        )

        website.generation_status = "completed"
        website.generation_started_at = None
        website.generation_attempt_id = None

        publication_state = publish_staged_site(
            staging_dir=staging_dir,
            website_id=str(website.id),
        )

        staging_dir = None

        db.commit()

        # ------------------------------------------------
        # Post-commit operations are best-effort.
        #
        # The completed-state commit above is the
        # authoritative success boundary. Failures after
        # that point must not convert a successfully
        # persisted generation into a failed generation
        # or roll back its published site.
        # ------------------------------------------------

        try:
            db.refresh(website)

        except Exception:
            logger.exception(
                "Website refresh failed after completed "
                "commit for website %s",
                website.id,
            )

        try:
            finalize_publication(
                publication_state
            )

        except Exception:
            logger.exception(
                "Website publication finalization failed "
                "after completed commit for website %s",
                website.id,
            )

        finally:
            publication_state = None

        # ------------------------------------------------
        # Publication-lock release is post-commit cleanup.
        #
        # The completed-state commit is already
        # authoritative. A release error must not convert
        # committed success into generation failure or
        # trigger publication rollback.
        #
        # Clear the reference before release so the outer
        # failure handler cannot attempt a second release
        # if __exit__ itself raises.
        # ------------------------------------------------

        completed_publication_lock_context = (
            publication_lock_context
        )
        publication_lock_context = None

        try:
            completed_publication_lock_context.__exit__(
                None,
                None,
                None,
            )

        except Exception:
            logger.exception(
                "Website publication lock release failed "
                "after completed commit for website %s",
                website.id,
            )

    except Exception as e:

        # ------------------------------------------------
        # Failure handling
        #
        # If publication itself failed, staging may still
        # exist while the terminal fencing row lock is
        # held. Remove that private filesystem state before
        # rollback releases the database fence.
        # ------------------------------------------------

        cleanup_staging(
            staging_dir
        )

        staging_dir = None

        try:
            db.rollback()
        except Exception:
            logger.exception(
                "Database rollback failed "
                "while handling generation failure for "
                "website %s",
                website.id if website else website_id,
            )

        if publication_state is not None:
            try:
                rollback_publication(
                    publication_state
                )
            except Exception:
                logger.exception(
                    "Website publication rollback failed "
                    "while handling generation failure for "
                    "website %s",
                    website.id,
                )
            finally:
                publication_state = None

        if website and attempt_id is not None:
            try:
                fail_generation_attempt(
                    db=db,
                    website_id=website_id,
                    attempt_id=attempt_id,
                    error_message=str(e),
                )
            except Exception:
                logger.exception(
                    "Website failure-state persistence failed "
                    "while handling generation failure for "
                    "website %s",
                    website.id,
                )

        if publication_lock_context is not None:
            failed_publication_lock_context = (
                publication_lock_context
            )
            publication_lock_context = None

            try:
                failed_publication_lock_context.__exit__(
                    type(e),
                    e,
                    e.__traceback__,
                )

            except Exception:
                logger.exception(
                    "Website publication lock release failed "
                    "while handling generation failure for "
                    "website %s",
                    website.id,
                )

        raise

    finally:

        try:
            db.close()
        except Exception:
            logger.exception(
                "Database close failed while finalizing "
                "website generation task for website %s",
                website.id if website else website_id,
            )

