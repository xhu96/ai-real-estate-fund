from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ai_real_estate_fund.production.readiness import ProductionReadinessChecker, render_readiness_markdown
from ai_real_estate_fund.production.release import build_release_manifest
from ai_real_estate_fund.production.settings import ProductionSettings


class ReadinessReleaseTest(unittest.TestCase):
    def test_readiness_report_for_repo(self) -> None:
        settings = ProductionSettings(environment="ci", secret_key="x" * 40, require_api_key=False, enable_demo_mode=True)
        report = ProductionReadinessChecker(root=Path("."), settings=settings).run()
        self.assertGreater(len(report.checks), 10)
        self.assertGreaterEqual(report.score, 80)
        markdown = render_readiness_markdown(report)
        self.assertIn("Production Readiness Report", markdown)

    def test_release_manifest_hashes_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "a.py").write_text("print('hello')\n", encoding="utf-8")
            (root / "README.md").write_text("# demo\n", encoding="utf-8")
            manifest = build_release_manifest(root, version="test")
        self.assertEqual(manifest.project, "ai-real-estate-fund")
        self.assertEqual(len(manifest.files), 2)
        self.assertEqual(len(manifest.root_hash), 64)


if __name__ == "__main__":
    unittest.main()
