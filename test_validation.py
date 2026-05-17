"""
Teste unitare pentru functia sanitize_text() din MindGuard.

Acest fisier contine teste automate care verifica toate cele 5 verificari
implementate in functia de validare a input-ului utilizatorului:
    1. Verificare tip (trebuie sa fie string)
    2. Verificare lungime minima (>= MIN_POST_LENGTH caractere)
    3. Verificare lungime maxima (<= MAX_POST_LENGTH caractere)
    4. Eliminare caractere de control
    5. Filtrare cuvinte interzise (FORBIDDEN_WORDS)

Cum se ruleaza:
    # Direct cu unittest (vine cu Python, nu necesita instalare):
    python -m unittest test_validation.py -v

    # Sau cu pytest daca e instalat:
    pytest test_validation.py -v

Pe laptopul cu Flet instalat, fisierul importa direct din MindGuard.py.
Toate testele trebuie sa treaca (PASS) pentru ca aplicatia sa fie
considerata stabila din punct de vedere al validarii input-ului.
"""

import unittest
import sys
import os

# Adaugam directorul curent in path pentru a putea importa MindGuard.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Importam functia si constantele din modulul principal MindGuard.
    from MindGuard import sanitize_text, MIN_POST_LENGTH, MAX_POST_LENGTH, FORBIDDEN_WORDS
except ImportError as e:
    print(f"EROARE: Nu pot importa MindGuard.")
    print(f"Asigura-te ca:")
    print(f"  1. Fisierul MindGuard.py exista in acelasi folder cu test_validation.py")
    print(f"  2. Flet este instalat (pip install flet)")
    print(f"  3. Rulezi comanda din folderul corect")
    print(f"\nDetalii eroare: {e}")
    sys.exit(1)


class TestSanitizeTextTypeValidation(unittest.TestCase):
    """Teste pentru verificarea tipului de date (Test 1 din sanitize_text)."""

    def test_string_input_is_accepted(self):
        """Un string valid trebuie acceptat."""
        result, error = sanitize_text("Buna ziua tuturor!")
        self.assertIsNone(error)
        self.assertEqual(result, "Buna ziua tuturor!")

    def test_integer_input_is_rejected(self):
        """Un numar intreg trebuie respins (nu e string)."""
        result, error = sanitize_text(12345)
        self.assertIsNone(result)
        self.assertIsNotNone(error)

    def test_none_input_is_rejected(self):
        """Valoarea None trebuie respinsa (nu e string)."""
        result, error = sanitize_text(None)
        self.assertIsNone(result)
        self.assertIsNotNone(error)

    def test_list_input_is_rejected(self):
        """O lista trebuie respinsa (nu e string)."""
        result, error = sanitize_text(["text", "in", "lista"])
        self.assertIsNone(result)
        self.assertIsNotNone(error)


class TestSanitizeTextLengthValidation(unittest.TestCase):
    """Teste pentru verificarea lungimii textului (Test 2 si 3)."""

    def test_empty_string_is_rejected(self):
        """Un string complet gol trebuie respins."""
        result, error = sanitize_text("")
        self.assertIsNone(result)
        self.assertIsNotNone(error)

    def test_only_spaces_is_rejected(self):
        """Un string format doar din spatii trebuie respins."""
        result, error = sanitize_text("     ")
        self.assertIsNone(result)
        self.assertIsNotNone(error)

    def test_text_below_minimum_length_is_rejected(self):
        """Texte sub MIN_POST_LENGTH caractere trebuie respinse."""
        result, error = sanitize_text("a")
        self.assertIsNone(result)
        self.assertIn("minim", error.lower())

    def test_text_at_minimum_length_is_accepted(self):
        """Texte cu exact MIN_POST_LENGTH caractere trebuie acceptate."""
        text = "a" * MIN_POST_LENGTH
        result, error = sanitize_text(text)
        self.assertIsNone(error)

    def test_text_at_maximum_length_is_accepted(self):
        """Texte cu exact MAX_POST_LENGTH caractere trebuie acceptate."""
        text = "a" * MAX_POST_LENGTH
        result, error = sanitize_text(text)
        self.assertIsNone(error)
        self.assertEqual(len(result), MAX_POST_LENGTH)

    def test_text_above_maximum_length_is_rejected(self):
        """Texte peste MAX_POST_LENGTH trebuie respinse (protectie anti-spam)."""
        text = "a" * (MAX_POST_LENGTH + 1)
        result, error = sanitize_text(text)
        self.assertIsNone(result)
        self.assertIn("prea lung", error.lower())


class TestSanitizeTextControlCharacters(unittest.TestCase):
    """Teste pentru eliminarea caracterelor de control (Test 4)."""

    def test_null_character_is_removed(self):
        """Caracterul null trebuie eliminat din text."""
        result, error = sanitize_text("Salut\x00toata lumea!")
        self.assertIsNone(error)
        self.assertNotIn("\x00", result)

    def test_bell_character_is_removed(self):
        """Caracterul bell trebuie eliminat din text."""
        result, error = sanitize_text("Buna\x07ziua")
        self.assertIsNone(error)
        self.assertNotIn("\x07", result)

    def test_newline_is_preserved(self):
        """Newline este permis (nu e caracter de control problematic)."""
        result, error = sanitize_text("Linia 1\nLinia 2")
        self.assertIsNone(error)
        self.assertIn("\n", result)

    def test_tab_is_preserved(self):
        """Tab-ul este permis."""
        result, error = sanitize_text("Coloana1\tColoana2")
        self.assertIsNone(error)
        self.assertIn("\t", result)


class TestSanitizeTextForbiddenWords(unittest.TestCase):
    """Teste pentru filtrarea cuvintelor interzise (Test 5)."""

    def test_normal_text_is_accepted(self):
        """Text normal, fara cuvinte interzise, trebuie acceptat."""
        result, error = sanitize_text("Astazi ma simt mult mai bine!")
        self.assertIsNone(error)
        self.assertEqual(result, "Astazi ma simt mult mai bine!")

    def test_forbidden_word_spam_is_rejected(self):
        """Cuvantul 'spam' trebuie respins."""
        result, error = sanitize_text("Acesta este spam evident")
        self.assertIsNone(result)
        self.assertIsNotNone(error)

    def test_forbidden_word_uppercase_is_rejected(self):
        """Verificarea trebuie sa fie case-insensitive (SPAM, Spam, spam)."""
        result, error = sanitize_text("Acesta este SPAM evident")
        self.assertIsNone(result)
        self.assertIsNotNone(error)

    def test_forbidden_word_hack_is_rejected(self):
        """Cuvantul 'hack' trebuie respins."""
        result, error = sanitize_text("Cum sa hack acest sistem?")
        self.assertIsNone(result)
        self.assertIsNotNone(error)

    def test_forbidden_word_virus_is_rejected(self):
        """Cuvantul 'virus' trebuie respins."""
        result, error = sanitize_text("Atentie, are virus!")
        self.assertIsNone(result)
        self.assertIsNotNone(error)


class TestSanitizeTextConstants(unittest.TestCase):
    """Teste pentru verificarea constantelor de configurare."""

    def test_min_length_is_reasonable(self):
        """MIN_POST_LENGTH trebuie sa fie cel putin 1."""
        self.assertGreaterEqual(MIN_POST_LENGTH, 1)

    def test_max_length_is_reasonable(self):
        """MAX_POST_LENGTH trebuie sa fie semnificativ mai mare decat MIN."""
        self.assertGreater(MAX_POST_LENGTH, MIN_POST_LENGTH)
        self.assertGreaterEqual(MAX_POST_LENGTH, 100)

    def test_forbidden_words_exist(self):
        """Lista de cuvinte interzise nu trebuie sa fie goala."""
        self.assertGreater(len(FORBIDDEN_WORDS), 0)

    def test_forbidden_words_are_lowercase(self):
        """Cuvintele interzise trebuie sa fie cu litere mici (pentru
        compararea case-insensitive cu .lower())."""
        for word in FORBIDDEN_WORDS:
            self.assertEqual(word, word.lower())


if __name__ == "__main__":
    # Ruleaza toate testele cand scriptul este executat direct.
    unittest.main(verbosity=2)
