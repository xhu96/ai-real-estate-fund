from __future__ import annotations

import dataclasses
import unittest

from tests.test_phase1_api import _client


def _example_payload() -> dict:
    from ai_real_estate_fund.data_loader import load_property

    return load_property("examples/duplex_sunbelt.json").to_dict()


def _content_type(response) -> str:
    # Works for both Starlette TestClient responses and the in-process shim.
    headers = getattr(response, "headers", None)
    if headers is not None:
        try:
            return headers.get("content-type", "")
        except Exception:  # pragma: no cover - defensive
            pass
    return ""


def _body_bytes(response) -> bytes:
    content = getattr(response, "content", None)
    if isinstance(content, (bytes, bytearray)):
        return bytes(content)
    text = getattr(response, "text", "")
    return text.encode("latin-1", "replace")


class ReportPdfApiTest(unittest.TestCase):
    def setUp(self) -> None:
        from app.backend.settings import settings

        self._saved_production = settings.production
        settings.production = dataclasses.replace(
            settings.production,
            environment="development",
            require_api_key=False,
            enable_demo_mode=True,
        )

    def tearDown(self) -> None:
        from app.backend.settings import settings

        settings.production = self._saved_production

    def test_exports_report_pdf(self) -> None:
        client = _client()
        response = client.post("/exports/report.pdf", json=_example_payload())
        self.assertEqual(response.status_code, 200, response.text)
        self.assertIn("application/pdf", _content_type(response))
        body = _body_bytes(response)
        self.assertTrue(body.startswith(b"%PDF-"), body[:8])
        self.assertGreater(len(body), 1000)

    def test_institutional_report_pdf(self) -> None:
        client = _client()
        response = client.post("/institutional/report.pdf", json=_example_payload())
        self.assertEqual(response.status_code, 200, response.text)
        self.assertIn("application/pdf", _content_type(response))
        body = _body_bytes(response)
        self.assertTrue(body.startswith(b"%PDF-"), body[:8])
        self.assertGreater(len(body), 1000)


class RenderReportPdfUnitTest(unittest.TestCase):
    def test_render_report_pdf_returns_pdf_bytes(self) -> None:
        from ai_real_estate_fund.committee import run_institutional_committee
        from ai_real_estate_fund.data_loader import load_property
        from ai_real_estate_fund.report_pdf import render_report_pdf

        prop = load_property("examples/duplex_sunbelt.json")
        decision = run_institutional_committee(prop)
        pdf_bytes = render_report_pdf(decision)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"), pdf_bytes[:8])
        self.assertGreater(len(pdf_bytes), 1000)


if __name__ == "__main__":
    unittest.main()
