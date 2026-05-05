"""
Solution 3: Factory Registry
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
        file_path = Path(path)
        data = json.loads(file_path.read_text(encoding="utf-8"))
        return Document.from_plain_text(
            data["title"],
            data["body"],
        )


class DocumentImporterFactory:
    _importers = {
        ".txt": PlainTextDocumentImporter,
        ".md": MarkdownDocumentImporter,
        ".html": HtmlDocumentImporter,
        ".json": JsonDocumentImporter,
    }

    @classmethod
    def create_for_file(cls, path: str) -> DocumentImporter:
        suffix = Path(path).suffix.lower()

        try:
            importer_class = cls._importers[suffix]
        except KeyError:
            raise ValueError(f"Unsupported document type: {path}") from None

        return importer_class()


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
    print("Exercise 3 solution checks passed.")
