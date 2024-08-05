import logging
import tempfile

from pypandoc import convert_text

from langrocks.common.models.tools_pb2 import (
    Content,
    ContentMimeType,
    FileConverterRequest,
    FileConverterResponse,
)

logger = logging.getLogger(__name__)


def _mime_type_to_file_extension(mime_type: ContentMimeType) -> str:
    return {
        ContentMimeType.TEXT: "txt",
        ContentMimeType.JSON: "json",
        ContentMimeType.HTML: "html",
        ContentMimeType.PNG: "png",
        ContentMimeType.JPEG: "jpeg",
        ContentMimeType.SVG: "svg",
        ContentMimeType.PDF: "pdf",
        ContentMimeType.LATEX: "latex",
        ContentMimeType.MARKDOWN: "md",
        ContentMimeType.CSV: "csv",
        ContentMimeType.ZIP: "zip",
        ContentMimeType.TAR: "tar",
        ContentMimeType.GZIP: "gzip",
        ContentMimeType.BZIP2: "bzip2",
        ContentMimeType.XZ: "xz",
        ContentMimeType.DOCX: "docx",
        ContentMimeType.PPTX: "pptx",
        ContentMimeType.XLSX: "xlsx",
        ContentMimeType.DOC: "doc",
        ContentMimeType.PPT: "ppt",
        ContentMimeType.XLS: "xls",
        ContentMimeType.C: "c",
        ContentMimeType.CPP: "cpp",
        ContentMimeType.JAVA: "java",
        ContentMimeType.CSHARP: "cs",
        ContentMimeType.PYTHON: "py",
        ContentMimeType.RUBY: "rb",
        ContentMimeType.PHP: "php",
        ContentMimeType.JAVASCRIPT: "js",
        ContentMimeType.XML: "xml",
        ContentMimeType.CSS: "css",
        ContentMimeType.GIF: "gif",
    }[mime_type]


class FileConverterHandler:
    def process(self, request: FileConverterRequest) -> FileConverterResponse:
        # Get the file name and the new extension
        input_filename = request.file.name or "output"

        # Remove extension if present along with any / or \ or . in the filename
        input_filename = input_filename.split(".")[0].replace("/", "").replace("\\", "")

        output_filename = f"{input_filename}.{_mime_type_to_file_extension(request.target_mime_type)}"

        # Create a temp directory and write to a temp file inside it
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = f"{temp_dir}/{output_filename}"

            # Convert the file
            convert_text(
                request.file.data.decode(),
                _mime_type_to_file_extension(request.target_mime_type),
                format=_mime_type_to_file_extension(request.file.mime_type),
                outputfile=temp_file,
            )

            converted_data = open(temp_file, "rb").read()

        # Return the converted file
        return FileConverterResponse(
            file=Content(
                data=converted_data,
                mime_type=request.target_mime_type,
                name=output_filename,
            )
        )
