import sys
import types
import unittest
from unittest.mock import patch

from dashboard.ai_insights import (
    build_ai_insights_input,
    generate_ai_decision_brief,
)


class AIInsightsTests(unittest.TestCase):
    def test_input_is_anonymized_and_limited_to_five_matches(self):
        recommendations = [
            {
                "INVESTOR_NAME": f"Investor {index}",
                "COMPANY_ID": "private-company-id",
                "INVESTOR_TYPE": "VC",
                "INVESTOR_HQ_COUNTRY": "US",
                "COMPATIBILITY_SCORE": 84.2,
                "EVIDENCE_COVERAGE": 0.75,
                "INDUSTRY_SCORE": 90,
            }
            for index in range(7)
        ]

        payload = build_ai_insights_input(
            {
                "COMPANY_NAME": "Confidential Startup",
                "COMPANY_ID": "private-company-id",
                "STARTUP_INDUSTRY": "Climate",
                "STARTUP_COUNTRY": "US",
                "STARTUP_STAGE": "Seed",
            },
            recommendations,
        )

        self.assertEqual(len(payload["top_matches"]), 5)
        self.assertNotIn("Confidential Startup", str(payload))
        self.assertNotIn("Investor 0", str(payload))
        self.assertNotIn("private-company-id", str(payload))
        self.assertEqual(payload["top_matches"][0]["evidence_coverage_pct"], 75.0)

        recommendations[0]["EVIDENCE_COVERAGE"] = 0.755
        payload = build_ai_insights_input({}, recommendations)
        self.assertEqual(payload["top_matches"][0]["evidence_coverage_pct"], 75.5)

    def test_generate_brief_uses_responses_api_without_storing_response(self):
        calls = {}

        class FakeResponses:
            def create(self, **kwargs):
                calls.update(kwargs)
                return types.SimpleNamespace(output_text="Prioritize evidence-backed matches.")

        class FakeOpenAI:
            def __init__(self, **kwargs):
                calls["client"] = kwargs
                self.responses = FakeResponses()

        fake_openai = types.ModuleType("openai")
        fake_openai.OpenAI = FakeOpenAI
        fake_openai.OpenAIError = RuntimeError

        with patch.dict(sys.modules, {"openai": fake_openai}):
            brief = generate_ai_decision_brief(
                {"STARTUP_INDUSTRY": "Climate"},
                [
                    {
                        "INVESTOR_NAME": "Investor",
                        "COMPATIBILITY_SCORE": 85,
                        "EVIDENCE_COVERAGE": 0.8,
                    }
                ],
                api_key="test-key",
                model="test-model",
            )

        self.assertEqual(brief, "Prioritize evidence-backed matches.")
        self.assertFalse(calls["store"])
        self.assertEqual(calls["model"], "test-model")
        self.assertEqual(calls["client"]["timeout"], 30.0)


if __name__ == "__main__":
    unittest.main()
