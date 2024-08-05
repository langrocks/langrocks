from enum import Enum

from pydantic import BaseModel

from langrocks.common.models.tools_pb2 import ContentMimeType


class FileMimeType(str, Enum):
    TEXT = "text/plain"
    JSON = "application/json"
    HTML = "text/html"
    PNG = "image/png"
    JPEG = "image/jpeg"
    SVG = "image/svg+xml"
    PDF = "application/pdf"
    LATEX = "application/x-latex"
    MARKDOWN = "text/markdown"
    CSV = "text/csv"
    ZIP = "application/zip"
    TAR = "application/x-tar"
    GZIP = "application/gzip"
    BZIP2 = "application/x-bzip2"
    XZ = "application/x-xz"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    PPTX = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    DOC = "application/msword"
    PPT = "application/vnd.ms-powerpoint"
    XLS = "application/vnd.ms-excel"
    C = "text/x-c"
    CPP = "text/x-c++src"
    JAVA = "text/x-java"
    CSHARP = "text/x-csharp"
    PYTHON = "text/x-python"
    RUBY = "text/x-ruby"
    PHP = "text/x-php"
    JAVASCRIPT = "text/javascript"
    XML = "application/xml"
    CSS = "text/css"
    GIF = "image/gif"

    def __str__(self):
        return self.value

    def to_tools_mime_type(self):
        if self == FileMimeType.TEXT:
            return ContentMimeType.TEXT
        elif self == FileMimeType.JSON:
            return ContentMimeType.JSON
        elif self == FileMimeType.HTML:
            return ContentMimeType.HTML
        elif self == FileMimeType.PNG:
            return ContentMimeType.PNG
        elif self == FileMimeType.JPEG:
            return ContentMimeType.JPEG
        elif self == FileMimeType.SVG:
            return ContentMimeType.SVG
        elif self == FileMimeType.PDF:
            return ContentMimeType.PDF
        elif self == FileMimeType.LATEX:
            return ContentMimeType.LATEX
        elif self == FileMimeType.MARKDOWN:
            return ContentMimeType.MARKDOWN
        elif self == FileMimeType.CSV:
            return ContentMimeType.CSV
        elif self == FileMimeType.ZIP:
            return ContentMimeType.ZIP
        elif self == FileMimeType.TAR:
            return ContentMimeType.TAR
        elif self == FileMimeType.GZIP:
            return ContentMimeType.GZIP
        elif self == FileMimeType.BZIP2:
            return ContentMimeType.BZIP2
        elif self == FileMimeType.XZ:
            return ContentMimeType.XZ
        elif self == FileMimeType.DOCX:
            return ContentMimeType.DOCX
        elif self == FileMimeType.PPTX:
            return ContentMimeType.PPTX
        elif self == FileMimeType.XLSX:
            return ContentMimeType.XLSX
        elif self == FileMimeType.DOC:
            return ContentMimeType.DOC
        elif self == FileMimeType.PPT:
            return ContentMimeType.PPT
        elif self == FileMimeType.XLS:
            return ContentMimeType.XLS
        elif self == FileMimeType.C:
            return ContentMimeType.C
        elif self == FileMimeType.CPP:
            return ContentMimeType.CPP
        elif self == FileMimeType.JAVA:
            return ContentMimeType.JAVA
        elif self == FileMimeType.CSHARP:
            return ContentMimeType.CSHARP
        elif self == FileMimeType.PYTHON:
            return ContentMimeType.PYTHON
        elif self == FileMimeType.RUBY:
            return ContentMimeType.RUBY
        elif self == FileMimeType.PHP:
            return ContentMimeType.PHP
        elif self == FileMimeType.JAVASCRIPT:
            return ContentMimeType.JAVASCRIPT
        elif self == FileMimeType.XML:
            return ContentMimeType.XML
        elif self == FileMimeType.CSS:
            return ContentMimeType.CSS
        elif self == FileMimeType.GIF:
            return ContentMimeType.GIF
        else:
            raise ValueError(f"Unknown file mime type: {self}")


class File(BaseModel):
    data: bytes = b""
    name: str = ""
    mime_type: FileMimeType = FileMimeType.TEXT

    class Config:
        json_encoders = {
            bytes: lambda v: v.decode(),
        }
