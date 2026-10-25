"""The model settings (code/model_settings.toml) and the API key (environment or .env)."""

from __future__ import annotations

import os
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from c00_interfaces.components import ModelError


@dataclass(frozen=True)
class ModelSettings:
    provider: str
    base_url: str
    api_key_variable: str
    text_model: str
    vision_model: str
    max_answer_tokens: int
    timeout_seconds: float
    attempts: int
    seconds_between_calls: float
    give_up_after_failures: int
    # (input, output) US dollars per million tokens
    prices: Mapping[str, tuple[float, float]] = field(default_factory=dict, hash=False)


def read_settings(path: Path) -> ModelSettings:
    try:
        settings = tomllib.loads(path.read_text(encoding="utf-8"))
        return ModelSettings(
            provider=str(settings["provider"]["name"]),
            base_url=str(settings["provider"]["base_url"]).rstrip("/"),
            api_key_variable=str(settings["provider"]["api_key_variable"]),
            text_model=str(settings["models"]["text"]),
            vision_model=str(settings["models"]["vision"]),
            max_answer_tokens=int(settings["calls"]["max_answer_tokens"]),
            timeout_seconds=float(settings["calls"]["timeout_seconds"]),
            attempts=max(1, int(settings["calls"]["attempts"])),
            seconds_between_calls=float(settings["calls"]["seconds_between_calls"]),
            give_up_after_failures=max(1, int(settings["calls"]["give_up_after_failures"])),
            prices={str(model): (float(price["input"]), float(price["output"]))
                    for model, price in settings.get("prices", {}).items()},
        )
    except (OSError, tomllib.TOMLDecodeError, KeyError, TypeError, ValueError) as error:
        raise ModelError(f"the model settings in {path.name} cannot be used: {type(error).__name__} {error}") from None


def read_api_key(variable: str, env_file: Path) -> str:
    """The key from the environment, else from the .env file; "" when neither has it."""
    if os.environ.get(variable, "").strip():
        return os.environ[variable].strip()
    try:
        # utf-8-sig, because some Windows editors start the file with a byte-order mark.
        lines = env_file.read_text(encoding="utf-8-sig").splitlines()
    except OSError:
        return ""
    for line in lines:
        name, separator, value = line.partition("=")
        if separator and name.strip() == variable and not name.lstrip().startswith("#"):
            return value.strip().strip("'\"")
    return ""
