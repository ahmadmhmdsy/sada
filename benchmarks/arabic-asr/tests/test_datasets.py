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

    def test_licence_policy_lists_permissive_and_pending_slices(self) -> None:
        self.assertIn("cc-by-4.0", datasets.COMMERCIAL_LICENCES)
        self.assertIn("mit", datasets.COMMERCIAL_LICENCES)
        self.assertIn("latin-mixed", datasets.SLICES)
        self.assertTrue(datasets.SLICES["gulf"].startswith("Gulf Arabic"))
        self.assertTrue(datasets.SLICES["technical"].startswith("Arabic/English"))
        self.assertTrue(datasets.SLICES["iraqi"].startswith("pending"))
        self.assertTrue(datasets.SLICES["levantine"].startswith("pending"))

    def test_perle_manifest_carries_mit_licence(self) -> None:
        clip = datasets.ClipSpec(
            "gulf-perle-001",
            "gulf",
            "لا تنسى إن success بالسوشيال يبيله process",
            "Perle-ai/ASR_Code_Switch",
            "default",
            "train",
            17,
            "rev",
        )
        payload = clip.to_manifest()
        self.assertEqual(payload["source"]["license"], "MIT")
        self.assertIn("Perle", payload["source"]["attribution"])

    def test_evenly_spaced_selection(self) -> None:
        rows = [(index, {}) for index in range(10)]
        picked = [row[0] for row in datasets._evenly_spaced(rows, 3)]
        self.assertEqual(picked, [0, 4, 9])
        self.assertEqual(datasets._evenly_spaced(rows, 0), [])
        self.assertEqual(len(datasets._evenly_spaced(rows, 20)), 10)


class ManifestReuseTest(unittest.TestCase):
    counts = {"msa_count": 1, "egyptian_count": 2, "latin_count": 1}

    def test_keeps_slices_whose_count_is_unchanged(self) -> None:
        manifest = {
            "clips": [
                {"id": "msa-cv-001", "slice": "msa"},
                {"id": "latin-cv-001", "slice": "latin-mixed"},
                {"id": "egyptian-fleurs-001", "slice": "egyptian"},
                {"id": "gulf-perle-001", "slice": "gulf"},
            ]
        }
        reused = datasets.reused_clips(manifest, self.counts)
        self.assertEqual([clip["id"] for clip in reused["msa"]], ["msa-cv-001"])
        self.assertEqual([clip["id"] for clip in reused["latin-mixed"]], ["latin-cv-001"])
        self.assertNotIn("egyptian", reused)  # asked for 2, manifest has 1 -> rebuild
        self.assertNotIn("gulf", reused)  # extension slice, never reused

    def test_empty_manifest_reuses_nothing(self) -> None:
        self.assertEqual(datasets.reused_clips({}, self.counts), {})

    def test_zero_count_slices_are_not_reused(self) -> None:
        counts = {"msa_count": 0, "egyptian_count": 0, "latin_count": 0}
        reused = datasets.reused_clips({"clips": []}, counts)
        self.assertEqual(reused, {})

if __name__ == "__main__":
    unittest.main()
