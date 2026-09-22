from types import SimpleNamespace

import pytest

import backend.services.business_profile_llm_client as llm_client


@pytest.mark.unit
def test_business_profile_model_defaults_to_gpt_4_1_mini(
    monkeypatch,
):
    monkeypatch.delenv(
        "OPENAI_MODEL",
        raising=False,
    )

    assert (
        llm_client.get_business_profile_model()
        == "gpt-4.1-mini"
    )


@pytest.mark.unit
def test_business_profile_model_uses_environment_override(
    monkeypatch,
):
    monkeypatch.setenv(
        "OPENAI_MODEL",
        "test-model-x",
    )

    assert (
        llm_client.get_business_profile_model()
        == "test-model-x"
    )


@pytest.mark.unit
@pytest.mark.parametrize(
    (
        "usage",
        "expected",
    ),
    [
        (
            None,
            {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
        ),
        (
            SimpleNamespace(
                prompt_tokens=120,
                completion_tokens=45,
                total_tokens=165,
            ),
            {
                "prompt_tokens": 120,
                "completion_tokens": 45,
                "total_tokens": 165,
            },
        ),
        (
            SimpleNamespace(
                prompt_tokens=None,
                completion_tokens=None,
                total_tokens=None,
            ),
            {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
        ),
        (
            SimpleNamespace(
                prompt_tokens="12",
                completion_tokens="8",
                total_tokens="20",
            ),
            {
                "prompt_tokens": 12,
                "completion_tokens": 8,
                "total_tokens": 20,
            },
        ),
        (
            SimpleNamespace(
                prompt_tokens=50,
            ),
            {
                "prompt_tokens": 50,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
        ),
    ],
)
def test_extract_business_profile_usage(
    usage,
    expected,
):
    response = SimpleNamespace(
        usage=usage,
    )

    assert (
        llm_client.extract_business_profile_usage(
            response
        )
        == expected
    )


@pytest.mark.unit
def test_generate_business_profile_content_contract(
    monkeypatch,
):
    calls = []

    class FakeCompletions:
        def create(
            self,
            **kwargs,
        ):
            calls.append(kwargs)

            return SimpleNamespace(
                usage=SimpleNamespace(
                    prompt_tokens=10,
                    completion_tokens=20,
                    total_tokens=30,
                ),
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(
                            content=(
                                '{"business_name":"Test"}'
                            )
                        )
                    )
                ],
            )

    fake_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=FakeCompletions(),
        )
    )

    monkeypatch.setattr(
        llm_client,
        "get_business_profile_client",
        lambda: fake_client,
    )

    content, usage = (
        llm_client.generate_business_profile_content(
            system_prompt="SYSTEM-CONTENT",
            prompt="USER DESCRIPTION",
            business_type="Pizza Shop",
            model="test-model",
        )
    )

    assert len(calls) == 1

    assert calls[0] == {
        "model": "test-model",
        "temperature": 0.7,
        "response_format": {
            "type": "json_object",
        },
        "messages": [
            {
                "role": "system",
                "content": "SYSTEM-CONTENT",
            },
            {
                "role": "user",
                "content": (
                    "Business Type: Pizza Shop\n\n"
                    "Business Description:\n"
                    "USER DESCRIPTION"
                ),
            },
        ],
    }

    assert content == '{"business_name":"Test"}'

    assert usage == {
        "prompt_tokens": 10,
        "completion_tokens": 20,
        "total_tokens": 30,
    }


@pytest.mark.unit
def test_generate_business_profile_content_defaults_empty_content(
    monkeypatch,
):
    class FakeCompletions:
        def create(
            self,
            **kwargs,
        ):
            return SimpleNamespace(
                usage=None,
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(
                            content=None,
                        )
                    )
                ],
            )

    fake_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=FakeCompletions(),
        )
    )

    monkeypatch.setattr(
        llm_client,
        "get_business_profile_client",
        lambda: fake_client,
    )

    content, usage = (
        llm_client.generate_business_profile_content(
            system_prompt="SYSTEM",
            prompt="DESCRIPTION",
            business_type="Test",
            model="test-model",
        )
    )

    assert content == "{}"

    assert usage == {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
    }


@pytest.mark.unit
def test_llm_client_module_imports_without_api_key(
    monkeypatch,
):
    import os
    import subprocess
    import sys

    env = os.environ.copy()
    env.pop(
        "OPENAI_API_KEY",
        None,
    )

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import "
                "backend.services.business_profile_llm_client "
                "as llm_client; "
                "assert "
                "llm_client.get_business_profile_model()"
            ),
        ],
        cwd=".",
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, (
        "business_profile_llm_client failed to import "
        "without OPENAI_API_KEY.\n"
        f"stdout={result.stdout}\n"
        f"stderr={result.stderr}"
    )
