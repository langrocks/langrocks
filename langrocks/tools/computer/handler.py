import asyncio
import base64
import glob
import json
import logging
import mimetypes
import os
import random
import subprocess
import tempfile
from concurrent import futures
from typing import Iterator

from playwright.async_api import Page, async_playwright

from langrocks.client.code_runner import Content
from langrocks.common.models.files import FileMimeType
from langrocks.common.models.tools_pb2 import (
    COMPUTER_CURSOR_POSITION,
    COMPUTER_DOUBLE_CLICK,
    COMPUTER_KEY,
    COMPUTER_LEFT_CLICK,
    COMPUTER_LEFT_CLICK_DRAG,
    COMPUTER_MIDDLE_CLICK,
    COMPUTER_MOUSE_MOVE,
    COMPUTER_RIGHT_CLICK,
    COMPUTER_SCREENSHOT,
    COMPUTER_TERMINATE,
    COMPUTER_TYPE,
    COMPUTER_WAIT,
    BoundingBox,
    ComputerContent,
    ComputerRequest,
    ComputerResponse,
    ComputerSession,
    ComputerSessionConfig,
    ComputerState,
    Point,
    WebBrowserButton,
    WebBrowserCommandError,
    WebBrowserCommandOutput,
    WebBrowserDownload,
    WebBrowserImage,
    WebBrowserInputField,
    WebBrowserLink,
    WebBrowserSelectField,
    WebBrowserTextAreaField,
)

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36 Edg/100.0.1150.46",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12.0; rv:99.0) Gecko/20100101 Firefox/99.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36 Edg/100.0.1150.36",
]

# Script to disable webdriver flag
BROWSER_INIT_SCRIPT = """
Object.defineProperty(Object.getPrototypeOf(navigator), 'webdriver', {
    set: undefined,
    enumerable: true,
    configurable: true,
    get: new Proxy(
        Object.getOwnPropertyDescriptor(Object.getPrototypeOf(navigator), 'webdriver').get,
        { apply: (target, thisArg, args) => {
            // emulate getter call validation
            Reflect.apply(target, thisArg, args);
            return false;
        }}
    )
});
"""

logger = logging.getLogger(__name__)


def capture_screeshot():
    screenshot_data = None
    # Use gnome-screenshot to capture screen to temp file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
        temp_path = temp.name

    process = subprocess.run(["gnome-screenshot", "-f", temp_path], capture_output=True, text=True)

    if process.returncode == 0:
        # Read the temp file and encode as base64
        with open(temp_path, "rb") as f:
            screenshot_data = f.read()
        # Clean up temp file
        os.remove(temp_path)
    return screenshot_data


async def get_browser_content_from_page(
    page: Page, utils_js: str, session_config: ComputerSessionConfig
) -> ComputerContent:
    """
    Get browser content from a page
    """
    content = ComputerContent()

    try:
        content.url = page.url
        content.title = await page.title()

        # Load utils script
        await page.evaluate(utils_js)

        # Script to collect details of all elements and add bounding boxes
        # and labels
        tags_to_extract = session_config.tags_to_extract or []
        tags_to_extract_string = "[" + ",".join([f'"{tag}"' for tag in tags_to_extract]) + "]"
        add_tags_script_string = (
            f'window["addTags"]({tags_to_extract_string}, {"true" if session_config.annotate else "false"});'
        )
        page_details = await page.evaluate(add_tags_script_string)

        if session_config.text:
            content.text = page_details["text"]

        if session_config.html:
            content.html = await page.content()

        # Process the returned data
        if "button" in tags_to_extract:
            for button in page_details["buttons"]:
                content.buttons.append(
                    WebBrowserButton(
                        text=button["text"],
                        selector=button["tag"],
                        midpoint=Point(x=button["midpoint"]["x"], y=button["midpoint"]["y"]),
                        box=BoundingBox(
                            top=button["boundingBox"]["top"],
                            left=button["boundingBox"]["left"],
                            width=button["boundingBox"]["width"],
                            height=button["boundingBox"]["height"],
                        ),
                        inViewport=button["inViewport"],
                    ),
                )

        # Include interactable labels and divs as buttons if clickable
        if "label" in tags_to_extract:
            for label in page_details["labels"]:
                content.buttons.append(
                    WebBrowserButton(
                        text=label["text"],
                        selector=label["tag"],
                        midpoint=Point(x=label["midpoint"]["x"], y=label["midpoint"]["y"]),
                        box=BoundingBox(
                            top=label["boundingBox"]["top"],
                            left=label["boundingBox"]["left"],
                            width=label["boundingBox"]["width"],
                            height=label["boundingBox"]["height"],
                        ),
                        inViewport=label["inViewport"],
                    ),
                )

        if "div" in tags_to_extract:
            for div in page_details["divs"]:
                if div["clickable"]:
                    content.buttons.append(
                        WebBrowserButton(
                            text=div["text"],
                            selector=div["tag"],
                            midpoint=Point(x=div["midpoint"]["x"], y=div["midpoint"]["y"]),
                            box=BoundingBox(
                                top=div["boundingBox"]["top"],
                                left=div["boundingBox"]["left"],
                                width=div["boundingBox"]["width"],
                                height=div["boundingBox"]["height"],
                            ),
                            inViewport=div["inViewport"],
                        ),
                    )

        if "input" in tags_to_extract:
            for input in page_details["inputs"]:
                content.input_fields.append(
                    WebBrowserInputField(
                        text=input["text"],
                        selector=input["tag"],
                        midpoint=Point(x=input["midpoint"]["x"], y=input["midpoint"]["y"]),
                        box=BoundingBox(
                            top=input["boundingBox"]["top"],
                            left=input["boundingBox"]["left"],
                            width=input["boundingBox"]["width"],
                            height=input["boundingBox"]["height"],
                        ),
                        inViewport=input["inViewport"],
                    ),
                )

        if "select" in tags_to_extract:
            for select in page_details["selects"]:
                content.select_fields.append(
                    WebBrowserSelectField(
                        text=select["text"],
                        selector=select["tag"],
                        midpoint=Point(x=select["midpoint"]["x"], y=select["midpoint"]["y"]),
                        box=BoundingBox(
                            top=select["boundingBox"]["top"],
                            left=select["boundingBox"]["left"],
                            width=select["boundingBox"]["width"],
                            height=select["boundingBox"]["height"],
                        ),
                        inViewport=select["inViewport"],
                    ),
                )

        if "textarea" in tags_to_extract:
            for textarea in page_details["textareas"]:
                content.textarea_fields.append(
                    WebBrowserTextAreaField(
                        text=textarea["text"],
                        selector=textarea["tag"],
                        midpoint=Point(x=textarea["midpoint"]["x"], y=textarea["midpoint"]["y"]),
                        box=BoundingBox(
                            top=textarea["boundingBox"]["top"],
                            left=textarea["boundingBox"]["left"],
                            width=textarea["boundingBox"]["width"],
                            height=textarea["boundingBox"]["height"],
                        ),
                        inViewport=textarea["inViewport"],
                    ),
                )

        # Add typable divs as textareas
        if "div" in tags_to_extract:
            for div in page_details["divs"]:
                if div["editable"]:
                    content.textarea_fields.append(
                        WebBrowserTextAreaField(
                            text=div["text"],
                            selector=div["tag"],
                            midpoint=Point(x=div["midpoint"]["x"], y=div["midpoint"]["y"]),
                            box=BoundingBox(
                                top=div["boundingBox"]["top"],
                                left=div["boundingBox"]["left"],
                                width=div["boundingBox"]["width"],
                                height=div["boundingBox"]["height"],
                            ),
                            inViewport=div["inViewport"],
                        ),
                    )

        if "a" in tags_to_extract:
            for link in page_details["links"]:
                content.links.append(
                    WebBrowserLink(
                        text=link["text"],
                        selector=link["tag"],
                        url=link["url"],
                        midpoint=Point(x=link["midpoint"]["x"], y=link["midpoint"]["y"]),
                        box=BoundingBox(
                            top=link["boundingBox"]["top"],
                            left=link["boundingBox"]["left"],
                            width=link["boundingBox"]["width"],
                            height=link["boundingBox"]["height"],
                        ),
                        inViewport=link["inViewport"],
                    ),
                )

        if "img" in tags_to_extract:
            for image in page_details["images"]:
                content.images.append(
                    WebBrowserImage(
                        text=image["text"],
                        selector=image["tag"],
                        src=image["src"],
                        midpoint=Point(x=image["midpoint"]["x"], y=image["midpoint"]["y"]),
                        box=BoundingBox(
                            top=image["boundingBox"]["top"],
                            left=image["boundingBox"]["left"],
                            width=image["boundingBox"]["width"],
                            height=image["boundingBox"]["height"],
                        ),
                        inViewport=image["inViewport"],
                    ),
                )

        # Add a screenshot
        if session_config.capture_screenshot:
            content.screenshot = capture_screeshot()

        # Clear tags
        await page.evaluate('window["clearTags"]();')
    except Exception as e:
        logger.error(e)

    return content


async def process_pending_downloads(downloads_queue: asyncio.Queue, timeout=10.0):
    if downloads_queue and not downloads_queue.empty():
        web_browser_downloads = []

        try:
            while not downloads_queue.empty():
                download = downloads_queue.get_nowait()
                logger.info(f"Processing download {download.suggested_filename}")

                try:
                    # Wait for download with timeout
                    path = await asyncio.wait_for(download.path(), timeout=timeout)
                    with open(path, "rb") as f:
                        web_browser_downloads.append(
                            WebBrowserDownload(
                                url=download.url,
                                file=Content(
                                    mime_type=FileMimeType(
                                        mimetypes.guess_type(download.suggested_filename)[0]
                                    ).to_tools_mime_type(),
                                    data=f.read(),
                                    name=download.suggested_filename,
                                ),
                            )
                        )
                    os.remove(path)
                    downloads_queue.task_done()
                except asyncio.TimeoutError:
                    logger.error(f"Download timeout for {download.suggested_filename}")
                except Exception as e:
                    logger.error(f"Failed to process download: {e}")

        except Exception as e:
            logger.error(f"Error processing downloads queue: {e}")

        return web_browser_downloads
    return []


async def process_web_browser_request(
    page: Page,
    utils_js: str,
    session_config: ComputerSessionConfig,
    request: ComputerRequest,
):
    """
    Process a web browser request using Playwright and returns the final output
    """

    def _get_locator(page, selector):
        if (
            selector.startswith("a=")
            or selector.startswith("b=")
            or selector.startswith("in=")
            or selector.startswith(
                "s=",
            )
            or selector.startswith("ta=")
            or selector.startswith("l=")
            or selector.startswith("d=")
        ):
            name, value = selector.split("=")
            if name == "in":
                name = "input"
            elif name == "ta":
                name = "textarea"
            elif name == "s":
                name = "select"
            elif name == "b":
                name = "button"
            elif name == "l":
                name = "label"
            elif name == "d":
                name = "div"

            return page.locator(name).nth(int(value))
        return page.locator(selector)

    steps = list(request.commands)
    outputs = []
    errors = []
    logger.info(steps)
    terminated = False

    for index, step in zip(range(len(steps)), steps):
        try:

            if step.type == COMPUTER_TERMINATE:
                terminated = True
                break

            elif step.type in [COMPUTER_LEFT_CLICK, COMPUTER_RIGHT_CLICK, COMPUTER_MIDDLE_CLICK, COMPUTER_DOUBLE_CLICK]:
                button = {
                    COMPUTER_LEFT_CLICK: "left",
                    COMPUTER_RIGHT_CLICK: "right",
                    COMPUTER_MIDDLE_CLICK: "middle",
                    COMPUTER_DOUBLE_CLICK: "left",
                }[step.type]

                click_count = 2 if step.type == COMPUTER_DOUBLE_CLICK else 1
                xdotool_button = {
                    COMPUTER_LEFT_CLICK: "1",
                    COMPUTER_RIGHT_CLICK: "3",
                    COMPUTER_MIDDLE_CLICK: "2",
                    COMPUTER_DOUBLE_CLICK: "1",
                }[step.type]

                if step.selector:
                    locator = _get_locator(page, step.selector)
                    await locator.click(button=button, timeout=2000, click_count=click_count)
                else:
                    # Use xdotool to click
                    cmd = ["xdotool", "click", xdotool_button]
                    if step.type == COMPUTER_DOUBLE_CLICK:
                        cmd.append("2")  # Double click needs 2 count
                    process = subprocess.run(cmd, capture_output=True, text=True)
                    if process.returncode == 0:
                        outputs.append(WebBrowserCommandOutput(index=index, output=f"Successfully clicked"))
                    else:
                        errors.append(WebBrowserCommandError(index=index, error=process.stdout))
                        logger.error(f"Failed to click: {process.stdout}")
                await page.wait_for_timeout(500)  # Wait for click to complete
            elif step.type == COMPUTER_WAIT:
                timeout = min(
                    int(step.data) * 1000 if step.data else 5000,
                    10000,
                )
                if not step.selector:
                    await page.wait_for_timeout(timeout)
                else:
                    await page.wait_for_selector(step.selector, timeout=timeout)
            elif step.type == COMPUTER_TYPE:
                process = subprocess.run(["xdotool", "type", step.data], capture_output=True, text=True)
                logger.info(f"Typed output: {process}")
                if process.returncode == 0:
                    outputs.append(
                        WebBrowserCommandOutput(
                            index=index,
                            output=(f"Successfully typed: {step.data}"),
                        )
                    )
                else:
                    errors.append(WebBrowserCommandError(index=index, error=process.stdout))
            elif step.type == COMPUTER_KEY:
                # Run xdotool in a subprocess and return the output
                process = subprocess.run(
                    ["xdotool", "key", "--delay", "100", step.data], capture_output=True, text=True
                )
                logger.info(f"Keyed output: {process}")
                if process.returncode == 0:
                    outputs.append(
                        WebBrowserCommandOutput(
                            index=index,
                            output=(f"Successfully pressed key: {step.data}"),
                        )
                    )
                else:
                    errors.append(WebBrowserCommandError(index=index, error=process.stdout))
            elif step.type == COMPUTER_CURSOR_POSITION:
                # Run xdotool in a subprocess and return the output as a json string of the form {"x": 100, "y": 200}
                process = subprocess.run(["xdotool", "getmouselocation"], capture_output=True, text=True)
                x, y = process.stdout.split("x:")[1].split(" y:")[0], process.stdout.split("y:")[1].split(" screen:")[0]
                outputs.append(
                    WebBrowserCommandOutput(
                        index=index,
                        output=json.dumps({"x": int(x), "y": int(y)}),
                    )
                )
            elif step.type == COMPUTER_MOUSE_MOVE:
                # Step.data will be a json string with x and y coordinates. We need to parse it and move the mouse
                try:
                    data = json.loads(step.data)
                    process = subprocess.run(
                        ["xdotool", "mousemove", "--sync", str(data["x"]), str(data["y"])],
                        capture_output=True,
                        text=True,
                    )
                    if process.returncode == 0:
                        outputs.append(
                            WebBrowserCommandOutput(
                                index=index,
                                output=(f"Successfully moved mouse to x:{data['x']}, y:{data['y']}"),
                            )
                        )
                    else:
                        errors.append(WebBrowserCommandError(index=index, error=process.stdout))
                except Exception as e:
                    logger.error(f"Failed to parse mouse move data: {step.data}")
                    errors.append(WebBrowserCommandError(index=index, error=str(e)))
            elif step.type == COMPUTER_LEFT_CLICK_DRAG:
                # Step.data will be a json string with x and y coordinates. We need to parse it and move the mouse
                try:
                    data = json.loads(step.data)
                    process = subprocess.run(
                        [
                            "xdotool",
                            "mousedown",
                            "1",
                            "mousemove",
                            "--sync",
                            str(data["x"]),
                            str(data["y"]),
                            "mouseup",
                            "1",
                        ],
                        capture_output=True,
                        text=True,
                    )
                    if process.returncode == 0:
                        outputs.append(
                            WebBrowserCommandOutput(
                                index=index,
                                output=(f"Successfully left click dragged to x:{data['x']}, y:{data['y']}"),
                            )
                        )
                    else:
                        errors.append(WebBrowserCommandError(index=index, error=process.stdout))
                except Exception as e:
                    logger.error(f"Failed to parse left click drag data: {step.data}")
                    errors.append(WebBrowserCommandError(index=index, error=str(e)))
            elif step.type == COMPUTER_SCREENSHOT:
                # Use gnome-screenshot to capture screen to temp file
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
                    temp_path = temp.name

                process = subprocess.run(["gnome-screenshot", "-f", temp_path], capture_output=True, text=True)

                if process.returncode == 0:
                    # Read the temp file and encode as base64
                    with open(temp_path, "rb") as f:
                        screenshot_data = f.read()
                    outputs.append(
                        WebBrowserCommandOutput(
                            index=index,
                            output=base64.b64encode(screenshot_data).decode(),
                        )
                    )
                    # Clean up temp file
                    os.remove(temp_path)
                else:
                    errors.append(WebBrowserCommandError(index=index, error=process.stderr))
        except Exception as e:
            logger.exception(e)
            errors.append(WebBrowserCommandError(index=index, error=str(e)))
        finally:
            pass

    # If there was only TERMINATE command, then skip getting the content
    if not steps or (len(steps) == 1 and steps[0].type == COMPUTER_TERMINATE):
        return ComputerContent(), terminated

    content = ComputerContent()
    if session_config.capture_screenshot:
        content.screenshot = capture_screeshot()
    for error in errors:
        content.command_errors.append(error)

    for text_output in outputs:
        content.command_outputs.append(text_output)

    return content, terminated


async def save_storage_state(context):
    try:
        # Get cookies directly from context
        cookies = await context.cookies()

        # Create storage state with just cookies
        storage_state = {"cookies": cookies, "origins": []}

        return storage_state

    except Exception as e:
        logger.warning(f"Failed to save storage state: {str(e)}")
        return {"cookies": [], "origins": []}


class ComputerHandler:

    def __init__(self, display_pool, wss_secure, wss_hostname, wss_port, ublock_path, allow_downloads):
        self.display_pool = display_pool
        self.wss_secure = wss_secure
        self.wss_hostname = wss_hostname
        self.wss_port = wss_port
        self.ublock_path = ublock_path
        self.allow_downloads = allow_downloads
        self.utils_js = ""
        # Load utils script
        with open(os.path.join(os.path.dirname(__file__), "utils.js")) as f:
            self.utils_js = f.read()

    async def _process_web_browser_input_stream(
        self,
        initial_request: ComputerRequest,
        request_iterator: Iterator[ComputerRequest],
        display,
        record_video_dir: str,
    ):
        os.environ["DISPLAY"] = f'{display["DISPLAY"]}.0'
        logger.info(f"Using {os.environ['DISPLAY']}")
        session_config = initial_request.session_config
        session_data = session_config.session_data
        downloads_queue = asyncio.Queue() if self.allow_downloads else None

        async with async_playwright() as playwright:
            try:
                session_data = (
                    json.loads(
                        session_data,
                    )
                    if session_data
                    else None
                )

                url = session_config.init_url or "chrome://newtab"
                if not url.startswith("http") and not url.startswith("chrome://"):
                    url = f"https://{url}"

                # Configure browser launch options with uBlock if available
                browser_args = [
                    "--disable-blink-features=AutomationControlled",
                    "--no-default-browser-check",
                    "--no-first-run",
                    "--disable-features=IsolateOrigins,site-per-process",
                ]
                if self.ublock_path:
                    logger.info(f"Enabling uBlock Origin from {self.ublock_path}")
                    context = await playwright.chromium.launch_persistent_context(
                        headless=False,
                        chromium_sandbox=False,
                        user_data_dir="",
                        args=browser_args
                        + [
                            f"--disable-extensions-except={self.ublock_path}",
                            f"--load-extension={self.ublock_path}",
                        ],
                        user_agent=USER_AGENTS[random.randint(0, len(USER_AGENTS) - 1)],
                        no_viewport=True,
                        ignore_default_args=["--enable-automation"],
                        accept_downloads=self.allow_downloads,
                        record_video_dir=record_video_dir,
                        base_url=url,
                    )
                else:
                    context = await playwright.chromium.launch_persistent_context(
                        headless=False,
                        chromium_sandbox=False,
                        user_data_dir="",
                        args=browser_args,
                        user_agent=USER_AGENTS[random.randint(0, len(USER_AGENTS) - 1)],
                        no_viewport=True,
                        ignore_default_args=["--enable-automation"],
                        accept_downloads=self.allow_downloads,
                        record_video_dir=record_video_dir,
                        base_url=url,
                    )

                if session_data:
                    await context.add_cookies(session_data["cookies"])

                await context.add_init_script(BROWSER_INIT_SCRIPT)
                page = context.pages[0] if context.pages else await context.new_page()

                # If downloads are allowed, then set the download handler
                if self.allow_downloads and downloads_queue:
                    page.on("download", lambda download: downloads_queue.put(download))

                content, terminated = await process_web_browser_request(
                    page, self.utils_js, session_config, initial_request
                )
                content.downloads.extend(await process_pending_downloads(downloads_queue, timeout=30.0))

                if terminated and session_config.persist_session:
                    session_data = await save_storage_state(context)
                    await context.close()
                    yield (content, terminated, session_data)
                else:
                    if terminated:
                        await context.close()
                    yield content, terminated, None

                for next_request in request_iterator:
                    content, terminated = await process_web_browser_request(
                        page, self.utils_js, session_config, next_request
                    )
                    content.downloads.extend(await process_pending_downloads(downloads_queue, timeout=30.0))

                    if terminated and session_config.persist_session:
                        session_data = await save_storage_state(context)
                        await context.close()
                        yield (content, terminated, session_data)
                    else:
                        if terminated:
                            await context.close()
                        yield content, terminated, None

                    await asyncio.sleep(0.1)

            except Exception as e:
                logger.exception(e)
            finally:
                # Clean up
                await context.close()

    def get_computer(self, request_iterator: Iterator[ComputerRequest]) -> Iterator[ComputerResponse]:
        # Get the first request from the client
        initial_request = next(request_iterator)
        session_config = initial_request.session_config

        if not session_config:
            logger.error("No session config provided")
            yield ComputerResponse(state=ComputerState.COMPUTER_TERMINATED)
            return

        display = self.display_pool.get_display(remote_control=session_config.interactive)
        SENTINAL = object()

        if not display:
            logger.error("No display available")
            yield ComputerResponse(state=ComputerState.COMPUTER_TERMINATED)
            return

        # Return the display info to the client
        if session_config.interactive:
            wss_server_path = (
                f"{self.wss_hostname}:{self.wss_port}" if "/" not in self.wss_hostname else self.wss_hostname
            )
            yield ComputerResponse(
                session=ComputerSession(
                    ws_url=(
                        f"{'wss' if self.wss_secure else 'ws'}://{display['username']}:{display['password']}@{wss_server_path}?token={display['token']}"
                        if "username" in display
                        else None
                    ),
                ),
                state=ComputerState.COMPUTER_RUNNING,
            )
        else:
            yield ComputerResponse(state=ComputerState.COMPUTER_RUNNING)

        # Create a temporary directory for video recording
        record_video_dir = tempfile.mkdtemp() if session_config.record_video else None

        # Use ThreadPoolExecutor to run the async function in a separate thread
        with futures.ThreadPoolExecutor(thread_name_prefix="async_tasks") as executor:
            browser_done = False

            # Wrap the coroutine in a function that gets the current event loop
            # or creates a new one and runs the coroutine in it
            def run_async_code(loop, fn):
                asyncio.set_event_loop(loop)

                return loop.run_until_complete(fn())

            # Create a queue to store the browser content
            content_queue = asyncio.Queue()

            async def collect_browser_output():
                async for content, terminated, session_data in self._process_web_browser_input_stream(
                    initial_request=initial_request,
                    request_iterator=request_iterator,
                    display=display,
                    record_video_dir=record_video_dir,
                ):
                    await content_queue.put((content, terminated, session_data))

                    if terminated:
                        break
                await content_queue.put(SENTINAL)

            # Submit the function to the executor and get a Future object
            content_future = executor.submit(
                run_async_code,
                asyncio.new_event_loop(),
                collect_browser_output,
            )

            # Wait for the future to complete and get the return value
            try:
                while not browser_done:
                    try:
                        element = content_queue.get_nowait()
                        if element is SENTINAL:
                            browser_done = True

                            # If video recording is enabled, then look for the video files and return it
                            if record_video_dir:
                                video_files = glob.glob(os.path.join(record_video_dir, "*.webm"))
                                if video_files:
                                    videos = []
                                    for video_file in video_files:
                                        with open(video_file, "rb") as f:
                                            file_name = os.path.basename(video_file)
                                            mime_type = mimetypes.guess_type(video_file)[0]
                                            videos.append(
                                                Content(
                                                    data=f.read(),
                                                    name=file_name,
                                                    mime_type=FileMimeType(mime_type).to_tools_mime_type(),
                                                )
                                            )
                                        os.remove(video_file)

                                    yield ComputerResponse(
                                        session=ComputerSession(videos=videos),
                                        state=ComputerState.COMPUTER_TERMINATED,
                                    )
                            break

                        content, terminated, session_data = element

                        response = ComputerResponse(
                            state=(
                                ComputerState.COMPUTER_RUNNING if not terminated else ComputerState.COMPUTER_TERMINATED
                            ),
                        )
                        response.content.CopyFrom(content)
                        if session_data:
                            response.session.CopyFrom(ComputerSession(session_data=json.dumps(session_data)))

                        yield response
                    except asyncio.QueueEmpty:
                        pass

                    if browser_done:
                        break

            except Exception as e:
                logger.error(e)
                yield ComputerResponse(
                    state=ComputerState.COMPUTER_TERMINATED,
                )
            finally:
                self.display_pool.put_display(display)
