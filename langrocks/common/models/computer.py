import base64
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

from langrocks.common.models.files import File


class ComputerCommandType(str, Enum):
    COMPUTER_TERMINATE = "COMPUTER_TERMINATE"
    COMPUTER_WAIT = "COMPUTER_WAIT"
    COMPUTER_LEFT_CLICK = "COMPUTER_LEFT_CLICK"
    COMPUTER_LEFT_CLICK_DRAG = "COMPUTER_LEFT_CLICK_DRAG"
    COMPUTER_TYPE = "COMPUTER_TYPE"
    COMPUTER_KEY = "COMPUTER_KEY"
    COMPUTER_CURSOR_POSITION = "COMPUTER_CURSOR_POSITION"
    COMPUTER_MOUSE_MOVE = "COMPUTER_MOUSE_MOVE"
    COMPUTER_SCREENSHOT = "COMPUTER_SCREENSHOT"
    COMPUTER_RIGHT_CLICK = "COMPUTER_RIGHT_CLICK"
    COMPUTER_MIDDLE_CLICK = "COMPUTER_MIDDLE_CLICK"
    COMPUTER_DOUBLE_CLICK = "COMPUTER_DOUBLE_CLICK"

    def __str__(self):
        return self.value


class ComputerDownload(BaseModel):
    url: str
    file: File


class ComputerCommandOutput(BaseModel):
    index: int
    output: str


class ComputerCommandError(BaseModel):
    index: int
    error: str


class ComputerCommand(BaseModel):
    command_type: ComputerCommandType
    selector: Optional[str] = None
    data: str = ""


class ComputerElement(BaseModel):
    selector: str
    text: str


class ComputerButton(ComputerElement):
    pass


class ComputerInputField(ComputerElement):
    pass


class ComputerSelectField(ComputerElement):
    pass


class ComputerTextAreaField(ComputerElement):
    pass


class ComputerLink(ComputerElement):
    url: str


class ComputerImage(ComputerElement):
    src: str


class ComputerContent(BaseModel):
    url: str = ""
    title: str = ""
    html: Optional[str] = None
    text: Optional[str] = None
    markdown: Optional[str] = None
    screenshot: Optional[bytes] = None
    buttons: Optional[List[ComputerButton]] = None
    input_fields: Optional[List[ComputerInputField]] = None
    select_fields: Optional[List[ComputerSelectField]] = None
    textarea_fields: Optional[List[ComputerTextAreaField]] = None
    links: Optional[List[ComputerLink]] = None
    images: Optional[List[ComputerImage]] = None
    command_outputs: Optional[List[ComputerCommandOutput]] = None
    command_errors: Optional[List[ComputerCommandError]] = None
    downloads: Optional[List[ComputerDownload]] = None

    @property
    def b64_screenshot(self):
        import base64

        return base64.b64encode(self.screenshot).decode() if self.screenshot else None

    class Config:
        json_encoders = {
            bytes: lambda v: base64.b64encode(v),
        }


class ComputerSessionConfig(BaseModel):
    init_url: str = ""
    terminate_url_pattern: str = ""
    session_data: str = ""
    timeout: int = 60
    command_timeout: int = 10
    text: bool = True
    html: bool = False
    markdown: bool = False
    persist_session: bool = False
    capture_screenshot: bool = False
    interactive: bool = False
    record_video: bool = False
    annotate: bool = False
    tags_to_extract: List[str] = []


class ComputerState(str, Enum):
    COMPUTER_RUNNING = "COMPUTER_RUNNING"
    COMPUTER_TERMINATED = "COMPUTER_TERMINATED"
    COMPUTER_TIMEOUT = "COMPUTER_TIMEOUT"


class ComputerSession(BaseModel):
    ws_url: Optional[str] = None
    session_data: Optional[str] = None
    videos: Optional[List[File]] = None

    class Config:
        json_encoders = {
            bytes: lambda v: base64.b64encode(v),
        }


class ComputerRequest(BaseModel):
    session_config: ComputerSessionConfig
    commands: List[ComputerCommand]


class ComputerResponse(BaseModel):
    session: ComputerSession
    state: ComputerState
    content: ComputerContent
