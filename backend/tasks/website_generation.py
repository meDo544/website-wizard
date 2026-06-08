import os

from backend.celery_app import celery_app
from backend.db.session import SessionLocal

from backend.models.generated_sites import GeneratedSite

from backend.services.gpt_website_generator import (
    generate_business_profile,
)

from backend.services.website_generator import (
    generate_website,
)


@celery_app.task
def generate_website_task(
    website_id: str,
    business_type: str,
):
    db = SessionLocal()

    website = None

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
        # Update status -> generating
        # ------------------------------------------------

        website.generation_status = "generating"

        db.commit()

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
        # Generate themed website
        # ------------------------------------------------

        generated_html = generate_website(
            profile=profile,
            business_type=website.business_type,
            theme=theme,
        )

        # ------------------------------------------------
        # Persist metadata
        # ------------------------------------------------

        website.metadata_json = {
            "theme": theme,
            "profile": profile,
        }

        # ------------------------------------------------
        # Create deployment directory
        # ------------------------------------------------

        BASE_DIR = "/app"

        output_dir = os.path.join(
            BASE_DIR,
            "generated_sites",
            str(website.id),
        )

        os.makedirs(
            output_dir,
            exist_ok=True,
        )

        # ------------------------------------------------
        # Define index path
        # ------------------------------------------------

        index_path = os.path.join(
            output_dir,
            "index.html",
        )

        # ------------------------------------------------
        # Write generated website
        # ------------------------------------------------

        with open(
            index_path,
            "w",
            encoding="utf-8",
        ) as f:
            f.write(generated_html)

        # ------------------------------------------------
        # Save generated output
        # ------------------------------------------------

        usage = profile.get(
            "_usage",
            {},
        )

        website.html = generated_html

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

        db.commit()

        db.refresh(website)

    except Exception as e:

        # ------------------------------------------------
        # Failure handling
        # ------------------------------------------------

        if website:

            website.generation_status = "failed"

            website.error_message = str(e)

            db.commit()

        raise

    finally:

        db.close()

