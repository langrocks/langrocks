from typing import Iterator

from grpc import ServicerContext

from langrocks.common.display import VirtualDisplayPool
from langrocks.common.models.tools_pb2 import WebBrowserRequest, WebBrowserResponse
from langrocks.common.models.tools_pb2_grpc import ToolsServicer
from langrocks.tools.file_operations.file_converter import FileConverterHandler
from langrocks.tools.web_browser.handler import WebBrowserHandler


class ToolHandler(ToolsServicer):
    def __init__(
        self,
        display_pool: VirtualDisplayPool = None,
        wss_secure=False,
        wss_hostname="localhost",
        wss_port=50052,
        kernel_manager=None,
    ):
        super().__init__()
        self.display_pool = display_pool
        self.wss_secure = wss_secure
        self.wss_hostname = wss_hostname
        self.wss_port = wss_port
        self.kernel_manager = kernel_manager
        self.web_browser_handler = WebBrowserHandler(display_pool, wss_secure, wss_hostname, wss_port)
        self.file_converter_handler = FileConverterHandler()

    def GetWebBrowser(
        self,
        request_iterator: Iterator[WebBrowserRequest],
        context: ServicerContext,
    ) -> Iterator[WebBrowserResponse]:
        return self.web_browser_handler.get_web_browser(request_iterator=request_iterator)

    def GetFileConverter(self, request, context):
        return self.file_converter_handler.process(request)
