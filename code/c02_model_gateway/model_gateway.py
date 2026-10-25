"""ARC-02_model_gateway: the only place that calls an AI model.

It speaks the OpenAI-compatible chat API over plain HTTP, which most providers offer, so the
provider and the models are settings (EXT-405). Every answer is cached on disk: a second run gives
the same output without calling the model again (EXT-402), and costs nothing. Every call is
recorded with its tokens and estimated cost for the usage report. Whatever goes wrong becomes a
ModelError, and the caller decides what to do instead (EXT-501).
"""

from __future__ import annotations

import base64
import hashlib
import http.client
import json
import os
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path

from c00_interfaces.components import ModelError
from c00_interfaces.records import ModelCall, ModelQuestion
from c02_model_gateway.settings import ModelSettings, read_api_key, read_settings

Send = Callable[[str, Mapping[str, str], bytes, float], object]


class TemporaryError(Exception):
    """A failure that may pass when the call is repeated: a rate limit, a server error, a timeout."""

    def __init__(self, reason: str, wait_seconds: float | None = None):
        super().__init__(reason)
        self.wait_seconds = wait_seconds  # what the provider asked for (Retry-After), when it said


class RefuseRedirects(urllib.request.HTTPRedirectHandler):
    """urllib would send the API key along to whatever server a redirect names, so none is followed."""

    def redirect_request(self, req: urllib.request.Request, fp: object, code: int, msg: str, headers: object,
                         newurl: str) -> urllib.request.Request | None:
        return None


OPENER = urllib.request.build_opener(RefuseRedirects)


@dataclass(frozen=True)
class Answer:
    text: str
    input_tokens: int
    output_tokens: int


def gateway_from_settings(repository_root: Path) -> ModelGatewayOverHttp:
    settings = read_settings(repository_root / "code" / "model_settings.toml")
    api_key = read_api_key(settings.api_key_variable, repository_root / ".env")
    return ModelGatewayOverHttp(settings, api_key, repository_root / ".cache" / "model_answers")


class ModelGatewayOverHttp:
    def __init__(self, settings: ModelSettings, api_key: str, cache_dir: Path, send: Send | None = None,
                 sleep: Callable[[float], None] = time.sleep, clock: Callable[[], float] = time.monotonic):
        self.settings = settings
        self.api_key = api_key
        self.cache_dir = cache_dir
        self.send = send or post_json
        self.sleep = sleep
        self.clock = clock
        self.calls: list[ModelCall] = []
        self.last_call_at: float | None = None
        self.failures_in_a_row = 0

    def ask(self, question: ModelQuestion) -> str:
        model = self.settings.text_model if question.image_png is None else self.settings.vision_model
        request = chat_request(model, question, self.settings.max_answer_tokens)
        cache_file = self.cache_dir / f"{cache_key(self.settings.base_url, request)}.json"
        answer = read_cached(cache_file)
        from_cache = answer is not None
        if answer is None:
            answer = self.call_model(request)
            write_cached(cache_file, answer, model, question.purpose)
        self.record(question.purpose, model, answer, from_cache)
        return answer.text

    def call_model(self, request: Mapping[str, object]) -> Answer:
        if not self.api_key:
            raise ModelError(f"no API key: set {self.settings.api_key_variable} in the environment or in .env")
        # A provider that is down would otherwise cost every remaining question all its attempts,
        # which can add hours to a run.
        if self.failures_in_a_row >= self.settings.give_up_after_failures:
            raise ModelError(f"the model failed {self.failures_in_a_row} questions in a row; no more calls in this run")
        try:
            answer = self.call_with_retries(request)
        except ModelError:
            self.failures_in_a_row += 1
            raise
        self.failures_in_a_row = 0
        return answer

    def recorded_calls(self) -> tuple[ModelCall, ...]:
        return tuple(self.calls)

    def call_with_retries(self, request: Mapping[str, object]) -> Answer:
        url = f"{self.settings.base_url}/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json",
                   "Accept": "application/json"}
        body = json.dumps(request).encode("utf-8")
        for attempt in range(1, self.settings.attempts + 1):
            self.wait_for_turn()
            try:
                return answer_from(self.send(url, headers, body, self.settings.timeout_seconds))
            except TemporaryError as error:
                if attempt == self.settings.attempts:
                    raise ModelError(f"the model did not answer in {attempt} attempts ({error})") from None
                self.sleep(error.wait_seconds if error.wait_seconds is not None else min(60.0, 2.0 ** attempt))
        raise ModelError("the model was not called")

    def wait_for_turn(self) -> None:
        if self.last_call_at is not None:
            wait = self.settings.seconds_between_calls - (self.clock() - self.last_call_at)
            if wait > 0:
                self.sleep(wait)
        self.last_call_at = self.clock()

    def record(self, purpose: str, model: str, answer: Answer, from_cache: bool) -> None:
        input_price, output_price = self.settings.prices.get(model, (0.0, 0.0))
        cost = (answer.input_tokens * input_price + answer.output_tokens * output_price) / 1_000_000
        self.calls.append(ModelCall(purpose, self.settings.provider, model, answer.input_tokens,
                                    answer.output_tokens, cost, from_cache))


def chat_request(model: str, question: ModelQuestion, max_answer_tokens: int) -> dict[str, object]:
    content: object = question.data
    if question.image_png is not None:
        image = base64.b64encode(question.image_png).decode("ascii")
        content = [{"type": "text", "text": question.data},
                   {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image}"}}]
    # The instructions and the data travel in separate messages, so that text from the dataset is
    # never mistaken for an instruction (EXT-502).
    return {"model": model, "temperature": 0, "top_p": 1, "max_tokens": max_answer_tokens,
            "messages": [{"role": "system", "content": question.instructions},
                         {"role": "user", "content": content}]}


def answer_from(response: object) -> Answer:
    response = response if isinstance(response, dict) else {}
    choices = response.get("choices")
    choice = choices[0] if isinstance(choices, list) and choices and isinstance(choices[0], dict) else {}
    message = choice.get("message")
    text = message.get("content") if isinstance(message, dict) else None
    if not isinstance(text, str) or not text.strip():
        raise ModelError("the model's answer is empty or missing")
    if choice.get("finish_reason") == "length":
        raise ModelError("the model's answer was cut off at max_answer_tokens")
    usage = response.get("usage")
    usage = usage if isinstance(usage, dict) else {}
    return Answer(text.strip(), token_count(usage.get("prompt_tokens")), token_count(usage.get("completion_tokens")))


def token_count(value: object) -> int:
    return value if isinstance(value, int) and value >= 0 else 0


def post_json(url: str, headers: Mapping[str, str], body: bytes, timeout: float) -> object:
    request = urllib.request.Request(url, data=body, headers=dict(headers), method="POST")
    try:
        with OPENER.open(request, timeout=timeout) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        error.close()
        if error.code in (408, 429) or error.code >= 500:
            retry_after = error.headers.get("Retry-After") if error.headers else None
            raise TemporaryError(f"HTTP {error.code}", seconds_to_wait(retry_after)) from None
        if 300 <= error.code < 400:
            raise ModelError(f"the provider answered with a redirect (HTTP {error.code}), which is not followed "
                             "so that the key goes nowhere else; check base_url") from None
        # The body is left out: it can name the account behind the key, and problems are logged.
        raise ModelError(f"the provider refused the call: HTTP {error.code} {error.reason}"
                         + (" (the model may not be available to this key)" if error.code == 404 else "")) from None
    except (urllib.error.URLError, http.client.HTTPException, TimeoutError, ConnectionError) as error:
        raise TemporaryError(type(error).__name__) from None
    except ValueError:
        raise ModelError("the provider's answer is not JSON") from None


def seconds_to_wait(retry_after: str | None) -> float | None:
    """Retry-After in seconds, at most two minutes; None when the provider gave none, or a date."""
    try:
        seconds = float(retry_after or "")
    except ValueError:
        return None
    return min(120.0, seconds) if seconds >= 0 else None


def cache_key(base_url: str, request: Mapping[str, object]) -> str:
    return hashlib.sha256(json.dumps({"base_url": base_url, "request": request}, sort_keys=True).encode()).hexdigest()


def read_cached(path: Path) -> Answer | None:
    try:
        cached = json.loads(path.read_text(encoding="utf-8"))
        return Answer(str(cached["answer"]), int(cached["input_tokens"]), int(cached["output_tokens"]))
    except (OSError, ValueError, KeyError, TypeError):
        return None


def write_cached(path: Path, answer: Answer, model: str, purpose: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps({"model": model, "purpose": purpose, "answer": answer.text,
                                     "input_tokens": answer.input_tokens, "output_tokens": answer.output_tokens},
                                    ensure_ascii=False, indent=1), encoding="utf-8")
    # Replacing in one step means a run that is stopped halfway never leaves half a cached answer.
    os.replace(temporary, path)
