import base64
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

from langrocks.common.models.files import File


class WebBrowserCommandType(str, Enum):
    GOTO = "GOTO"
    TERMINATE = "TERMINATE"
    WAIT = "WAIT"
    CLICK = "CLICK"
    COPY = "COPY"
    TYPE = "TYPE"
    SCROLL_X = "SCROLL_X"
    SCROLL_Y = "SCROLL_Y"
    ENTER = "ENTER"
    KEY = "KEY"
    CURSOR_POSITION = "CURSOR_POSITION"
    MOUSE_MOVE = "MOUSE_MOVE"
    SCREENSHOT = "SCREENSHOT"
    GET_DOWNLOADS = "GET_DOWNLOADS"
    RIGHT_CLICK = "RIGHT_CLICK"
    MIDDLE_CLICK = "MIDDLE_CLICK"
    DOUBLE_CLICK = "DOUBLE_CLICK"

    def __str__(self):
        return self.value


class WebBrowserDownload(BaseModel):
    url: str
    file: File


class WebBrowserCommandOutput(BaseModel):
    index: int
    output: str


class WebBrowserCommandError(BaseModel):
    index: int
    error: str


class WebBrowserCommand(BaseModel):
    command_type: WebBrowserCommandType
    selector: Optional[str] = None
    data: str = ""


class WebBrowserElement(BaseModel):
    selector: str
    text: str


class WebBrowserButton(WebBrowserElement):
    pass


class WebBrowserInputField(WebBrowserElement):
    pass


class WebBrowserSelectField(WebBrowserElement):
    pass


class WebBrowserTextAreaField(WebBrowserElement):
    pass


class WebBrowserLink(WebBrowserElement):
    url: str


class WebBrowserImage(WebBrowserElement):
    src: str


class WebBrowserContent(BaseModel):
    url: str = ""
    title: str = ""
    html: Optional[str] = None
    text: Optional[str] = None
    markdown: Optional[str] = None
    screenshot: Optional[bytes] = None
    buttons: Optional[List[WebBrowserButton]] = None
    input_fields: Optional[List[WebBrowserInputField]] = None
    select_fields: Optional[List[WebBrowserSelectField]] = None
    textarea_fields: Optional[List[WebBrowserTextAreaField]] = None
    links: Optional[List[WebBrowserLink]] = None
    images: Optional[List[WebBrowserImage]] = None
    command_outputs: Optional[List[WebBrowserCommandOutput]] = None
    command_errors: Optional[List[WebBrowserCommandError]] = None
    downloads: Optional[List[WebBrowserDownload]] = None

    class Config:
        json_encoders = {
            bytes: lambda v: base64.b64encode(v),
        }


class WebBrowserSessionConfig(BaseModel):
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


class WebBrowserState(str, Enum):
    RUNNING = "RUNNING"
    TERMINATED = "TERMINATED"
    TIMEOUT = "TIMEOUT"


class WebBrowserSession(BaseModel):
    ws_url: Optional[str] = None
    session_data: Optional[str] = None
    videos: Optional[List[File]] = None

    class Config:
        json_encoders = {
            bytes: lambda v: base64.b64encode(v),
        }


class WebBrowserRequest(BaseModel):
    session_config: WebBrowserSessionConfig
    commands: List[WebBrowserCommand]


class WebBrowserResponse(BaseModel):
    session: WebBrowserSession
    state: WebBrowserState
    content: WebBrowserContent
