import asyncio
import json
import logging
import os
import random
from concurrent import futures
from typing import Iterator

from playwright.async_api import Page, async_playwright

from langrocks.common.models.tools_pb2 import (
    CLICK,
    COPY,
    ENTER,
    GOTO,
    SCROLL_X,
    SCROLL_Y,
    TERMINATE,
    TYPE,
    WAIT,
    WebBrowserButton,
    WebBrowserCommandError,
    WebBrowserCommandOutput,
    WebBrowserInputField,
    WebBrowserLink,
    WebBrowserOutput,
    WebBrowserRequest,
    WebBrowserResponse,
    WebBrowserSelectField,
    WebBrowserSession,
    WebBrowserSessionConfig,
    WebBrowserState,
    WebBrowserTextAreaField,
)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36 Edg/99.0.1150.46",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12.0; rv:99.0) Gecko/20100101 Firefox/99.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36 Edg/99.0.1150.36",
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


async def get_browser_output_from_page(page: Page, utils_js: str, skip_tags: bool = False) -> WebBrowserOutput:
    """
    Get browser output from a page
    """
    output = WebBrowserOutput()

    try:
        output.url = page.url
        output.title = await page.title()

        if skip_tags:
            output.text = await page.evaluate("document.body.innerText")
            output.screenshot = await page.screenshot(type="png")
            return output

        # Load utils script
        await page.evaluate(utils_js)

        # Script to collect details of all elements and add bounding boxes
        # and labels
        page_details = await page.evaluate("addTags();")
        output.text = page_details["text"]

        # Process the returned data
        for button in page_details["buttons"]:
            output.buttons.append(
                WebBrowserButton(
                    text=button["text"],
                    selector=button["tag"],
                ),
            )

        # Include interactable labels and divs as buttons if clickable
        for label in page_details["labels"]:
            output.buttons.append(
                WebBrowserButton(
                    text=label["text"],
                    selector=label["tag"],
                ),
            )

        for div in page_details["divs"]:
            if div["clickable"]:
                output.buttons.append(
                    WebBrowserButton(
                        text=div["text"],
                        selector=div["tag"],
                    ),
                )

        for input in page_details["inputs"]:
            output.inputs.append(
                WebBrowserInputField(
                    text=input["text"],
                    selector=input["tag"],
                ),
            )

        for select in page_details["selects"]:
            output.selects.append(
                WebBrowserSelectField(
                    text=select["text"],
                    selector=select["tag"],
                ),
            )

        for textarea in page_details["textareas"]:
            output.textareas.append(
                WebBrowserTextAreaField(
                    text=textarea["text"],
                    selector=textarea["tag"],
                ),
            )

        # Add typable divs as textareas
        for div in page_details["divs"]:
            if div["editable"]:
                output.textareas.append(
                    WebBrowserTextAreaField(
                        text=div["text"],
                        selector=div["tag"],
                    ),
                )

        for link in page_details["links"]:
            output.links.append(
                WebBrowserLink(
                    text=link["text"],
                    selector=link["tag"],
                    url=link["url"],
                ),
            )

        # Add a screenshot
        output.screenshot = await page.screenshot(type="png")

        # Clear tags
        await page.evaluate("clearTags();")
    except Exception as e:
        logger.error(e)
        output.error = str(e)

    return output


async def process_web_browser_request(
    page: Page, utils_js: str, session_config: WebBrowserSessionConfig, request: WebBrowserRequest
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

    steps = list(request.inputs)
    outputs = []
    errors = []
    logger.info(steps)
    terminated = False

    for index, step in zip(range(len(steps)), steps):
        try:
            if step.type == TERMINATE:
                terminated = True
                break
            elif step.type == GOTO:
                await page.goto(
                    (page.url + step.data if step.data and step.data.startswith("/") else step.data) or page.url,
                )
            elif step.type == CLICK:
                locator = _get_locator(page, step.selector)
                await locator.click(timeout=2000)
                await page.wait_for_timeout(200)  # Wait
            elif step.type == WAIT:
                timeout = min(
                    int(step.data) * 1000 if step.data else 5000,
                    10000,
                )
                if not step.selector:
                    await page.wait_for_timeout(timeout)
                else:
                    await page.wait_for_selector(step.selector, timeout=timeout)
            elif step.type == COPY:
                results = await page.query_selector_all(step.selector or "body")
                outputs.append(
                    WebBrowserCommandOutput(
                        index=index,
                        output="".join([await result.inner_text() for result in results]),
                    )
                )
            elif step.type == TYPE:
                locator = _get_locator(page, step.selector)
                # Clear before typing
                await locator.fill("", timeout=1000)
                await locator.press_sequentially(step.data, timeout=1000)
            elif step.type == SCROLL_X:
                await page.mouse.wheel(delta_x=int(step.data), delta_y=0)
            elif step.type == SCROLL_Y:
                await page.mouse.wheel(delta_x=0, delta_y=int(step.data))
            elif step.type == ENTER:
                if await page.evaluate(
                    '() => { return (document.activeElement.tagName === "INPUT" || document.activeElement.tagName === "TEXTAREA"); }',
                ):
                    await page.keyboard.press("Enter")
                    # Wait for navigation to complete if any
                    await page.wait_for_timeout(5000)
        except Exception as e:
            logger.exception(e)
            errors.append(WebBrowserCommandError(index=index, error=str(e)))
        finally:
            pass

    output = await get_browser_output_from_page(page, utils_js, session_config.skip_tags)
    for error in errors:
        output.errors.append(error)

    for text_output in outputs:
        output.outputs.append(text_output)

    return output, terminated


class WebBrowserHandler:
    def __init__(self, display_pool, wss_secure, wss_hostname, wss_port):
        self.display_pool = display_pool
        self.wss_secure = wss_secure
        self.wss_hostname = wss_hostname
        self.wss_port = wss_port

        # Load utils script
        with open(os.path.join(os.path.dirname(__file__), "utils.js")) as f:
            self.utils_js = f.read()

    async def _process_web_browser_input_stream(
        self,
        initial_request: WebBrowserRequest,
        request_iterator: Iterator[WebBrowserRequest],
        display,
    ):
        os.environ["DISPLAY"] = f'{display["DISPLAY"]}.0'
        logger.info(f"Using {os.environ['DISPLAY']}")
        session_config = initial_request.session_config
        session_data = session_config.session_data

        async with async_playwright() as playwright:
            try:
                session_data = (
                    json.loads(
                        session_data,
                    )
                    if session_data
                    else None
                )
                browser = await playwright.chromium.launch(
                    headless=False, args=["--disable-blink-features=AutomationControlled"]
                )
                context = await browser.new_context(
                    no_viewport=True,
                    storage_state=session_data,
                    user_agent=USER_AGENTS[random.randint(0, len(USER_AGENTS) - 1)],
                )
                await context.add_init_script(BROWSER_INIT_SCRIPT)
                page = await context.new_page()

                url = session_config.init_url or "chrome://newtab"
                if not url.startswith("http"):
                    url = f"https://{url}"

                # Load the start_url before processing the steps
                await page.goto(url, wait_until="domcontentloaded")

                output, terminated = await process_web_browser_request(
                    page, self.utils_js, session_config, initial_request
                )

                if terminated and session_config.persist_session:
                    session_data = await context.storage_state()
                    yield (output, terminated, session_data)
                else:
                    yield output, terminated, None

                for next_request in request_iterator:
                    output, terminated = await process_web_browser_request(
                        page, self.utils_js, session_config, next_request
                    )
                    if session_config.persist_session:
                        session_data = await context.storage_state()
                        yield (output, terminated, session_data)
                    else:
                        yield output, terminated, None

                    await asyncio.sleep(0.1)

            except Exception as e:
                logger.exception(e)
            finally:
                # Clean up
                await browser.close()

    def get_web_browser(
        self,
        request_iterator: Iterator[WebBrowserRequest],
    ) -> Iterator[WebBrowserResponse]:
        # Get the first request from the client
        initial_request = next(request_iterator)
        session_config = initial_request.session_config

        logger.info(f"Received initial request: {initial_request}")

        if not session_config:
            logger.error("No session config provided")
            yield WebBrowserResponse(state=WebBrowserState.TERMINATED)
            return

        display = self.display_pool.get_display(remote_control=session_config.interactive)
        SENTINAL = object()

        if not display:
            logger.error("No display available")
            yield WebBrowserResponse(state=WebBrowserState.TERMINATED)
            return

        # Return the display info to the client
        if session_config.interactive:
            wss_server_path = (
                f"{self.wss_hostname}:{self.wss_port}" if "/" not in self.wss_hostname else self.wss_hostname
            )
            yield WebBrowserResponse(
                session=WebBrowserSession(
                    ws_url=(
                        f"{'wss' if self.wss_secure else 'ws'}://{display['username']}:{display['password']}@{wss_server_path}?token={display['token']}"
                        if "username" in display
                        else None
                    ),
                ),
                state=WebBrowserState.RUNNING,
            )

        # Use ThreadPoolExecutor to run the async function in a separate thread
        with futures.ThreadPoolExecutor(thread_name_prefix="async_tasks") as executor:
            browser_done = False

            # Wrap the coroutine in a function that gets the current event loop
            # or creates a new one and runs the coroutine in it
            def run_async_code(loop, fn):
                asyncio.set_event_loop(loop)

                return loop.run_until_complete(fn())

            # Create a queue to store the browser output
            output_queue = asyncio.Queue()

            async def collect_browser_output():
                async for output, terminated, session_data in self._process_web_browser_input_stream(
                    initial_request=initial_request,
                    request_iterator=request_iterator,
                    display=display,
                ):
                    await output_queue.put((output, terminated, session_data))

                    if terminated:
                        break
                await output_queue.put(SENTINAL)

            # Submit the function to the executor and get a Future object
            content_future = executor.submit(
                run_async_code,
                asyncio.new_event_loop(),
                collect_browser_output,
            )

            # Wait for the future to complete and get the return value
            try:
                yield WebBrowserResponse(state=WebBrowserState.RUNNING)

                while not browser_done:
                    try:
                        element = output_queue.get_nowait()
                        if element is SENTINAL:
                            browser_done = True
                            break

                        output, terminated, session_data = element

                        logger.info(f"Sending output: {terminated}, {session_data}")

                        response = WebBrowserResponse(
                            state=WebBrowserState.RUNNING if not terminated else WebBrowserState.TERMINATED,
                        )
                        response.output.CopyFrom(output)
                        if session_data:
                            response.session.CopyFrom(WebBrowserSession(session_data=json.dumps(session_data)))

                        yield response
                    except asyncio.QueueEmpty:
                        pass

                    if content_future.done() or browser_done:
                        break

            except Exception as e:
                logger.error(e)
                yield WebBrowserResponse(
                    state=WebBrowserState.TERMINATED,
                )
            finally:
                self.display_pool.put_display(display)
