import json
from contextlib import contextmanager

import pytest


@pytest.mark.unit
def test_generate_business_profile_composition_contract(
    monkeypatch,
):
    # The generator imports the LLM client, whose module-level
    # OpenAI client requires an API key during import.
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "test-key",
    )

    import backend.services.gpt_website_generator as generator

    events = []

    @contextmanager
    def fake_track_gpt_duration(
        *,
        model,
        user_id,
    ):
        events.append(
            (
                "duration_start",
                model,
                user_id,
            )
        )

        metrics = {}

        yield metrics

        events.append(
            (
                "duration_end",
                dict(metrics),
            )
        )

    def fake_get_model():
        events.append(
            ("model",)
        )
        return "test-model"

    def fake_build_prompt():
        events.append(
            ("prompt",)
        )
        return "SYSTEM-PROMPT"

    def fake_generate_content(
        *,
        system_prompt,
        prompt,
        business_type,
        model,
    ):
        events.append(
            (
                "llm",
                system_prompt,
                prompt,
                business_type,
                model,
            )
        )

        return (
            json.dumps(
                {
                    "business_name": "Test Pizza",
                }
            ),
            {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30,
            },
        )

    def fake_record_tokens(
        *,
        model,
        user_id,
        prompt_tokens,
        completion_tokens,
        total_tokens,
    ):
        events.append(
            (
                "tokens",
                model,
                user_id,
                prompt_tokens,
                completion_tokens,
                total_tokens,
            )
        )

    def fake_normalize(profile):
        events.append(
            (
                "normalize",
                dict(profile),
            )
        )

        result = dict(profile)
        result["normalized"] = True
        return result

    def fake_intelligence(profile):
        events.append(
            (
                "intelligence",
                dict(profile),
            )
        )

        result = dict(profile)
        result["intelligence"] = True
        return result

    def fake_telemetry(
        *,
        business_type,
        model,
        usage,
        profile,
    ):
        events.append(
            (
                "telemetry",
                business_type,
                model,
                dict(usage),
                dict(profile),
            )
        )

    monkeypatch.setattr(
        generator,
        "get_business_profile_model",
        fake_get_model,
    )
    monkeypatch.setattr(
        generator,
        "track_gpt_duration",
        fake_track_gpt_duration,
    )
    monkeypatch.setattr(
        generator,
        "build_business_profile_system_prompt",
        fake_build_prompt,
    )
    monkeypatch.setattr(
        generator,
        "generate_business_profile_content",
        fake_generate_content,
    )
    monkeypatch.setattr(
        generator,
        "record_gpt_tokens",
        fake_record_tokens,
    )
    monkeypatch.setattr(
        generator,
        "normalize_generated_business_profile",
        fake_normalize,
    )
    monkeypatch.setattr(
        generator,
        "run_website_intelligence_pipeline",
        fake_intelligence,
    )
    monkeypatch.setattr(
        generator,
        "log_business_profile_generation",
        fake_telemetry,
    )

    result = generator.generate_business_profile(
        prompt="Neighborhood pizza shop",
        business_type="Pizza Shop",
        user_id="test-user",
    )

    assert result == {
        "business_name": "Test Pizza",
        "normalized": True,
        "intelligence": True,
        "_usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30,
        },
        "_model": "test-model",
    }

    event_names = [
        event[0]
        for event in events
    ]

    assert event_names == [
        "model",
        "duration_start",
        "prompt",
        "llm",
        "tokens",
        "normalize",
        "intelligence",
        "telemetry",
        "duration_end",
    ]

    assert events[3] == (
        "llm",
        "SYSTEM-PROMPT",
        "Neighborhood pizza shop",
        "Pizza Shop",
        "test-model",
    )

    assert events[4] == (
        "tokens",
        "test-model",
        "test-user",
        10,
        20,
        30,
    )

    # Telemetry receives the intelligence-enriched profile
    # before generation metadata is attached.
    telemetry_profile = events[7][4]

    assert telemetry_profile == {
        "business_name": "Test Pizza",
        "normalized": True,
        "intelligence": True,
    }

    assert "_usage" not in telemetry_profile
    assert "_model" not in telemetry_profile

    assert events[-1] == (
        "duration_end",
        {
            "status": "success",
        },
    )


@pytest.mark.unit
def test_generate_business_profile_failure_contract(
    monkeypatch,
):
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "test-key",
    )

    import backend.services.gpt_website_generator as generator

    captured_metrics = {}

    @contextmanager
    def fake_track_gpt_duration(
        *,
        model,
        user_id,
    ):
        yield captured_metrics

    monkeypatch.setattr(
        generator,
        "get_business_profile_model",
        lambda: "test-model",
    )
    monkeypatch.setattr(
        generator,
        "track_gpt_duration",
        fake_track_gpt_duration,
    )
    monkeypatch.setattr(
        generator,
        "build_business_profile_system_prompt",
        lambda: "SYSTEM",
    )

    def fail_generation(**kwargs):
        raise RuntimeError(
            "synthetic generation failure"
        )

    monkeypatch.setattr(
        generator,
        "generate_business_profile_content",
        fail_generation,
    )

    exception_calls = []

    def fake_exception(
        event,
        **kwargs,
    ):
        exception_calls.append(
            (
                event,
                kwargs,
            )
        )

    monkeypatch.setattr(
        generator.logger,
        "exception",
        fake_exception,
    )

    with pytest.raises(
        RuntimeError,
        match="synthetic generation failure",
    ):
        generator.generate_business_profile(
            prompt="Test description",
            business_type="Pizza Shop",
            user_id="test-user",
        )

    assert captured_metrics == {
        "status": "failure",
    }

    assert exception_calls == [
        (
            "Website generation failed",
            {
                "business_type": "Pizza Shop",
                "model": "test-model",
                "failure_type": "RuntimeError",
            },
        )
    ]
