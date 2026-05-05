"""
Solution 2: Simple Factory
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from html import unescape
from pathlib import Path
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


class DocumentImporterFactory:
    @staticmethod
    def create_for_file(path: str) -> DocumentImporter:
        suffix = Path(path).suffix.lower()

        if suffix == ".txt":
            return PlainTextDocumentImporter()

        if suffix == ".md":
            return MarkdownDocumentImporter()

        if suffix == ".html":
            return HtmlDocumentImporter()

        raise ValueError(f"Unsupported document type: {path}")


def test_plain_text_importer(root: Path):
    txt_path = root / "notes.txt"
    txt_path.write_text(" Hello plain text ", encoding="utf-8")

    importer = DocumentImporterFactory.create_for_file(str(txt_path))
    assert isinstance(importer, PlainTextDocumentImporter)

    document = importer.import_document(str(txt_path))
    assert document.title == "notes"
    assert document.body == "Hello plain text"


def test_markdown_importer(root: Path):
    md_path = root / "notes.md"
    md_path.write_text("# Heading\n\nThis is **important**.", encoding="utf-8")

    importer = DocumentImporterFactory.create_for_file(str(md_path))
    assert isinstance(importer, MarkdownDocumentImporter)

    document = importer.import_document(str(md_path))
    assert document.title == "notes"
    assert "#" not in document.body
    assert "**" not in document.body
    assert "important" in document.body


def test_html_importer(root: Path):
    html_path = root / "notes.html"
    html_path.write_text("<h1>Heading</h1><p>Alice &amp; Bob</p>", encoding="utf-8")

    importer = DocumentImporterFactory.create_for_file(str(html_path))
    assert isinstance(importer, HtmlDocumentImporter)

    document = importer.import_document(str(html_path))
    assert document.title == "notes"
    assert "<h1>" not in document.body
    assert "Alice & Bob" in document.body


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
        test_plain_text_importer(root)
        test_markdown_importer(root)
        test_html_importer(root)
        test_unsupported_file_type(root)


if __name__ == "__main__":
    run_tests()
    print("Exercise 2 solution checks passed.")
