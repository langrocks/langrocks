import logging
from typing import Iterator, List, Optional

import grpc

from langrocks.common.models import tools_pb2
from langrocks.common.models.tools_pb2_grpc import ToolsStub
from langrocks.common.models.web_browser import (
    WebBrowserButton,
    WebBrowserCommand,
    WebBrowserCommandError,
    WebBrowserCommandOutput,
    WebBrowserCommandType,
    WebBrowserContent,
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
    )


def convert_proto_to_web_browser_session(
    session: tools_pb2.WebBrowserSession,
) -> Optional[WebBrowserSession]:
    if session is None:
        return None
    return WebBrowserSession(
        ws_url=session.ws_url,
        session_data=session.session_data,
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
