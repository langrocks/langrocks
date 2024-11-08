from enum import Enum

from pydantic import BaseModel

from langrocks.common.models.tools_pb2 import Content, ContentMimeType


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
    OCTET_STREAM = "application/octet-stream"
    VIDEO_WEBM = "video/webm"
    VIDEO_MP4 = "video/mp4"
    VIDEO_OGG = "video/ogg"
    AUDIO_WEBM = "audio/webm"
    AUDIO_MP3 = "audio/mpeg"

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
        elif self == FileMimeType.OCTET_STREAM:
            return ContentMimeType.OCTET_STREAM
        elif self == FileMimeType.VIDEO_WEBM:
            return ContentMimeType.VIDEO_WEBM
        elif self == FileMimeType.VIDEO_MP4:
            return ContentMimeType.VIDEO_MP4
        elif self == FileMimeType.VIDEO_OGG:
            return ContentMimeType.VIDEO_OGG

        return ContentMimeType.OCTET_STREAM

    @staticmethod
    def from_tools_content_mime_type(mime_type: ContentMimeType):
        if mime_type == ContentMimeType.TEXT:
            return FileMimeType.TEXT
        elif mime_type == ContentMimeType.JSON:
            return FileMimeType.JSON
        elif mime_type == ContentMimeType.HTML:
            return FileMimeType.HTML
        elif mime_type == ContentMimeType.PNG:
            return FileMimeType.PNG
        elif mime_type == ContentMimeType.JPEG:
            return FileMimeType.JPEG
        elif mime_type == ContentMimeType.SVG:
            return FileMimeType.SVG
        elif mime_type == ContentMimeType.PDF:
            return FileMimeType.PDF
        elif mime_type == ContentMimeType.LATEX:
            return FileMimeType.LATEX
        elif mime_type == ContentMimeType.MARKDOWN:
            return FileMimeType.MARKDOWN
        elif mime_type == ContentMimeType.CSV:
            return FileMimeType.CSV
        elif mime_type == ContentMimeType.ZIP:
            return FileMimeType.ZIP
        elif mime_type == ContentMimeType.TAR:
            return FileMimeType.TAR
        elif mime_type == ContentMimeType.GZIP:
            return FileMimeType.GZIP
        elif mime_type == ContentMimeType.BZIP2:
            return FileMimeType.BZIP2
        elif mime_type == ContentMimeType.XZ:
            return FileMimeType.XZ
        elif mime_type == ContentMimeType.DOCX:
            return FileMimeType.DOCX
        elif mime_type == ContentMimeType.PPTX:
            return FileMimeType.PPTX
        elif mime_type == ContentMimeType.XLSX:
            return FileMimeType.XLSX
        elif mime_type == ContentMimeType.DOC:
            return FileMimeType.DOC
        elif mime_type == ContentMimeType.PPT:
            return FileMimeType.PPT
        elif mime_type == ContentMimeType.XLS:
            return FileMimeType.XLS
        elif mime_type == ContentMimeType.C:
            return FileMimeType.C
        elif mime_type == ContentMimeType.CPP:
            return FileMimeType.CPP
        elif mime_type == ContentMimeType.JAVA:
            return FileMimeType.JAVA
        elif mime_type == ContentMimeType.CSHARP:
            return FileMimeType.CSHARP
        elif mime_type == ContentMimeType.PYTHON:
            return FileMimeType.PYTHON
        elif mime_type == ContentMimeType.RUBY:
            return FileMimeType.RUBY
        elif mime_type == ContentMimeType.PHP:
            return FileMimeType.PHP
        elif mime_type == ContentMimeType.JAVASCRIPT:
            return FileMimeType.JAVASCRIPT
        elif mime_type == ContentMimeType.XML:
            return FileMimeType.XML
        elif mime_type == ContentMimeType.CSS:
            return FileMimeType.CSS
        elif mime_type == ContentMimeType.GIF:
            return FileMimeType.GIF
        elif mime_type == ContentMimeType.OCTET_STREAM:
            return FileMimeType.OCTET_STREAM
        elif mime_type == ContentMimeType.VIDEO_WEBM:
            return FileMimeType.VIDEO_WEBM
        elif mime_type == ContentMimeType.VIDEO_MP4:
            return FileMimeType.VIDEO_MP4
        elif mime_type == ContentMimeType.VIDEO_OGG:
            return FileMimeType.VIDEO_OGG

        return FileMimeType.OCTET_STREAM


class File(BaseModel):
    data: bytes = b""
    name: str = ""
    mime_type: FileMimeType = FileMimeType.TEXT

    class Config:
        json_encoders = {
            bytes: lambda v: v.decode(),
        }

    @staticmethod
    def from_tools_content(content: Content):
        return File(
            data=content.data, name=content.name, mime_type=FileMimeType.from_tools_content_mime_type(content.mime_type)
        )
