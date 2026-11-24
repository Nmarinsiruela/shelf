import unicodedata

from shelf.store import Store
from tests.support import ShelfTestCase


class SearchCommandTest(ShelfTestCase):
    def setUp(self) -> None:
        super().setUp()
        store = Store(self.shelf_path)
        store.add("Dune", "Frank Herbert")
        store.add("Kindred", "Octavia E. Butler", "reading")
        store.add("One Hundred Years of Solitude", "Gabriel García Márquez")

    def test_finds_a_book_by_part_of_its_title(self):
        result = self.shelf("search", "Hundred")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout,
            "#3 [to-read] One Hundred Years of Solitude by Gabriel García Márquez\n",
        )

    def test_finds_a_book_by_part_of_its_author(self):
        result = self.shelf("search", "Butler")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "#2 [reading] Kindred by Octavia E. Butler\n")

    def test_matching_ignores_case_including_accented_letters(self):
        result = self.shelf("search", "GARCÍA")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout,
            "#3 [to-read] One Hundred Years of Solitude by Gabriel García Márquez\n",
        )

    def test_an_accent_typed_as_a_combining_mark_still_matches(self):
        decomposed = unicodedata.normalize("NFD", "GARCÍA")

        result = self.shelf("search", decomposed)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("García Márquez", result.stdout)

    def test_matches_use_the_same_format_and_order_as_list(self):
        listed = self.shelf("list").stdout.splitlines()

        result = self.shelf("search", "er")  # Herbert and Butler, not García Márquez

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), [listed[0], listed[1]])

    def test_no_match_says_so_and_succeeds(self):
        result = self.shelf("search", "Tolkien")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, 'No books match "Tolkien".\n')

    def test_search_without_text_is_a_usage_error(self):
        result = self.shelf("search")

        self.assertEqual(result.returncode, 2)
        self.assertIn("usage: shelf search", result.stderr)

    def test_search_does_not_modify_the_shelf_file(self):
        before = (self.shelf_path.read_bytes(), self.shelf_path.stat().st_mtime_ns)

        self.shelf("search", "Herbert")
        self.shelf("search", "Tolkien")

        after = (self.shelf_path.read_bytes(), self.shelf_path.stat().st_mtime_ns)
        self.assertEqual(before, after)


class SearchEmptyShelfTest(ShelfTestCase):
    def test_an_empty_shelf_matches_nothing_and_is_not_created(self):
        result = self.shelf("search", "Dune")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, 'No books match "Dune".\n')
        self.assertFalse(self.shelf_path.exists())
