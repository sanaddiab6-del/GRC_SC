"""The pinned-model check warns about drift but never blocks."""
import io
import unittest
import urllib.error
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError

from ai_onboarding import llm_config, llm_engine
from ai_onboarding.model_check import OK, WARN, check_ai_model

ENV = {"AI_PROVIDER": "local", "LOCAL_AI_BASE_URL": "http://192.168.65.254:11434",
       "LOCAL_AI_MODEL_DEFAULT": llm_config.PINNED_MODEL}


def ollama(models, version=llm_config.PINNED_OLLAMA_VERSION):
    def fetch(url):
        return {"version": version} if url.endswith("/api/version") else {"models": models}
    return fetch


PINNED = [{"name": llm_config.PINNED_MODEL, "digest": llm_config.PINNED_MODEL_DIGEST}]


class ModelCheckTests(unittest.TestCase):
    def levels(self, results):
        return [r.level for r in results]

    def test_pinned_model_and_version_pass(self):
        results = check_ai_model(ENV, ollama(PINNED))
        self.assertEqual(self.levels(results), [OK, OK])

    def test_missing_model_warns_with_fix(self):
        results = check_ai_model(ENV, ollama([{"name": "qwen2.5:3b", "digest": "abc"}]))
        self.assertIn(WARN, self.levels(results))
        self.assertTrue(any(f"ollama pull {llm_config.PINNED_MODEL}" in r.message for r in results))

    def test_different_digest_warns(self):
        results = check_ai_model(ENV, ollama([{"name": llm_config.PINNED_MODEL, "digest": "f" * 64}]))
        self.assertTrue(any("expected 0edcdef34593" in r.message for r in results))

    def test_different_ollama_version_warns(self):
        results = check_ai_model(ENV, ollama(PINNED, version="0.1.0"))
        self.assertEqual(self.levels(results), [WARN, OK])

    def test_model_override_warns(self):
        env = {**ENV, "LOCAL_AI_MODEL_GRC_CAPABILITY_SELECTION": "qwen2.5:3b"}
        results = check_ai_model(env, ollama(PINNED))
        self.assertTrue(any("LOCAL_AI_MODEL_GRC_CAPABILITY_SELECTION=qwen2.5:3b" in r.message for r in results))

    def test_unreachable_ollama_warns_without_raising(self):
        def down(url):
            raise urllib.error.URLError("refused")
        results = check_ai_model(ENV, down)
        self.assertEqual(self.levels(results), [WARN])

    def test_disabled_ai_and_unsafe_url_do_not_call_ollama(self):
        def never(url):
            raise AssertionError("must not call Ollama")
        self.assertEqual(self.levels(check_ai_model({}, never)), [WARN])
        cloud = {**ENV, "LOCAL_AI_BASE_URL": "https://api.openai.com"}
        self.assertEqual(self.levels(check_ai_model(cloud, never)), [WARN])

    def test_command_warns_by_default_and_fails_only_when_strict(self):
        with patch("ai_onboarding.management.commands.check_ai_model.check_ai_model",
                   return_value=check_ai_model({}, ollama(PINNED))):
            out = io.StringIO()
            call_command("check_ai_model", stdout=out)
            self.assertIn("WARN", out.getvalue())
            with self.assertRaises(CommandError):
                call_command("check_ai_model", "--strict", stdout=io.StringIO())


class PinnedDefaultTests(unittest.TestCase):
    def test_default_model_is_the_pinned_model(self):
        self.assertEqual(llm_config.DEFAULT_MODEL, llm_config.PINNED_MODEL)
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(llm_engine._configured_model(), llm_config.PINNED_MODEL)
