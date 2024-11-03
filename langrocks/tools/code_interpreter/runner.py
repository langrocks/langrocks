import base64
import logging
import queue
import re
import time
from enum import Enum
from typing import Iterator, Union

from pydantic import BaseModel

from langrocks.common.models.tools_pb2 import (
    CodeRunnerRequest,
    CodeRunnerResponse,
    CodeRunnerState,
    Content,
    ContentMimeType,
)

logger = logging.getLogger(__name__)


class CodeRunnerMessageType(str, Enum):
    CONSOLE = "console"
    ERROR = "error"
    DISPLAY_DATA = "display_data"
    EXECUTE_RESULT = "execute_result"
    STATUS = "status"
    CLEAR_OUTPUT = "clear_output"
    COMM_OPEN = "comm_open"
    COMM_MSG = "comm_msg"
    COMM_CLOSE = "comm_close"


class CodeRunnerMessageMimeType(str, Enum):
    TEXT = "text"
    HTML = "html"
    MARKDOWN = "markdown"
    LATEX = "latex"
    JAVASCRIPT = "javascript"
    SVG = "svg"
    PNG = "png"
    JPEG = "jpeg"
    GIF = "gif"
    PDF = "pdf"
    JSON = "json"


class CodeRunnerMessage(BaseModel):
    type: CodeRunnerMessageType
    mime_type: CodeRunnerMessageMimeType
    content: Union[str, dict, list, bytes]


class CodeRunner:
    def __init__(self, kernel_manager=None):
        self.kernel_manager = kernel_manager

    def process(self, request_iterator: Iterator[CodeRunnerRequest]):
        kernel_id = self.kernel_manager.start_kernel(kernel_name="chroot_python")
        kernel = self.kernel_manager.get_kernel(kernel_id)
        kernel_client = kernel.client()

        kernel_client.start_channels()

        try:
            kernel_client.wait_for_ready(timeout=30)
        except Exception as e:
            logger.error(f"Kernel failed to become ready: {str(e)}")
            try:
                if hasattr(kernel_client, "get_shell_msg"):
                    msg = kernel_client.get_shell_msg(timeout=1)
                    logger.error(f"Last shell message: {msg}")
            except Exception as shell_err:
                logger.error(f"Failed to get shell message: {shell_err}")

            kernel_client.stop_channels()
            self.kernel_manager.shutdown_kernel(kernel_id)
            raise

        self.run_cancelled = False
        self.finished = False

        # # Create a new kernel in the workspace
        for request in request_iterator:
            for msg in self.execute_code(kernel_client, request.source_code):
                if msg.type == CodeRunnerMessageType.CONSOLE:
                    yield CodeRunnerResponse(
                        state=CodeRunnerState.CODE_RUNNING,
                        stdout=[Content(mime_type=ContentMimeType.TEXT, data=msg.content.encode())],
                    )
                elif msg.type == CodeRunnerMessageType.DISPLAY_DATA:
                    yield CodeRunnerResponse(
                        state=CodeRunnerState.CODE_RUNNING,
                        stdout=[Content(mime_type=ContentMimeType.PNG, data=msg.content)],
                    )
                elif msg.type == CodeRunnerMessageType.ERROR:
                    yield CodeRunnerResponse(state=CodeRunnerState.CODE_RUNNING, stderr=msg.content)
                elif msg.type == CodeRunnerMessageType.STATUS:
                    pass

        yield CodeRunnerResponse(state=CodeRunnerState.CODE_FINISHED)

        kernel_client.stop_channels()
        kernel_client.shutdown()

    def execute_code(self, kernel_client, code):
        execution_time_exceeded = False

        start_time = time.time()
        kernel_client.execute(code, store_history=False)
        while True:
            try:
                msg = kernel_client.get_iopub_msg(timeout=1)

                if msg["header"]["msg_type"] == "status" and msg["content"]["execution_state"] == "idle":
                    # Set finish_flag and return when the kernel becomes idle
                    self.finished = True
                    return CodeRunnerMessage(
                        type=CodeRunnerMessageType.STATUS,
                        mime_type=CodeRunnerMessageMimeType.TEXT,
                        content="Execution finished",
                    )

                content = msg["content"]

                if msg["msg_type"] == "stream":
                    yield CodeRunnerMessage(
                        type=CodeRunnerMessageType.CONSOLE,
                        mime_type=CodeRunnerMessageMimeType.TEXT,
                        content=content["text"],
                    )

                elif msg["msg_type"] == "error":
                    content = "\n".join(content["traceback"])
                    ansi_escape = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
                    content = ansi_escape.sub("", content)
                    yield CodeRunnerMessage(
                        type=CodeRunnerMessageType.ERROR,
                        mime_type=CodeRunnerMessageMimeType.TEXT,
                        content=content,
                    )

                elif msg["msg_type"] == "execute_input":
                    pass
                elif msg["msg_type"] == "execute_result":
                    data = content["data"]
                    if "image/png" in data:
                        yield CodeRunnerMessage(
                            type=CodeRunnerMessageType.DISPLAY_DATA,
                            mime_type=CodeRunnerMessageMimeType.PNG,
                            content=base64.b64decode(data["image/png"]),
                        )
                    elif "image/jpeg" in data:
                        yield CodeRunnerMessage(
                            type=CodeRunnerMessageType.DISPLAY_DATA,
                            mime_type=CodeRunnerMessageMimeType.JPEG,
                            content=base64.b64decode(data["image/jpeg"]),
                        )
                    elif "text/html" in data:
                        yield CodeRunnerMessage(
                            type=CodeRunnerMessageType.DISPLAY_DATA,
                            mime_type=CodeRunnerMessageMimeType.HTML,
                            content=data["text/html"],
                        )
                    elif "text/plain" in data:
                        yield CodeRunnerMessage(
                            type=CodeRunnerMessageType.DISPLAY_DATA,
                            mime_type=CodeRunnerMessageMimeType.TEXT,
                            content=data["text/plain"],
                        )
                    else:
                        yield CodeRunnerMessage(
                            type=CodeRunnerMessageType.DISPLAY_DATA,
                            mime_type=CodeRunnerMessageMimeType.JSON,
                            content=data,
                        )
                elif msg["msg_type"] == "display_data":
                    data = content["data"]
                    if "image/png" in data:
                        yield CodeRunnerMessage(
                            type=CodeRunnerMessageType.DISPLAY_DATA,
                            mime_type=CodeRunnerMessageMimeType.PNG,
                            content=base64.b64decode(data["image/png"]),
                        )
                    elif "image/jpeg" in data:
                        yield CodeRunnerMessage(
                            type=CodeRunnerMessageType.DISPLAY_DATA,
                            mime_type=CodeRunnerMessageMimeType.JPEG,
                            content=base64.b64decode(data["image/jpeg"]),
                        )
                    elif "text/html" in data:
                        yield CodeRunnerMessage(
                            type=CodeRunnerMessageType.DISPLAY_DATA,
                            mime_type=CodeRunnerMessageMimeType.HTML,
                            content=data["text/html"],
                        )
                    elif "text/plain" in data:
                        yield CodeRunnerMessage(
                            type=CodeRunnerMessageType.DISPLAY_DATA,
                            mime_type=CodeRunnerMessageMimeType.TEXT,
                            content=data["text/plain"],
                        )
                    else:
                        yield CodeRunnerMessage(
                            type=CodeRunnerMessageType.DISPLAY_DATA,
                            mime_type=CodeRunnerMessageMimeType.JSON,
                            content=data,
                        )
                elif msg["msg_type"] == "execute_reply":
                    pass
                elif msg["msg_type"] == "status":
                    pass
                elif msg["msg_type"] == "clear_output":
                    pass
                elif msg["msg_type"] == "comm_open":
                    pass
                elif msg["msg_type"] == "comm_msg":
                    pass
                elif msg["msg_type"] == "comm_close":
                    pass
                elif msg["msg_type"] == "display_data":
                    pass

            except queue.Empty:
                logger.exception("Queue is empty")
                continue
            except KeyboardInterrupt:
                logger.exception("Keyboard interrupt")
                break
            except Exception as e:
                logger.exception(e)
                # If no messages are available, we'll end up here, but we can just continue and try again.
                elapsed_time = time.time() - start_time
                if elapsed_time > 5:
                    execution_time_exceeded = True
                    break
        if execution_time_exceeded:
            # Send a message to the user that the execution time has exceeded
            return CodeRunnerMessage(
                type=CodeRunnerMessageType.STATUS,
                mime_type=CodeRunnerMessageMimeType.TEXT,
                content="Execution time exceeded",
            )

    def stop(self):
        self.kc.stop_channels()
        self.kc = None
