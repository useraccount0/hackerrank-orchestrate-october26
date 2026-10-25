"""ARC-02_model_gateway: CHR-508, EXT-401, EXT-402, EXT-405, EXT-408, EXT-501, EXT-502."""

import json
import os
import socket
import tempfile
import threading
import time
import unittest
from collections.abc import Callable, Mapping
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import mock

from c00_interfaces.components import ModelError, ModelGateway
from c00_interfaces.records import ModelCall, ModelQuestion
from c02_model_gateway.model_gateway import ModelGatewayOverHttp, TemporaryError, post_json
from c02_model_gateway.settings import ModelSettings, read_api_key, read_settings

SETTINGS = ModelSettings("test_provider", "https://models.example/v1", "TEST_MODEL_KEY", "text-model",
                         "vision-model", 1000, 5.0, 3, 1.0, 3, {"text-model": (2.0, 8.0)})
KEY = "test-key-7f3a"
QUESTION = ModelQuestion("classify", "Decide whether the request asks for deletion.", "Please delete my account.")
SETTINGS_FILE = Path(__file__).resolve().parents[1] / "model_settings.toml"


def reply(text: str = "answer", finish_reason: str = "stop") -> dict[str, object]:
    return {"choices": [{"message": {"role": "assistant", "content": text}, "finish_reason": finish_reason}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 50}}


class FakeProvider:
    """Answers like an OpenAI-compatible API, one outcome per call, and keeps what it was sent."""

    def __init__(self, *outcomes: object):
        self.outcomes = list(outcomes)
        self.requests: list[tuple[str, dict[str, str], dict[str, object]]] = []

    def __call__(self, url: str, headers: Mapping[str, str], body: bytes, timeout: float) -> object:
        self.requests.append((url, dict(headers), json.loads(body)))
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class GatewayTest(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.cache_dir = Path(temporary.name)
        self.sleeps: list[float] = []

    def gateway(self, provider: FakeProvider, api_key: str = KEY) -> ModelGatewayOverHttp:
        return ModelGatewayOverHttp(SETTINGS, api_key, self.cache_dir, provider, sleep=self.sleeps.append,
                                    clock=lambda: 0.0)


class AsksTheModel(GatewayTest):
    def test_the_gateway_fits_the_interface(self) -> None:
        gateway: ModelGateway = self.gateway(FakeProvider())
        self.assertIsInstance(gateway, ModelGateway)

    def test_instructions_and_data_travel_in_separate_messages_to_the_text_model(self) -> None:
        provider = FakeProvider(reply("yes"))
        self.assertEqual(self.gateway(provider).ask(QUESTION), "yes")
        url, headers, body = provider.requests[0]
        self.assertEqual(url, "https://models.example/v1/chat/completions")
        self.assertEqual(headers["Authorization"], f"Bearer {KEY}")
        self.assertEqual((body["model"], body["temperature"]), ("text-model", 0))
        self.assertEqual(body["messages"], [{"role": "system", "content": QUESTION.instructions},
                                            {"role": "user", "content": QUESTION.data}])

    def test_a_screenshot_goes_to_the_vision_model_as_an_inline_image(self) -> None:
        provider = FakeProvider(reply("text on the screen"))
        self.gateway(provider).ask(ModelQuestion("transcribe_screenshot", "Write down the text.", "a.png", b"\x89PNG"))
        body = provider.requests[0][2]
        self.assertEqual(body["model"], "vision-model")
        content = body["messages"][1]["content"]  # type: ignore[index]
        self.assertEqual(content[1], {"type": "image_url", "image_url": {"url": "data:image/png;base64,iVBORw=="}})

    def test_each_call_is_recorded_with_its_tokens_and_estimated_cost(self) -> None:
        gateway = self.gateway(FakeProvider(reply()))
        gateway.ask(QUESTION)
        cost = (100 * 2 + 50 * 8) / 1e6
        self.assertEqual(gateway.recorded_calls(),
                         (ModelCall("classify", "test_provider", "text-model", 100, 50, cost, False),))

    def test_calls_are_spaced_out_for_the_providers_rate_limit(self) -> None:
        gateway = self.gateway(FakeProvider(reply("one"), reply("two")))
        gateway.ask(QUESTION)
        gateway.ask(ModelQuestion("classify", QUESTION.instructions, "Another request."))
        self.assertEqual(self.sleeps, [1.0])


class CachesEveryAnswer(GatewayTest):
    def test_a_second_run_gets_the_same_answer_from_the_cache_without_a_call(self) -> None:
        provider = FakeProvider(reply("yes"))
        self.gateway(provider).ask(QUESTION)
        second_run = self.gateway(provider)
        self.assertEqual(second_run.ask(QUESTION), "yes")
        self.assertEqual(len(provider.requests), 1)
        self.assertTrue(second_run.recorded_calls()[0].from_cache)

    def test_without_a_key_only_cached_answers_are_given(self) -> None:
        provider = FakeProvider()
        with self.assertRaisesRegex(ModelError, "TEST_MODEL_KEY"):
            self.gateway(provider, api_key="").ask(QUESTION)
        self.assertEqual(provider.requests, [])

    def test_the_key_is_never_written_to_the_cache_or_the_records(self) -> None:
        gateway = self.gateway(FakeProvider(reply()))
        gateway.ask(QUESTION)
        cached = "".join(path.read_text(encoding="utf-8") for path in self.cache_dir.iterdir())
        self.assertNotIn(KEY, cached + repr(gateway.recorded_calls()))


class HandlesFailures(GatewayTest):
    def test_a_rate_limit_is_waited_out_and_the_call_repeated(self) -> None:
        provider = FakeProvider(TemporaryError("HTTP 429"), reply("yes"))
        self.assertEqual(self.gateway(provider).ask(QUESTION), "yes")
        self.assertEqual(len(provider.requests), 2)
        self.assertIn(2.0, self.sleeps)

    def test_a_model_that_keeps_failing_gives_a_model_error(self) -> None:
        provider = FakeProvider(*[TemporaryError("HTTP 503")] * 3)
        with self.assertRaisesRegex(ModelError, "3 attempts"):
            self.gateway(provider).ask(QUESTION)

    def test_a_refusal_is_not_repeated(self) -> None:
        provider = FakeProvider(ModelError("the provider refused the call: HTTP 401 Unauthorized"))
        with self.assertRaises(ModelError):
            self.gateway(provider).ask(QUESTION)
        self.assertEqual(len(provider.requests), 1)

    def test_after_three_failed_questions_the_run_stops_calling_but_cached_answers_still_come(self) -> None:
        provider = FakeProvider(reply("cached"), *[ModelError("HTTP 401 Unauthorized")] * 3)
        gateway = self.gateway(provider)
        gateway.ask(QUESTION)
        for number in range(3):
            with self.assertRaises(ModelError):
                gateway.ask(ModelQuestion("classify", QUESTION.instructions, f"Request {number}."))
        with self.assertRaisesRegex(ModelError, "no more calls"):
            gateway.ask(ModelQuestion("classify", QUESTION.instructions, "One more request."))
        self.assertEqual(len(provider.requests), 4)
        self.assertEqual(gateway.ask(QUESTION), "cached")

    def test_an_empty_cut_off_or_malformed_answer_is_neither_used_nor_cached(self) -> None:
        for answer in (reply(""), reply("{\"case_1\": tr", finish_reason="length"), {"error": "busy"}, ["odd"]):
            with self.subTest(answer=answer), self.assertRaises(ModelError):
                self.gateway(FakeProvider(answer)).ask(QUESTION)
        self.assertEqual(list(self.cache_dir.iterdir()), [])


def send(handler: BaseHTTPRequestHandler, status: int, body: bytes = b"", location: str = "") -> None:
    handler.send_response(status)
    if location:
        handler.send_header("Location", location)
    handler.end_headers()
    handler.wfile.write(body)


class HttpErrors(unittest.TestCase):
    def serve(self, respond: Callable[[BaseHTTPRequestHandler], None]) -> str:
        """A small HTTP server on this machine that answers as the test says; returns its address."""

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self) -> None:
                respond(self)

            def do_GET(self) -> None:
                respond(self)

            def log_message(self, format: str, *args: object) -> None:
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        return f"http://127.0.0.1:{server.server_address[1]}"

    def test_refusals_and_busy_servers_are_told_apart_and_the_error_body_is_left_out(self) -> None:
        status = {"code": 404}
        url = self.serve(lambda handler: send(handler, status["code"], b'{"detail": "account secret-account-id"}'))
        with self.assertRaises(ModelError) as refused:
            post_json(url, {}, b"{}", 5.0)
        self.assertIn("HTTP 404", str(refused.exception))
        self.assertNotIn("secret-account-id", str(refused.exception))
        status["code"] = 503
        with self.assertRaises(TemporaryError):
            post_json(url, {}, b"{}", 5.0)

    def test_a_redirect_is_not_followed_so_the_key_reaches_no_other_server(self) -> None:
        received: list[str | None] = []

        def keep_the_key_and_answer(handler: BaseHTTPRequestHandler) -> None:
            received.append(handler.headers.get("Authorization"))
            send(handler, 200, b"{}")

        other = self.serve(keep_the_key_and_answer)
        provider = self.serve(lambda handler: send(handler, 302, location=other + "/elsewhere"))
        with self.assertRaisesRegex(ModelError, "redirect"):
            post_json(provider, {"Authorization": f"Bearer {KEY}"}, b"{}", 5.0)
        self.assertEqual(received, [])

    def test_a_server_that_cannot_be_reached_or_answers_too_slowly_is_a_temporary_failure(self) -> None:
        with socket.socket() as unused:
            unused.bind(("127.0.0.1", 0))
            closed_port = unused.getsockname()[1]
        with self.assertRaises(TemporaryError):
            post_json(f"http://127.0.0.1:{closed_port}", {}, b"{}", 5.0)
        slow = self.serve(lambda handler: time.sleep(1.0))
        with self.assertRaises(TemporaryError):
            post_json(slow, {}, b"{}", 0.2)

    def test_an_answer_that_is_not_json_is_a_model_error(self) -> None:
        url = self.serve(lambda handler: send(handler, 200, b"<html>busy</html>"))
        with self.assertRaisesRegex(ModelError, "not JSON"):
            post_json(url, {}, b"{}", 5.0)


class Settings(unittest.TestCase):
    def test_the_projects_settings_name_a_provider_and_two_models(self) -> None:
        settings = read_settings(SETTINGS_FILE)
        self.assertTrue(settings.base_url.startswith("https://"))
        self.assertTrue(settings.text_model and settings.vision_model)
        self.assertEqual(settings.api_key_variable, "NVIDIA_API_KEY")

    def test_unusable_settings_give_a_model_error(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            broken = Path(folder) / "model_settings.toml"
            broken.write_text("[provider]\nname = 'x'\n", encoding="utf-8")
            with self.assertRaises(ModelError):
                read_settings(broken)

    def test_the_key_comes_from_the_environment_first_then_from_the_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            env_file = Path(folder) / ".env"
            env_file.write_text("# comment\nOTHER=1\nTEST_MODEL_KEY='from-file'\n", encoding="utf-8")
            with mock.patch.dict(os.environ, {}, clear=True):
                self.assertEqual(read_api_key("TEST_MODEL_KEY", env_file), "from-file")
                self.assertEqual(read_api_key("MISSING_KEY", env_file), "")
            with mock.patch.dict(os.environ, {"TEST_MODEL_KEY": "from-environment"}):
                self.assertEqual(read_api_key("TEST_MODEL_KEY", env_file), "from-environment")

    def test_a_byte_order_mark_does_not_hide_the_key(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            env_file = Path(folder) / ".env"
            env_file.write_bytes(b"\xef\xbb\xbfTEST_MODEL_KEY=from-file\n")
            with mock.patch.dict(os.environ, {}, clear=True):
                self.assertEqual(read_api_key("TEST_MODEL_KEY", env_file), "from-file")


if __name__ == "__main__":
    unittest.main()
