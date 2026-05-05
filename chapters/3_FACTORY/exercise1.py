"""
Exercise 1: Factory Methods as Named Constructors

Complete the Document class.

Run this file directly to execute the small checks at the bottom:

    python exercise1.py

The tests are intentionally simple. They are meant to fail until you finish
implementing the TODO methods.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Document:
    title: str
    body: str

    @classmethod
    def from_plain_text(cls, title: str, text: str):
        """Create a Document from plain text."""
        # TODO: strip title and text, then return cls(...)
        raise NotImplementedError

    @classmethod
    def from_markdown(cls, title: str, markdown: str):
        """Create a Document from simple Markdown input."""
        # TODO:
        # - strip title
        # - remove simple heading markers like #, ##, ### at line starts
        # - remove simple bold markers **
        # - strip the final body
        # - return cls(...)
        raise NotImplementedError

    @classmethod
    def from_html(cls, title: str, html: str):
        """Create a Document from simple HTML input."""
        # TODO:
        # - strip title
        # - remove simple HTML tags
        # - unescape basic HTML entities such as &amp;
        # - normalize whitespace if you want
        # - return cls(...)
        raise NotImplementedError


def test_plain_text_document_creation():
    doc = Document.from_plain_text(" Notes ", " Hello world ")
    assert doc.title == "Notes"
    assert doc.body == "Hello world"


def test_markdown_document_creation():
    doc = Document.from_markdown(
        " Notes ",
        "# Heading\n\nThis is **important**.",
    )
    assert doc.title == "Notes"
    assert "#" not in doc.body
    assert "**" not in doc.body
    assert "Heading" in doc.body
    assert "important" in doc.body


def test_html_document_creation():
    doc = Document.from_html(
        " Notes ",
        "<h1>Heading</h1><p>Alice &amp; Bob</p>",
    )
    assert doc.title == "Notes"
    assert "<h1>" not in doc.body
    assert "Alice & Bob" in doc.body


def run_tests():
    test_plain_text_document_creation()
    test_markdown_document_creation()
    test_html_document_creation()


if __name__ == "__main__":
    run_tests()
    print("Exercise 1 checks passed.")
