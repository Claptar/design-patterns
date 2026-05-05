"""
Solution 1: Factory Methods as Named Constructors
"""

from dataclasses import dataclass
from html import unescape
import re


@dataclass(frozen=True)
class Document:
    title: str
    body: str

    @classmethod
    def from_plain_text(cls, title: str, text: str):
        return cls(
            title=title.strip(),
            body=text.strip(),
        )

    @classmethod
    def from_markdown(cls, title: str, markdown: str):
        body = markdown.strip()

        # Remove simple Markdown heading markers at the start of lines.
        body = re.sub(r"^#{1,6}\s*", "", body, flags=re.MULTILINE)

        # Remove simple bold markers.
        body = body.replace("**", "")

        return cls(
            title=title.strip(),
            body=body.strip(),
        )

    @classmethod
    def from_html(cls, title: str, html: str):
        # This is intentionally simple. It is good enough for the exercise,
        # but not a real HTML parser.
        body = re.sub(r"<[^>]+>", " ", html)
        body = unescape(body)
        body = " ".join(body.split())

        return cls(
            title=title.strip(),
            body=body.strip(),
        )


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
    print("Exercise 1 solution checks passed.")
