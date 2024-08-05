import logging
from typing import List

import grpc

from langrocks.common.models.files import File, FileMimeType
from langrocks.common.models.tools_pb2 import Content, FileConverterRequest
from langrocks.common.models.tools_pb2_grpc import ToolsStub

logger = logging.getLogger(__name__)


class FileOperations:
    def __init__(self, base_url: str = "", path: str = ""):
        self.base_url = base_url
        self.path = path

        self._channel = grpc.insecure_channel(
            f"{base_url}/{path}",
        )
        self._stub = ToolsStub(self._channel)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._channel.close()

    def convert_file(
        self,
        data: bytes,
        filename: str,
        input_mime_type: FileMimeType,
        output_mime_type: FileMimeType,
        options: List[str] = [],
    ) -> File:
        """
        Converts and returns a file
        """
        response = self._stub.GetFileConverter(
            FileConverterRequest(
                file=Content(
                    data=data,
                    mime_type=input_mime_type.to_tools_mime_type(),
                    name=filename,
                ),
                target_mime_type=output_mime_type.to_tools_mime_type(),
                options=options,
            )
        )

        return File(
            name=response.file.name,
            data=response.file.data,
            mime_type=output_mime_type,
        )
