"""Unit tests for WER/CER, acronym and timestamp metrics."""

import unittest

from sadabench import metrics


class WerTest(unittest.TestCase):
    def test_identical_text_scores_zero(self) -> None:
        stats = metrics.word_stats("السلام عليكم", "السلام عليكم")
        self.assertEqual(stats.errors, 0)
        self.assertEqual(metrics.rate(stats), 0.0)

    def test_normalisation_avoids_false_errors(self) -> None:
        # Hamza form, diacritics and punctuation differences are not errors.
        stats = metrics.word_stats("أحمدٌ، ذهب", "احمد ذهب")
        self.assertEqual(stats.errors, 0)

    def test_deletions(self) -> None:
        stats = metrics.word_stats("السلام عليكم ورحمة الله", "السلام عليكم")
        self.assertEqual(stats.deletions, 2)
        self.assertEqual(stats.reference_length, 4)
        self.assertAlmostEqual(metrics.rate(stats), 50.0)

    def test_substitution(self) -> None:
        stats = metrics.word_stats("كتاب جديد", "كتاب قديم")
        self.assertEqual(stats.substitutions, 1)
        self.assertAlmostEqual(metrics.rate(stats), 50.0)

    def test_insertion(self) -> None:
        stats = metrics.word_stats("كتاب", "كتاب جديد")
        self.assertEqual(stats.insertions, 1)
        self.assertAlmostEqual(metrics.rate(stats), 100.0)

    def test_cer_uses_characters(self) -> None:
        stats = metrics.char_stats("abc", "abd")
        self.assertEqual(stats.substitutions, 1)
        self.assertAlmostEqual(metrics.rate(stats), 100.0 * 1 / 3)

    def test_arabic_cer(self) -> None:
        stats = metrics.char_stats("سلام", "سلام")
        self.assertEqual(stats.errors, 0)


class AcronymTest(unittest.TestCase):
    def test_transliteration_is_not_preserved(self) -> None:
        occurrences, preserved = metrics.acronym_report(
            "نصدر الملف بصيغة SRT و VTT", "نصدر الملف بصيغة السورتي وفي تيتي"
        )
        self.assertEqual((occurrences, preserved), (2, 0))

    def test_written_acronyms_are_preserved(self) -> None:
        occurrences, preserved = metrics.acronym_report(
            "نصدر الملف بصيغة SRT و VTT", "نصدر الملف بصيغة SRT و VTT"
        )
        self.assertEqual((occurrences, preserved), (2, 2))

    def test_dotted_spelling_counts_as_preserved(self) -> None:
        occurrences, preserved = metrics.acronym_report("رفع تقارير BDF", "رفع تقارير B.D.F")
        self.assertEqual((occurrences, preserved), (1, 1))

    def test_lowercase_counts(self) -> None:
        occurrences, preserved = metrics.acronym_report("افتح ملف PDF", "افتح ملف pdf")
        self.assertEqual((occurrences, preserved), (1, 1))


class EngineDecodeTest(unittest.TestCase):
    def test_engine_output_is_decoded_as_utf8(self) -> None:
        from sadabench.engine import _decode

        arabic = "أعلنت القوات الأمريكية انتهاء مهمتها في العراق."
        self.assertEqual(_decode(arabic.encode("utf-8")), arabic)

    def test_invalid_bytes_are_replaced_not_raised(self) -> None:
        from sadabench.engine import _decode

        self.assertIn("\ufffd", _decode(b"abc\xffdef"))


class LatinReportTest(unittest.TestCase):
    def test_preserved_latin_names(self) -> None:
        occurrences, preserved = metrics.latin_report(
            "تقع قمة Diadem في الجنوب الشرقي", "تقع قمة Diadem في الجنوب الشرقي"
        )
        self.assertEqual((occurrences, preserved), (1, 1))

    def test_transliterated_latin_name_is_not_preserved(self) -> None:
        occurrences, preserved = metrics.latin_report(
            "كانت هناك محطتان في Braintree", "كانت هناك محطتان في برينتري"
        )
        self.assertEqual((occurrences, preserved), (1, 0))

    def test_short_latin_tokens_ignored(self) -> None:
        occurrences, _ = metrics.latin_report("حرف E في اللغة", "حرف E في اللغة")
        self.assertEqual(occurrences, 0)


class TimestampTest(unittest.TestCase):
    def test_parses_word_timestamps(self) -> None:
        output = (
            "[00:00:00.130 --> 00:00:00.650] شكراً\n"
            "[00:00:00.650 --> 00:00:01.480] جزيلاً\n"
        )
        parsed = metrics.parse_word_timestamps(output)
        self.assertTrue(parsed["ok"])
        self.assertEqual(parsed["words"], ["شكراً", "جزيلاً"])
        self.assertEqual(parsed["coverage"], 1.0)

    def test_detects_non_monotonic_timestamps(self) -> None:
        output = (
            "[00:00:02.000 --> 00:00:03.000] ب\n"
            "[00:00:01.000 --> 00:00:01.500] أ\n"
        )
        self.assertFalse(metrics.parse_word_timestamps(output)["ok"])

    def test_plain_text_has_no_timestamps(self) -> None:
        parsed = metrics.parse_word_timestamps("نص عادي بدون أزمنة")
        self.assertFalse(parsed["ok"])
        self.assertEqual(parsed["coverage"], 0.0)


class ScoreTest(unittest.TestCase):
    def test_accumulates_and_reports(self) -> None:
        score = metrics.Score()
        score.add("السلام عليكم", "السلام عليكم", 2.0, 1.0, True)
        score.add("افتح ملف PDF", "افتح ملف بي دي إف", 2.0, 1.0, False)
        payload = score.as_dict()
        self.assertEqual(payload["clips"], 2)
        self.assertGreater(payload["wer_pct"], 0)
        self.assertEqual(payload["acronym_occurrences"], 1)
        self.assertEqual(payload["acronym_preserved_pct"], 0.0)
        self.assertEqual(payload["latin_occurrences"], 1)
        self.assertEqual(payload["latin_preserved_pct"], 0.0)
        self.assertEqual(payload["timestamps_ok_pct"], 50.0)
        self.assertEqual(payload["rtf"], 0.5)


if __name__ == "__main__":
    unittest.main()
