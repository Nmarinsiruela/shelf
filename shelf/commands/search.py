"""shelf search TEXT"""

from __future__ import annotations

import argparse
import unicodedata

from shelf.store import Store


def register(subparsers) -> None:
    parser = subparsers.add_parser("search", help="find books by title or author")
    parser.add_argument("text", metavar="TEXT", help="text to look for; case does not matter")
    parser.set_defaults(handler=run)


def run(args: argparse.Namespace, store: Store) -> int:
    wanted = fold(args.text)
    matches = [
        book for book in store.load()
        if wanted in fold(book.title) or wanted in fold(book.author)
    ]
    if not matches:
        print(f'No books match "{args.text}".')
        return 0
    for book in matches:
        print(book)
    return 0


def fold(text: str) -> str:
    """Text in a form where case doesn't matter, accented letters included.

    Normalizing to NFC first makes an accent typed as a separate combining
    mark equal to the precomposed letter. Normalizing again after casefold()
    keeps its output comparable, since casefolding can undo NFC.
    """
    return unicodedata.normalize("NFC", unicodedata.normalize("NFC", text).casefold())
