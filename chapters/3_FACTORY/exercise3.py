"""
Exercise 3: Factory Registry

Refactor the factory to use a registry dictionary and add JSON support.

Run this file directly to execute the small checks at the bottom:

    python exercise3.py

The tests are intentionally simple. They are meant to fail until you finish
implementing the TODO parts.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from html import unescape
from pathlib import Path
import json
import re
import tempfile


@dataclass(frozen=True)
class Document:
    title: str
    body: str

    @classmethod
    def from_plain_text(cls, title: str, text: str):
        return cls(title=title.strip(), body=text.strip())

    @classmethod
    def from_markdown(cls, title: str, markdown: str):
        body = markdown.strip()
        body = re.sub(r"^#{1,6}\s*", "", body, flags=re.MULTILINE)
        body = body.replace("**", "")
        return cls(title=title.strip(), body=body.strip())

    @classmethod
    def from_html(cls, title: str, html: str):
        body = re.sub(r"<[^>]+>", " ", html)
        body = unescape(body)
        body = " ".join(body.split())
        return cls(title=title.strip(), body=body.strip())


class DocumentImporter(ABC):
    @abstractmethod
    def import_document(self, path: str) -> Document:
        pass


class PlainTextDocumentImporter(DocumentImporter):
    def import_document(self, path: str) -> Document:
        file_path = Path(path)
        return Document.from_plain_text(
            file_path.stem,
            file_path.read_text(encoding="utf-8"),
        )


class MarkdownDocumentImporter(DocumentImporter):
    def import_document(self, path: str) -> Document:
        file_path = Path(path)
        return Document.from_markdown(
            file_path.stem,
            file_path.read_text(encoding="utf-8"),
        )


class HtmlDocumentImporter(DocumentImporter):
    def import_document(self, path: str) -> Document:
        file_path = Path(path)
        return Document.from_html(
            file_path.stem,
            file_path.read_text(encoding="utf-8"),
        )


class JsonDocumentImporter(DocumentImporter):
    def import_document(self, path: str) -> Document:
        # TODO:
        # - read JSON from the file
        # - expect keys: title and body
        # - return Document.from_plain_text(title, body)
        raise NotImplementedError


class DocumentImporterFactory:
    # TODO: replace this empty dict with a registry mapping extensions to classes.
    _importers = {}

    @classmethod
    def create_for_file(cls, path: str) -> DocumentImporter:
        # TODO:
        # - get the lowercase file suffix with Path(path).suffix.lower()
        # - look up the importer class in cls._importers
        # - return an instance of that class
        # - raise ValueError for unsupported file types
        raise NotImplementedError


def test_json_importer(root: Path):
    json_path = root / "notes.json"
    json_path.write_text(
        json.dumps({"title": "JSON Notes", "body": "This came from JSON."}),
        encoding="utf-8",
    )

    importer = DocumentImporterFactory.create_for_file(str(json_path))
    assert isinstance(importer, JsonDocumentImporter)

    document = importer.import_document(str(json_path))
    assert document.title == "JSON Notes"
    assert document.body == "This came from JSON."


def test_existing_markdown_importer_still_works(root: Path):
    md_path = root / "notes.md"
    md_path.write_text("# Heading\n\nThis is **important**.", encoding="utf-8")

    importer = DocumentImporterFactory.create_for_file(str(md_path))
    assert isinstance(importer, MarkdownDocumentImporter)
    assert "**" not in importer.import_document(str(md_path)).body


def test_unsupported_file_type(root: Path):
    try:
        DocumentImporterFactory.create_for_file(str(root / "notes.pdf"))
    except ValueError:
        pass
    else:
        raise AssertionError("Unsupported file type should raise ValueError")


def run_tests():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        test_json_importer(root)
        test_existing_markdown_importer_still_works(root)
        test_unsupported_file_type(root)


if __name__ == "__main__":
    run_tests()
    print("Exercise 3 checks passed.")
