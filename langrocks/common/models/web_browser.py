from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


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

    def __str__(self):
        return self.value


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
    url: str
    title: str
    html: Optional[str]
    text: Optional[str]
    screenshot: Optional[bytes]
    buttons: Optional[List[WebBrowserButton]]
    input_fields: Optional[List[WebBrowserInputField]]
    select_fields: Optional[List[WebBrowserSelectField]]
    textarea_fields: Optional[List[WebBrowserTextAreaField]]
    links: Optional[List[WebBrowserLink]]
    images: Optional[List[WebBrowserImage]]
    command_outputs: Optional[List[WebBrowserCommandOutput]]
    command_errors: Optional[List[WebBrowserCommandError]]


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
    video: Optional[bytes] = None


class WebBrowserRequest(BaseModel):
    session_config: WebBrowserSessionConfig
    commands: List[WebBrowserCommand]


class WebBrowserResponse(BaseModel):
    session: WebBrowserSession
    state: WebBrowserState
    content: WebBrowserContent
