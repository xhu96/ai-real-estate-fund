from __future__ import annotations

import asyncio
import dataclasses
import json
import unittest


class _Response:
    """Minimal response shim exposing .status_code, .text and .json()."""

    def __init__(self, status_code: int, body: bytes) -> None:
        self.status_code = status_code
        self._body = body

    @property
    def text(self) -> str:
        return self._body.decode("utf-8", "replace")

    def json(self):
        return json.loads(self._body)


class _ASGIClient:
    """Tiny in-process ASGI client used when httpx (TestClient's dep) is absent.

    The CI image ships FastAPI/Starlette but not httpx, so starlette.testclient
    raises at import time. This driver speaks the ASGI protocol directly so the
    Phase 1 contract tests still execute end-to-end instead of skipping.
    """

    def __init__(self, app) -> None:
        self._app = app

    def _call(self, method: str, path: str, json_body=None):
        if "?" in path:
            raw_path, query = path.split("?", 1)
        else:
            raw_path, query = path, ""
        headers: list[tuple[bytes, bytes]] = []
        body = b""
        if json_body is not None:
            body = json.dumps(json_body).encode()
            headers.append((b"content-type", b"application/json"))
        scope = {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.3"},
            "http_version": "1.1",
            "method": method,
            "path": raw_path,
            "raw_path": raw_path.encode(),
            "query_string": query.encode(),
            "headers": headers,
            "client": ("testclient", 50000),
            "server": ("testserver", 80),
            "scheme": "http",
        }
        sent: list[dict] = []

        async def receive():
            return {"type": "http.request", "body": body, "more_body": False}

        async def send(message):
            sent.append(message)

        asyncio.run(self._app(scope, receive, send))
        status = next(m["status"] for m in sent if m["type"] == "http.response.start")
        payload = b"".join(m.get("body", b"") for m in sent if m["type"] == "http.response.body")
        return _Response(status, payload)

    def get(self, path: str):
        return self._call("GET", path)

    def post(self, path: str, json=None):  # noqa: A002 - mirror TestClient signature
        return self._call("POST", path, json_body=json)


def _client():
    """Build a TestClient against a freshly-created app.

    Prefer Starlette's TestClient; if its httpx dependency is missing, fall back
    to an in-process ASGI driver so the contract is still exercised.
    """
    from app.backend.main import create_app

    app = create_app()
    try:
        from fastapi.testclient import TestClient

        return TestClient(app)
    except Exception:  # httpx not installed -> drive ASGI directly
        return _ASGIClient(app)


def _example_payload() -> dict:
    from ai_real_estate_fund.data_loader import load_property

    return load_property("examples/duplex_sunbelt.json").to_dict()


class Phase1ApiTest(unittest.TestCase):
    def setUp(self) -> None:
        # Force demo-open defaults for every test, regardless of ambient env.
        from app.backend.settings import settings

        self._saved_production = settings.production
        settings.production = dataclasses.replace(
            settings.production,
            environment="development",
            require_api_key=False,
            enable_demo_mode=True,
        )

    def tearDown(self) -> None:
        # Always restore so later tests (and the rest of the suite) see demo mode.
        from app.backend.settings import settings

        settings.production = self._saved_production

    # (a) DEMO OPEN -------------------------------------------------------
    def test_demo_open_analyses_and_institutional_without_key(self) -> None:
        client = _client()
        payload = _example_payload()

        analyses = client.post("/analyses", json=payload)
        self.assertEqual(analyses.status_code, 200, analyses.text)

        institutional = client.post("/institutional/analyze", json=payload)
        self.assertEqual(institutional.status_code, 200, institutional.text)

    # (b) INSTITUTIONAL PERSISTENCE --------------------------------------
    def test_institutional_run_persisted_to_analyses(self) -> None:
        client = _client()
        payload = _example_payload()

        created = client.post("/institutional/analyze", json=payload)
        self.assertEqual(created.status_code, 200, created.text)
        run_id = created.json()["run_id"]

        listed = client.get("/analyses?limit=50")
        self.assertEqual(listed.status_code, 200, listed.text)
        runs = listed.json()
        match = next((run for run in runs if run.get("run_id") == run_id), None)
        self.assertIsNotNone(match, f"run {run_id} not found in /analyses")
        self.assertEqual(match["engine"], "institutional")

    # (c) PRODUCTION FAIL-CLOSED -----------------------------------------
    def test_production_fail_closed_without_key(self) -> None:
        from app.backend.settings import settings

        settings.production = dataclasses.replace(
            settings.production,
            environment="production",
            require_api_key=True,
            enable_demo_mode=False,
            api_keys=(),
            api_key_hashes=(),
        )
        client = _client()
        response = client.post("/analyses", json=_example_payload())
        self.assertEqual(response.status_code, 401, response.text)

    # (c2) STAGING FAIL-CLOSED -------------------------------------------
    def test_staging_does_not_serve_demo_principal(self) -> None:
        # A deployed non-production env (staging) must NOT fall open even if an
        # operator left enable_demo_mode=True and require_api_key=False.
        from app.backend.settings import settings

        settings.production = dataclasses.replace(
            settings.production,
            environment="staging",
            require_api_key=False,
            enable_demo_mode=True,
            api_keys=(),
            api_key_hashes=(),
        )
        client = _client()
        response = client.post("/analyses", json=_example_payload())
        self.assertEqual(response.status_code, 401, response.text)

    # (d) VALIDATION: 422 not 500 ----------------------------------------
    def test_validation_returns_422(self) -> None:
        client = _client()

        self.assertEqual(client.post("/portfolio/optimize", json={}).status_code, 422)
        self.assertEqual(client.post("/watchlist", json={}).status_code, 422)

        missing_fields = client.post("/analyses", json={"name": "x"})
        self.assertEqual(missing_fields.status_code, 422, missing_fields.text)

        bad = dict(_example_payload())
        bad["definitely_not_a_field"] = True
        unknown_field = client.post("/institutional/analyze", json=bad)
        self.assertEqual(unknown_field.status_code, 422, unknown_field.text)

    # (e) HEALTH OPEN -----------------------------------------------------
    def test_health_endpoints_open_without_key(self) -> None:
        client = _client()
        self.assertEqual(client.get("/health").status_code, 200)
        self.assertEqual(client.get("/ops/health").status_code, 200)


if __name__ == "__main__":
    unittest.main()
