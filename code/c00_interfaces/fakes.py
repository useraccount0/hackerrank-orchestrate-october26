"""Stand-ins for tests, so that no test needs a real AI model or another component's code."""

from __future__ import annotations

from collections.abc import Callable

from c00_interfaces.records import ModelCall, ModelQuestion


class FakeModelGateway:
    def __init__(self, answer_for: Callable[[ModelQuestion], str]):
        self.answer_for = answer_for
        self.questions: list[ModelQuestion] = []

    def ask(self, question: ModelQuestion) -> str:
        self.questions.append(question)
        return self.answer_for(question)

    def calls(self) -> tuple[ModelCall, ...]:
        return tuple(ModelCall(question.purpose, "fake", "fake-model", 0, 0, 0.0, False)
                     for question in self.questions)
