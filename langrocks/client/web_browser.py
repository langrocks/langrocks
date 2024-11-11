import base64
import logging
import threading
from queue import Queue
from typing import Iterator, List, Optional

import grpc

from langrocks.common.models import tools_pb2
from langrocks.common.models.files import File, FileMimeType
from langrocks.common.models.tools_pb2_grpc import ToolsStub
from langrocks.common.models.web_browser import (
    WebBrowserButton,
    WebBrowserCommand,
    WebBrowserCommandError,
    WebBrowserCommandOutput,
    WebBrowserCommandType,
    WebBrowserContent,
    WebBrowserDownload,
    WebBrowserImage,
    WebBrowserInputField,
    WebBrowserLink,
    WebBrowserSelectField,
    WebBrowserSession,
    WebBrowserSessionConfig,
    WebBrowserState,
    WebBrowserTextAreaField,
)

logger = logging.getLogger(__name__)


def convert_proto_web_browser_state(
    state: tools_pb2.WebBrowserState,
) -> WebBrowserState:
    if state == tools_pb2.WebBrowserState.RUNNING:
        return WebBrowserState.RUNNING
    elif state == tools_pb2.WebBrowserState.TERMINATED:
        return WebBrowserState.TERMINATED
    elif state == tools_pb2.WebBrowserState.TIMEOUT:
        return WebBrowserState.TIMEOUT
    else:
        return WebBrowserState.RUNNING


def convert_web_browser_state_to_proto(
    state: WebBrowserState,
) -> tools_pb2.WebBrowserState:
    if state == WebBrowserState.RUNNING:
        return tools_pb2.WebBrowserState.RUNNING
    elif state == WebBrowserState.TERMINATED:
        return tools_pb2.WebBrowserState.TERMINATED
    elif state == WebBrowserState.TIMEOUT:
        return tools_pb2.WebBrowserState.TIMEOUT
    else:
        return tools_pb2.WebBrowserState.RUNNING


def convert_web_browser_command_to_proto(
    command: WebBrowserCommand,
) -> tools_pb2.WebBrowserCommand:
    return tools_pb2.WebBrowserCommand(
        type=command.command_type,
        selector=command.selector,
        data=command.data,
    )


def convert_proto_to_web_browser_content(
    content: tools_pb2.WebBrowserContent,
) -> WebBrowserContent:
    return WebBrowserContent(
        url=content.url,
        title=content.title,
        html=content.html,
        text=content.text,
        screenshot=content.screenshot,
        buttons=[
            WebBrowserButton(
                selector=button.selector,
                text=button.text,
            )
            for button in content.buttons
        ],
        input_fields=[
            WebBrowserInputField(
                selector=input.selector,
                text=input.text,
            )
            for input in content.input_fields
        ],
        select_fields=[
            WebBrowserSelectField(
                selector=select.selector,
                text=select.text,
            )
            for select in content.select_fields
        ],
        textarea_fields=[
            WebBrowserTextAreaField(
                selector=textarea.selector,
                text=textarea.text,
            )
            for textarea in content.textarea_fields
        ],
        images=[
            WebBrowserImage(
                selector=image.selector,
                text=image.text,
                src=image.src,
            )
            for image in content.images
        ],
        links=[
            WebBrowserLink(
                selector=link.selector,
                text=link.text,
                url=link.url,
            )
            for link in content.links
        ],
        command_outputs=[
            WebBrowserCommandOutput(
                index=output.index,
                output=output.output,
            )
            for output in content.command_outputs
        ],
        command_errors=[
            WebBrowserCommandError(
                index=error.index,
                error=error.error,
            )
            for error in content.command_errors
        ],
        downloads=[
            WebBrowserDownload(
                url=download.url,
                file=File.from_tools_content(download.file),
            )
            for download in content.downloads
        ],
    )


def convert_proto_to_web_browser_session(
    session: tools_pb2.WebBrowserSession,
) -> Optional[WebBrowserSession]:
    if session is None:
        return None
    return WebBrowserSession(
        ws_url=session.ws_url,
        session_data=session.session_data,
        videos=session.videos,
    )


def convert_web_browser_session_config_to_proto(
    config: WebBrowserSessionConfig,
) -> tools_pb2.WebBrowserSessionConfig:
    return tools_pb2.WebBrowserSessionConfig(
        init_url=config.init_url,
        terminate_url_pattern=config.terminate_url_pattern,
        session_data=config.session_data,
        timeout=config.timeout,
        command_timeout=config.command_timeout,
        text=config.text,
        html=config.html,
        markdown=config.markdown,
        persist_session=config.persist_session,
        capture_screenshot=config.capture_screenshot,
        interactive=config.interactive,
        annotate=config.annotate,
        record_video=config.record_video,
        tags_to_extract=config.tags_to_extract,
    )


def commands_to_proto_web_browser_request_iterator(
    config: WebBrowserSessionConfig, commands: List[WebBrowserCommand]
) -> Iterator[tools_pb2.WebBrowserRequest]:
    try:
        data = tools_pb2.WebBrowserRequest(
            session_config=convert_web_browser_session_config_to_proto(config),
            commands=[convert_web_browser_command_to_proto(command) for command in commands],
        )
    except Exception as e:
        logger.error(f"Error converting commands to proto: {e}")
        raise e

    yield data


def commands_iterator_to_proto_web_browser_request_iterator(
    config: WebBrowserSessionConfig, commands_iterator: Iterator[WebBrowserCommand]
) -> Iterator[tools_pb2.WebBrowserRequest]:
    for command in commands_iterator:
        try:
            data = tools_pb2.WebBrowserRequest(
                session_config=convert_web_browser_session_config_to_proto(config),
                commands=[convert_web_browser_command_to_proto(command)],
            )
        except Exception as e:
            logger.error(f"Error converting commands to proto: {e}")
            raise e

        yield data


class WebBrowserContextManager:
    def __init__(self, base_url: str = "", path: str = ""):
        self._channel = grpc.insecure_channel(
            f"{base_url}/{path}",
            options=[("grpc.max_receive_message_length", 100 * 1024 * 1024)],
        )
        self._stub = ToolsStub(self._channel)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._channel.close()

    def run_commands_interactive(
        self,
        commands: List[WebBrowserCommand] = [],
        commands_iterator: Iterator[WebBrowserCommand] = None,
        config: WebBrowserSessionConfig = WebBrowserSessionConfig(interactive=True),
    ) -> tuple[WebBrowserSession, Iterator[WebBrowserContent]]:
        """
        Run the web browser commands and returns the session and the response iterator.
        """

        def _response_iterator(
            response: Iterator[tools_pb2.WebBrowserResponse],
        ) -> Iterator[WebBrowserContent]:
            for resp in response:
                yield convert_proto_to_web_browser_content(resp.content)

        # If commands_iterator is provided, use it instead of commands
        if commands_iterator:
            response = self._stub.GetWebBrowser(
                commands_iterator_to_proto_web_browser_request_iterator(config, commands_iterator),
            )
        else:
            response = self._stub.GetWebBrowser(
                commands_to_proto_web_browser_request_iterator(config, commands),
            )

        first_response = next(response)

        return (
            convert_proto_to_web_browser_session(first_response.session),
            _response_iterator(response),
        )

    def run_commands(
        self,
        commands: List[WebBrowserCommand],
        config: WebBrowserSessionConfig = WebBrowserSessionConfig(interactive=False),
    ) -> WebBrowserContent:
        """
        Run the web browser commands and returns the content.
        """
        response = self._stub.GetWebBrowser(
            commands_to_proto_web_browser_request_iterator(config, commands),
        )

        _ = next(response)
        second_response = next(response)

        return convert_proto_to_web_browser_content(second_response.content)

    def get_html_from_page(self, url: str) -> str:
        """
        Get the HTML content of a page.
        """
        return self.run_commands(
            commands=[
                WebBrowserCommand(
                    command_type=WebBrowserCommandType.GOTO,
                    data=url,
                ),
                WebBrowserCommand(
                    command_type=WebBrowserCommandType.WAIT,
                    data="body",
                ),
            ],
            config=WebBrowserSessionConfig(html=True),
        ).html

    def get_text_from_page(self, url: str) -> str:
        """
        Get the text content of a page.
        """
        return self.run_commands(
            commands=[
                WebBrowserCommand(
                    command_type=WebBrowserCommandType.GOTO,
                    data=url,
                ),
                WebBrowserCommand(
                    command_type=WebBrowserCommandType.WAIT,
                    data="body",
                ),
            ],
            config=WebBrowserSessionConfig(text=True),
        ).text

    def get_elements_from_page(
        self, url: str, selectors: str = ["a", "img", "button", "input", "textarea", "select"]
    ) -> str:
        """
        Get matching elements from a page.
        """
        return self.run_commands(
            commands=[
                WebBrowserCommand(
                    command_type=WebBrowserCommandType.GOTO,
                    data=url,
                ),
                WebBrowserCommand(
                    command_type=WebBrowserCommandType.WAIT,
                    selector="body",
                ),
            ],
            config=WebBrowserSessionConfig(tags_to_extract=selectors),
        )

    def get_images_from_page(self, url: str) -> List[WebBrowserImage]:
        """
        Get the images from a page.
        """
        return self.get_elements_from_page(url, ["img"]).images

    def get_links_from_page(self, url: str) -> List[WebBrowserLink]:
        """
        Get the links from a page.
        """
        return self.get_elements_from_page(url, ["a"]).links

    def get_buttons_from_page(self, url: str) -> List[WebBrowserButton]:
        """
        Get the buttons from a page.
        """
        return self.get_elements_from_page(url, ["button"]).buttons

    def get_input_fields_from_page(self, url: str) -> List[WebBrowserInputField]:
        """
        Get the input fields from a page.
        """
        return self.get_elements_from_page(url, ["input"]).input_fields

    def get_select_fields_from_page(self, url: str) -> List[WebBrowserSelectField]:
        """
        Get the select fields from a page.
        """
        return self.get_elements_from_page(url, ["select"]).select_fields

    def get_textarea_fields_from_page(self, url: str) -> List[WebBrowserTextAreaField]:
        """
        Get the textarea fields from a page.
        """
        return self.get_elements_from_page(url, ["textarea"]).textarea_fields


class WebBrowser:
    def __init__(
        self,
        url: str = "",
        base_url: str = "",
        path: str = "",
        session_data: str = None,
        text: bool = True,
        html: bool = False,
        markdown: bool = False,
        persist_session: bool = False,
        capture_screenshot: bool = False,
        interactive: bool = True,
        record_video: bool = False,
        annotate: bool = False,
        tags_to_extract: List[str] = [],
    ):
        self.SENTINAL = object()  # Used to signal the end of the queue
        self.session_data = session_data
        self.text = text
        self.html = html
        self.markdown = markdown
        self.persist_session = persist_session
        self.capture_screenshot = capture_screenshot
        self.interactive = interactive
        self.record_video = record_video
        self.annotate = annotate
        self.tags_to_extract = tags_to_extract

        try:
            self._channel = grpc.insecure_channel(
                url if url else f"{base_url}/{path}",
                options=[("grpc.max_receive_message_length", 100 * 1024 * 1024)],
            )
            # Try to establish connection by creating stub
            self._stub = ToolsStub(self._channel)
            # Test connection by making a simple unary call
            grpc.channel_ready_future(self._channel).result(timeout=5)
        except grpc.FutureTimeoutError:
            self._channel.close()
            raise ConnectionError(f"Could not connect to gRPC server at {url if url else f'{base_url}/{path}'}")
        except Exception as e:
            self._channel.close()
            raise ConnectionError(f"Error connecting to gRPC server: {str(e)}")

        self._output_session_data = None
        self._wss_url = None
        self._state = None
        self._commands_queue = Queue()  # Queue containing list of commands
        self._content_queue = Queue()  # Queue with resulting content from running each set of commands
        self._commands_cv = threading.Condition()
        self._content_cv = threading.Condition()
        self._last_content = None
        self._videos = []
        self._videos_event = threading.Event()

    def __enter__(self):
        self._response_thread = threading.Thread(target=self._response_iterator)
        self._response_thread.start()

        # Pull the first response from the content queue
        with self._content_cv:
            while self._content_queue.empty():
                self._content_cv.wait()
            self._content_queue.get()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # If the session is still running, terminate it
        if self._state == WebBrowserState.RUNNING:
            self.terminate()

        self._response_thread.join()
        self._channel.close()

    def _request_iterator(self):
        # Send the session config before any commands
        yield tools_pb2.WebBrowserRequest(
            session_config=tools_pb2.WebBrowserSessionConfig(
                session_data=self.session_data,
                text=self.text,
                html=self.html,
                markdown=self.markdown,
                persist_session=self.persist_session,
                capture_screenshot=self.capture_screenshot,
                interactive=self.interactive,
                annotate=self.annotate,
                tags_to_extract=self.tags_to_extract,
                record_video=self.record_video,
            ),
        )
        with self._commands_cv:
            # Wait for the first set of commands
            while self._commands_queue.empty():
                self._commands_cv.wait()

            while not self._commands_queue.empty():
                commands = self._commands_queue.get()
                if commands is self.SENTINAL:
                    break

                yield tools_pb2.WebBrowserRequest(
                    commands=[convert_web_browser_command_to_proto(command) for command in commands],
                )

                # Wait for the next set of commands
                while self._commands_queue.empty():
                    self._commands_cv.wait()

    def _response_iterator(self):
        try:
            for response in self._stub.GetWebBrowser(self._request_iterator()):
                if response.HasField("session"):
                    self._output_session_data = response.session.session_data
                    self._wss_url = response.session.ws_url

                    if response.session.videos:
                        for video in response.session.videos:
                            self._videos.append(File.from_tools_content(video))
                        self._videos_event.set()
                if response.HasField("content"):
                    self._last_content = convert_proto_to_web_browser_content(response.content)
                    self._content_queue.put(self._last_content)
                if convert_web_browser_state_to_proto(response.state) is not self._state:
                    self._state = convert_proto_web_browser_state(response.state)

                    # If the session is terminated, add a SENTINAL to the queue to signal the end
                    if self._state == WebBrowserState.TERMINATED:
                        self._commands_queue.put(self.SENTINAL)
                        self._content_queue.put(None)

                with self._content_cv:
                    self._content_cv.notify_all()
        except Exception as e:
            self._state = WebBrowserState.TERMINATED
            # Add error to content queue to unblock __enter__
            self._content_queue.put(None)
            with self._content_cv:
                self._content_cv.notify_all()
            # Re-raise the exception to bubble it up
            raise ConnectionError(f"Error in response iterator: {e}")

    def get_state(self) -> WebBrowserState:
        """
        Get the state of the web browser.
        """
        return self._state

    def get_session_data(self) -> str:
        """
        Get the session data of the web browser.
        """
        return self._output_session_data

    def get_videos(self) -> List[str]:
        """
        Get the videos of the web browser as base64 encoded strings.
        """
        self._videos_event.wait(timeout=5)
        return self._videos

    def get_wss_url(self) -> str:
        """
        Get the WebSocket URL of the web browser for interactive sessions.
        """
        return self._wss_url

    def run_commands(
        self,
        commands: List[WebBrowserCommand],
    ) -> WebBrowserContent:
        """
        Run the web browser commands and returns the content.
        """
        self._commands_queue.put(commands)
        with self._commands_cv:
            self._commands_cv.notify_all()

        with self._content_cv:
            while self._content_queue.empty():
                self._content_cv.wait()
            return self._content_queue.get()

    def run_command(
        self,
        command: WebBrowserCommand,
    ) -> WebBrowserContent:
        """
        Run the web browser command and returns the content.
        """
        return self.run_commands(
            commands=[command],
        )

    def terminate(self):
        """
        Terminate the web browser and returns the session data.
        """
        # Send a terminate command
        self.run_command(
            command=WebBrowserCommand(
                command_type=WebBrowserCommandType.TERMINATE,
            ),
        )

        return self.get_session_data()

    # Helper functions
    def goto(self, url: str, wait_timeout: int = 2000) -> WebBrowserContent:
        """
        Navigate to a URL.
        """
        return self.run_commands(
            commands=[
                WebBrowserCommand(
                    command_type=WebBrowserCommandType.GOTO,
                    data=url,
                ),
                WebBrowserCommand(
                    command_type=WebBrowserCommandType.WAIT,
                    selector="body",
                    data=str(wait_timeout),
                ),
            ]
        )

    def wait(self, selector: str, wait_timeout: int = 2000) -> WebBrowserContent:
        """
        Wait for an element to appear.
        """
        return self.run_command(
            command=WebBrowserCommand(
                command_type=WebBrowserCommandType.WAIT,
                selector=selector,
                data=str(wait_timeout),
            ),
        )

    def click(self, selector: str) -> WebBrowserContent:
        """
        Click on an element.
        """
        return self.run_command(
            command=WebBrowserCommand(
                command_type=WebBrowserCommandType.CLICK,
                selector=selector,
            ),
        )

    def type(self, selector: str, text: str) -> WebBrowserContent:
        """
        Type text into an input field.
        """
        return self.run_command(
            command=WebBrowserCommand(
                command_type=WebBrowserCommandType.TYPE,
                selector=selector,
                data=text,
            ),
        )

    def get_html(self, url=None) -> str:
        """
        Get the HTML content of the page.
        """
        if self._last_content and self._last_content.url == url:
            return self._last_content.html

        # Run a WAIT command and return the HTML content
        return self.goto(url).html if url else self.wait("body").html

    def get_text(self, url=None) -> str:
        """
        Get the text content of the page.
        """
        if self._last_content and self._last_content.url == url:
            return self._last_content.text

        # Run a WAIT command and return the text content
        return self.goto(url).text if url else self.wait("body").text

    def get_markdown(self, url=None) -> str:
        """
        Get the markdown content of the page.
        """
        if self._last_content and self._last_content.url == url:
            return self._last_content.markdown

        # Run a WAIT command and return the markdown content
        return self.goto(url).markdown if url else self.wait("body").markdown

    def get_images(self, url=None) -> List[WebBrowserImage]:
        """
        Get the images from the page.
        """
        if self._last_content and self._last_content.url == url:
            return self._last_content.images

        # Run a WAIT command and return the images
        return self.goto(url).images if url else self.wait("body").images

    def get_links(self, url=None) -> List[WebBrowserLink]:
        """
        Get the links from the page.
        """
        if self._last_content and self._last_content.url == url:
            return self._last_content.links

        # Run a WAIT command and return the links
        return self.goto(url).links if url else self.wait("body").links

    def get_buttons(self, url=None) -> List[WebBrowserButton]:
        """
        Get the buttons from the page.
        """
        if self._last_content and self._last_content.url == url:
            return self._last_content.buttons

        # Run a WAIT command and return the buttons
        return self.goto(url).buttons if url else self.wait("body").buttons

    def get_input_fields(self, url=None) -> List[WebBrowserInputField]:
        """
        Get the input fields from the page.
        """
        if self._last_content and self._last_content.url == url:
            return self._last_content.input_fields

        # Run a WAIT command and return the input fields
        return self.goto(url).input_fields if url else self.wait("body").input_fields

    def get_select_fields(self, url=None) -> List[WebBrowserSelectField]:
        """
        Get the select fields from the page.
        """
        if self._last_content and self._last_content.url == url:
            return self._last_content.select_fields

        # Run a WAIT command and return the select fields
        return self.goto(url).select_fields if url else self.wait("body").select_fields

    def get_textarea_fields(self, url=None) -> List[WebBrowserTextAreaField]:
        """
        Get the textarea fields from the page.
        """
        if self._last_content and self._last_content.url == url:
            return self._last_content.textarea_fields

        # Run a WAIT command and return the textarea fields
        return self.goto(url).textarea_fields if url else self.wait("body").textarea_fields

    def get_screenshot(self, url=None) -> str:
        """
        Get a screenshot of the page as a data URL.
        """
        screenshot = None
        if self._last_content and self._last_content.url == url:
            screenshot = self._last_content.screenshot

        if not screenshot:
            # Run a WAIT command and return the screenshot
            screenshot = self.goto(url).screenshot if url else self.wait("body").screenshot

        if screenshot:
            return f"data:image/png;base64,{base64.b64encode(screenshot).decode()}"

        return ""
