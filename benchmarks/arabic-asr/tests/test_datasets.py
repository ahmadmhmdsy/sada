"""Unit tests for clip selection rules and manifest metadata (no network)."""

import unittest

from sadabench import datasets


class SelectionRulesTest(unittest.TestCase):
    msa_sentence = "اجتمع الفريق صباح اليوم لمناقشة خطة الإطلاق واتفقنا على تأجيل المشروع أسبوعا واحدا"

    def test_accepts_plain_msa_sentence(self) -> None:
        self.assertTrue(len(self.msa_sentence) >= 40)
        self.assertTrue(datasets.qualifies_msa(self.msa_sentence))

    def test_rejects_short_sentence(self) -> None:
        self.assertFalse(datasets.qualifies_msa("قصير جدا"))

    def test_rejects_latin_and_digits(self) -> None:
        self.assertFalse(datasets.qualifies_msa(self.msa_sentence + " GPU"))
        self.assertFalse(datasets.qualifies_msa(self.msa_sentence + " 2026"))

    def test_acronym_hits(self) -> None:
        self.assertEqual(datasets.acronym_hits("افتح ملف PDF ثم صدّر SRT"), 2)
        self.assertEqual(datasets.acronym_hits("افتح ملف بي دي إف"), 0)
        self.assertEqual(datasets.acronym_hits("شغّل GPU"), 1)
        self.assertEqual(datasets.acronym_hits("عادي"), 0)

    def test_manifest_metadata_carries_licence(self) -> None:
        clip = datasets.ClipSpec(
            id="msa-cv-001",
            slice="msa",
            reference=self.msa_sentence,
            dataset="MohamedRashad/common-voice-18-arabic",
            config="default",
            split="validation",
            offset=42,
            revision="abc123",
        )
        payload = clip.to_manifest()
        self.assertEqual(payload["source"]["license"], "CC0-1.0")
        self.assertIn("Common Voice", payload["source"]["attribution"])
        self.assertEqual(payload["source"]["offset"], 42)
        fleurs = datasets.ClipSpec("e", "egyptian", "مرحبا", "google/fleurs", "ar_eg", "test", 0, "rev")
        self.assertEqual(fleurs.to_manifest()["source"]["license"], "CC-BY-4.0")

    def test_licence_policy_lists_copyleft_and_pending_slices(self) -> None:
        self.assertIn("cc-by-4.0", datasets.COMMERCIAL_LICENCES)
        self.assertIn("latin-mixed", datasets.SLICES)
        self.assertTrue(datasets.SLICES["iraqi"].startswith("pending"))
        self.assertTrue(datasets.SLICES["technical"].startswith("pending"))


if __name__ == "__main__":
    unittest.main()
