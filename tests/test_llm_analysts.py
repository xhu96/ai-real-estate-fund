from __future__ import annotations

import json
import unittest

from ai_real_estate_fund.committee import run_institutional_committee
from ai_real_estate_fund.data_loader import load_property
from ai_real_estate_fund.institutional.analysts import PERSONAS, build_fact_pack
from ai_real_estate_fund.institutional.memo import render_institutional_memo
from ai_real_estate_fund.llm import OfflineAnalystClient, safe_json_loads


class RecordingClient:
    """Fake LLM client that returns canned, persona-tagged JSON."""

    model = "fake-model"

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def complete(self, system: str, prompt: str, *, temperature: float = 0.3) -> str:
        self.calls.append((system, prompt))
        return json.dumps(
            {
                "thesis": f"Canned thesis #{len(self.calls)}.",
                "key_points": ["Point A", "Point B", "Point C"],
                "questions": ["Question 1?"],
            }
        )


class LlmAnalystTests(unittest.TestCase):
    def setUp(self) -> None:
        self.prop = load_property("examples/duplex_sunbelt.json")

    def test_committee_is_deterministic_without_llm(self) -> None:
        decision = run_institutional_committee(self.prop)
        self.assertIsNone(decision.llm_review)
        self.assertIsNone(decision.to_dict()["llm_review"])

    def test_fact_pack_is_json_safe_and_grounded(self) -> None:
        decision = run_institutional_committee(self.prop)
        pack = build_fact_pack(decision)
        json.dumps(pack)
        self.assertEqual(pack["committee"]["overall_score"], decision.overall_score)
        self.assertEqual(len(pack["weakest_workstreams"]), 5)
        self.assertEqual(len(pack["scenarios"]), len(decision.scenarios))

    def test_analysts_attach_commentary_without_touching_scores(self) -> None:
        baseline = run_institutional_committee(self.prop)
        client = RecordingClient()
        decision = run_institutional_committee(self.prop, llm_client=client)
        self.assertEqual(decision.overall_score, baseline.overall_score)
        self.assertEqual(decision.recommendation, baseline.recommendation)
        self.assertIsNotNone(decision.llm_review)
        self.assertEqual(len(decision.llm_review.opinions), len(PERSONAS))
        self.assertEqual(len(client.calls), len(PERSONAS))
        # later personas see earlier opinions
        self.assertIn("prior_opinions", client.calls[-1][1])
        self.assertNotIn("prior_opinions", client.calls[0][1])
        payload = decision.to_dict()
        json.dumps(payload)
        self.assertEqual(payload["llm_review"]["model"], "fake-model")

    def test_memo_renders_commentary_section(self) -> None:
        decision = run_institutional_committee(self.prop, llm_client=RecordingClient())
        memo = render_institutional_memo(decision)
        self.assertIn("## Analyst Commentary (LLM)", memo)
        self.assertIn("### IC Chair", memo)
        self.assertIn("Canned thesis", memo)
        # no LLM -> no section
        plain = render_institutional_memo(run_institutional_committee(self.prop))
        self.assertNotIn("Analyst Commentary", plain)

    def test_offline_client_and_json_salvage(self) -> None:
        decision = run_institutional_committee(self.prop, llm_client=OfflineAnalystClient())
        self.assertEqual(len(decision.llm_review.opinions), len(PERSONAS))
        self.assertEqual(decision.llm_review.model, "offline-rules")
        self.assertEqual(safe_json_loads('noise {"a": 1} trailing'), {"a": 1})
        self.assertEqual(safe_json_loads("not json at all"), {})


if __name__ == "__main__":
    unittest.main()


class ProviderSelectionTests(unittest.TestCase):
    PROVIDER_ENVS = ["NVIDIA_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY", "LLM_PROVIDER", "LLM_MODEL", "LLM_BASE_URL"]

    def setUp(self) -> None:
        import os
        from unittest import mock

        from ai_real_estate_fund import llm

        self._saved = {k: os.environ.pop(k, None) for k in self.PROVIDER_ENVS}
        self._dotenv_patch = mock.patch.object(llm, "load_dotenv_if_present", lambda *a, **k: None)
        self._dotenv_patch.start()

    def tearDown(self) -> None:
        import os

        self._dotenv_patch.stop()
        for k, v in self._saved.items():
            if v is not None:
                os.environ[k] = v
            else:
                os.environ.pop(k, None)

    def test_provider_detection_order_and_explicit_override(self) -> None:
        import os

        from ai_real_estate_fund.llm import AnthropicClient, GeminiClient, OpenAICompatibleClient, client_for_provider, detect_provider

        os.environ["GEMINI_API_KEY"] = "g"
        os.environ["ANTHROPIC_API_KEY"] = "a"
        self.assertEqual(detect_provider(), "anthropic")
        os.environ["LLM_PROVIDER"] = "gemini"
        self.assertEqual(detect_provider(), "gemini")
        self.assertIsInstance(client_for_provider("gemini"), GeminiClient)
        self.assertIsInstance(client_for_provider("anthropic"), AnthropicClient)
        os.environ["OPENAI_API_KEY"] = "o"
        client = client_for_provider("openai")
        self.assertIsInstance(client, OpenAICompatibleClient)
        self.assertIn("api.openai.com", client.base_url)

    def test_missing_key_and_unknown_provider_raise(self) -> None:
        from ai_real_estate_fund.llm import OfflineAnalystClient, client_for_provider, client_from_env, live_client_from_env

        with self.assertRaises(RuntimeError):
            live_client_from_env()
        with self.assertRaises(RuntimeError):
            client_for_provider("anthropic")
        with self.assertRaises(RuntimeError):
            client_for_provider("doesnotexist")
        self.assertIsInstance(client_from_env(), OfflineAnalystClient)

    def test_request_shapes_per_provider(self) -> None:
        from ai_real_estate_fund.llm import AnthropicClient, GeminiClient, OpenAICompatibleClient

        url, headers, body = OpenAICompatibleClient(api_key="k", model="m").build_request("sys", "hi", 0.3)
        self.assertTrue(url.endswith("/chat/completions"))
        self.assertEqual(headers["Authorization"], "Bearer k")
        self.assertEqual(body["messages"][0], {"role": "system", "content": "sys"})

        url, headers, body = AnthropicClient(api_key="k", model="m").build_request("sys", "hi", 0.3)
        self.assertTrue(url.endswith("/messages"))
        self.assertEqual(headers["x-api-key"], "k")
        self.assertIn("anthropic-version", headers)
        self.assertEqual(body["system"], "sys")
        self.assertEqual(body["messages"], [{"role": "user", "content": "hi"}])

        url, headers, body = GeminiClient(api_key="k", model="m").build_request("sys", "hi", 0.3)
        self.assertIn("models/m:generateContent", url)
        self.assertEqual(headers["x-goog-api-key"], "k")
        self.assertEqual(body["system_instruction"]["parts"][0]["text"], "sys")
        self.assertEqual(body["contents"][0]["parts"][0]["text"], "hi")
