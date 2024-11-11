import logging
from enum import Enum
from typing import Iterator, List, Optional, Union

import grpc
from pydantic import BaseModel

from langrocks.common.models import tools_pb2
from langrocks.common.models.tools_pb2_grpc import ToolsStub

logger = logging.getLogger(__name__)


class CodeRunnerState(str, Enum):
    CODE_RUNNING = "CODE_RUNNING"
    CODE_TERMINATED = "CODE_TERMINATED"
    CODE_TIMEOUT = "CODE_TIMEOUT"
    CODE_FINISHED = "CODE_FINISHED"


class ContentMimeType(str, Enum):
    TEXT = "TEXT"
    JSON = "JSON"
    HTML = "HTML"
    PNG = "PNG"
    JPEG = "JPEG"
    SVG = "SVG"
    PDF = "PDF"
    LATEX = "LATEX"
    MARKDOWN = "MARKDOWN"
    CSV = "CSV"
    ZIP = "ZIP"
    TAR = "TAR"
    GZIP = "GZIP"
    BZIP2 = "BZIP2"
    XZ = "XZ"
    DOCX = "DOCX"
    PPTX = "PPTX"
    XLSX = "XLSX"
    DOC = "DOC"
    PPT = "PPT"
    XLS = "XLS"
    C = "C"
    CPP = "CPP"
    JAVA = "JAVA"
    CSHARP = "CSHARP"
    PYTHON = "PYTHON"
    RUBY = "RUBY"
    PHP = "PHP"
    JAVASCRIPT = "JAVASCRIPT"
    XML = "XML"
    CSS = "CSS"
    GIF = "GIF"


class Content(BaseModel):
    mime_type: ContentMimeType
    data: bytes
    name: Optional[str] = None


class CodeRunnerSession(BaseModel):
    session_id: str
    session_data: Optional[str] = None


def convert_proto_code_runner_state(state: tools_pb2.CodeRunnerState) -> CodeRunnerState:
    if state == tools_pb2.CodeRunnerState.CODE_RUNNING:
        return CodeRunnerState.CODE_RUNNING
    elif state == tools_pb2.CodeRunnerState.CODE_TERMINATED:
        return CodeRunnerState.CODE_TERMINATED
    elif state == tools_pb2.CodeRunnerState.CODE_TIMEOUT:
        return CodeRunnerState.CODE_TIMEOUT
    elif state == tools_pb2.CodeRunnerState.CODE_FINISHED:
        return CodeRunnerState.CODE_FINISHED
    else:
        return CodeRunnerState.CODE_RUNNING


def convert_proto_to_content(content: tools_pb2.Content) -> Content:
    return Content(
        mime_type=ContentMimeType(tools_pb2.ContentMimeType.Name(content.mime_type)),
        data=content.data,
        name=content.name if content.name else None,
    )


def convert_proto_to_code_runner_session(
    session: tools_pb2.CodeRunnerSession,
) -> Optional[CodeRunnerSession]:
    if session is None:
        return None
    return CodeRunnerSession(
        session_id=session.session_id,
        session_data=session.session_data,
    )


class CodeRunnerContextManager:
    def __init__(self, base_url: str = "", path: str = ""):
        try:
            self._channel = grpc.insecure_channel(
                base_url,
            )
            self._stub = ToolsStub(self._channel)
            self._session = None
        except Exception as e:
            raise ConnectionError(f"Error connecting to gRPC server: {str(e)}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._channel.close()

    def run_code(
        self,
        source_code: str,
        timeout_secs: int = 30,
        session: Optional[CodeRunnerSession] = None,
        files: List[Content] = None,
    ) -> Iterator[Union[str, bytes]]:
        """
        Run code and return an iterator of outputs.
        """
        request = tools_pb2.CodeRunnerRequest(
            source_code=source_code,
            timeout_secs=timeout_secs,
            session=(
                tools_pb2.CodeRunnerSession(
                    session_id=session.session_id,
                    session_data=session.session_data,
                )
                if session
                else None
            ),
            files=[
                tools_pb2.Content(
                    mime_type=getattr(tools_pb2.ContentMimeType, file.mime_type),
                    data=file.data,
                    name=file.name,
                )
                for file in (files or [])
            ],
        )

        try:
            for response in self._stub.GetCodeRunner(iter([request])):
                if response.stdout:
                    for content in response.stdout:
                        yield content.data
                if response.stderr:
                    yield response.stderr.encode()
                if response.content:
                    for content in response.content:
                        yield content.data
                if response.session:
                    self._session = convert_proto_to_code_runner_session(response.session)
                if response.state != tools_pb2.CodeRunnerState.CODE_RUNNING:
                    break

        except Exception as e:
            logger.error(f"Error running code: {e}")
            raise

    def run_python_code(
        self,
        source_code: str,
        timeout_secs: int = 30,
        files: List[Content] = None,
    ) -> Iterator[Union[str, bytes]]:
        """
        Run Python code and return an iterator of outputs.
        """
        return self.run_code(source_code, timeout_secs, files)

    def run_python_file(
        self,
        file_path: str,
        timeout_secs: int = 30,
        additional_files: List[Content] = None,
    ) -> Iterator[Union[str, bytes]]:
        """
        Run a Python file and return an iterator of outputs.
        """
        with open(file_path, "r") as f:
            source_code = f.read()
        return self.run_python_code(source_code, timeout_secs, additional_files)


class CodeRunner:
    def __init__(
        self,
        url: str = "",
        base_url: str = "",
        path: str = "",
        session: Optional[CodeRunnerSession] = None,
    ):
        self._channel = grpc.insecure_channel(
            url if url else base_url,
        )
        self._stub = ToolsStub(self._channel)
        self._session = session
        self._state = CodeRunnerState.CODE_RUNNING

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._channel.close()

    def get_state(self) -> CodeRunnerState:
        """
        Get the state of the code runner.
        """
        return self._state

    def get_session(self) -> Optional[CodeRunnerSession]:
        """
        Get the session data of the code runner.
        """
        return self._session

    def run_code(
        self,
        source_code: str,
        timeout_secs: int = 30,
        files: List[Content] = None,
    ) -> Iterator[Union[str, bytes]]:
        """
        Run code and return an iterator of outputs.
        """
        request = tools_pb2.CodeRunnerRequest(
            source_code=source_code,
            timeout_secs=timeout_secs,
            session=(
                tools_pb2.CodeRunnerSession(
                    session_id=self._session.session_id,
                    session_data=self._session.session_data,
                )
                if self._session
                else None
            ),
            files=[
                tools_pb2.Content(
                    mime_type=getattr(tools_pb2.ContentMimeType, file.mime_type),
                    data=file.data,
                    name=file.name,
                )
                for file in (files or [])
            ],
        )

        try:
            for response in self._stub.GetCodeRunner(iter([request])):
                if response.stdout:
                    for content in response.stdout:
                        yield content.data
                if response.stderr:
                    yield response.stderr.encode()
                if response.content:
                    for content in response.content:
                        yield content.data
                if response.session:
                    self._session = convert_proto_to_code_runner_session(response.session)
                if response.state != tools_pb2.CodeRunnerState.CODE_RUNNING:
                    self._state = convert_proto_code_runner_state(response.state)
                    break

        except Exception as e:
            logger.error(f"Error running code: {e}")
            raise

    def run_python_code(
        self,
        source_code: str,
        timeout_secs: int = 30,
        files: List[Content] = None,
    ) -> Iterator[Union[str, bytes]]:
        """
        Run Python code and return an iterator of outputs.
        """
        return self.run_code(source_code, timeout_secs, files)

    def run_python_file(
        self,
        file_path: str,
        timeout_secs: int = 30,
        additional_files: List[Content] = None,
    ) -> Iterator[Union[str, bytes]]:
        """
        Run a Python file and return an iterator of outputs.
        """
        with open(file_path, "r") as f:
            source_code = f.read()
        return self.run_python_code(source_code, timeout_secs, additional_files)
