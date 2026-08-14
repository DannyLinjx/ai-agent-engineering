from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent_control.static import resolve_spa_asset


class StaticAssetTests(unittest.TestCase):
    def test_spa_fallback_and_path_traversal_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.html").write_text("index", encoding="utf-8")
            (root / "assets").mkdir()
            (root / "assets/app.js").write_text("js", encoding="utf-8")

            self.assertEqual(resolve_spa_asset(root, "assets/app.js"), (root / "assets/app.js").resolve())
            self.assertEqual(resolve_spa_asset(root, "conversation/current"), (root / "index.html").resolve())
            with self.assertRaises(ValueError):
                resolve_spa_asset(root, "../private.txt")
            with self.assertRaises(FileNotFoundError):
                resolve_spa_asset(root, "api/v1/secret")


if __name__ == "__main__":
    unittest.main()
