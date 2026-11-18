"""Unit tests for Arabic text normalisation."""

import unittest

from sadabench import normalize as norm


class NormalizeTest(unittest.TestCase):
    def test_removes_diacritics(self) -> None:
        self.assertEqual(norm.normalize("مُحَمَّدٌ"), "محمد")

    def test_removes_tatweel(self) -> None:
        self.assertEqual(norm.normalize("مـــحمد"), "محمد")

    def test_unifies_hamza_forms(self) -> None:
        self.assertEqual(norm.normalize("أحمد"), "احمد")
        self.assertEqual(norm.normalize("إبراهيم"), "ابراهيم")
        self.assertEqual(norm.normalize("آمن"), "امن")
        self.assertEqual(norm.normalize("مؤمن"), "مومن")
        self.assertEqual(norm.normalize("مسئول"), "مسيول")

    def test_unifies_alef_maqsura(self) -> None:
        self.assertEqual(norm.normalize("هدى"), "هدي")

    def test_keeps_ta_marbuta(self) -> None:
        self.assertEqual(norm.normalize("مدرسة"), "مدرسة")

    def test_normalises_digits(self) -> None:
        self.assertEqual(norm.normalize("١٢٣"), "123")
        self.assertEqual(norm.normalize("۱۲۳"), "123")

    def test_replaces_punctuation_with_spaces(self) -> None:
        self.assertEqual(norm.normalize("مرحبا، بالعالم!"), "مرحبا بالعالم")
        # Hamza unification turns the waw-with-hamza in سؤال into a plain waw.
        self.assertEqual(norm.normalize("سؤال؟ جواب."), "سوال جواب")

    def test_lowercases_latin(self) -> None:
        self.assertEqual(norm.normalize("GPU و PDF"), "gpu و pdf")

    def test_words_and_characters(self) -> None:
        self.assertEqual(norm.words("السلام، عليكم"), ["السلام", "عليكم"])
        self.assertEqual(norm.characters("أ ب"), ["ا", "ب"])


if __name__ == "__main__":
    unittest.main()
