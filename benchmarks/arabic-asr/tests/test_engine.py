"""Unit tests for model loading and prompt wiring (no engine, no network)."""

import json
import tempfile
import unittest
from pathlib import Path

from sadabench import engine


class ModelPromptTest(unittest.TestCase):
    def _write_models(self, directory: Path, prompt_file: str | None) -> Path:
        model_path = directory / "model.bin"
        model_path.write_bytes(b"not a real model")
        (directory / "prompt.txt").write_text("تبقى المصطلحات التقنية بالإنجليزية: GPU CPU API", encoding="utf-8")
        payload = {
            "models": {
                "plain": {"path": str(model_path), "language": "ar", "family": "whisper"},
                "prompted": {"path": str(model_path), "language": "ar", "family": "whisper"},
            }
        }
        if prompt_file is not None:
            payload["models"]["prompted"]["prompt_file"] = prompt_file
        path = directory / "models.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_prompt_file_becomes_a_single_prompt_argument(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)
            models_path = self._write_models(directory, "prompt.txt")
            models = engine.load_models(models_path, "engine.exe")["_models"]
            plain = models["plain"]
            prompted = models["prompted"]
            self.assertIsNone(plain.prompt)
            self.assertFalse(any(arg.startswith("--prompt") for arg in plain.args))
            self.assertEqual(prompted.prompt, "تبقى المصطلحات التقنية بالإنجليزية: GPU CPU API")
            self.assertEqual(prompted.args.count("--prompt=" + prompted.prompt), 1)

    def test_missing_prompt_file_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)
            models_path = self._write_models(directory, "does-not-exist.txt")
            with self.assertRaises(FileNotFoundError):
                engine.load_models(models_path, "engine.exe")

    def test_inline_prompt_is_supported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)
            models_path = self._write_models(directory, None)
            payload = json.loads(models_path.read_text(encoding="utf-8"))
            payload["models"]["plain"]["prompt"] = "keep GPU"
            models_path.write_text(json.dumps(payload), encoding="utf-8")
            models = engine.load_models(models_path, "engine.exe")["_models"]
            self.assertEqual(models["plain"].prompt, "keep GPU")
            self.assertIn("--prompt=keep GPU", models["plain"].args)


if __name__ == "__main__":
    unittest.main()
