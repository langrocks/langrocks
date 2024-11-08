from langrocks.client.web_browser import WebBrowser, WebBrowserContextManager
from langrocks.common.models.web_browser import WebBrowserCommand, WebBrowserCommandType

# Test the web browser
with WebBrowser(
    "localhost:50051", capture_screenshot=True, html=True, persist_session=True, tags_to_extract=["img"]
) as web_browser:
    print("\nRunning web browser")

    print("Browser state", web_browser.get_state())

    ws_url = web_browser.get_wss_url()
    print("WSS_URL", ws_url)

    # Run commands
    print("Running commands")
    content = web_browser.run_commands(
        commands=[
            WebBrowserCommand(
                command_type=WebBrowserCommandType.GOTO,
                data="https://www.google.com",
            ),
        ]
    )
    print("Output from running commands", content.model_dump_json()[:100])

    # Run command
    print("Running command")
    content = web_browser.run_command(
        command=WebBrowserCommand(
            command_type=WebBrowserCommandType.WAIT,
            selector="body",
        )
    )
    print("Output from running command", content.model_dump_json()[:100])

    # Get text from session
    print("Getting text from session")
    print("Text", web_browser.get_text()[:100])

    # Get HTML from session
    print("Getting HTML from session")
    print("HTML", web_browser.get_html()[:100])

    # Get images from session
    print("Getting images from session")
    print("Images", web_browser.get_images()[:3])

    # Get links from session
    print("Getting links from session")
    print("Links", web_browser.get_links()[:3])

    # Get buttons from session
    print("Getting buttons from session")
    print("Buttons", web_browser.get_buttons())

    # Get input fields from session
    print("Getting input fields from session")
    print("Input fields", web_browser.get_input_fields())

    # Get select fields from session
    print("Getting select fields from session")
    print("Select fields", web_browser.get_select_fields())

    # Get textarea fields from session
    print("Getting textarea fields from session")
    print("Textarea fields", web_browser.get_textarea_fields())

    # Get screenshot
    print("Getting screenshot")
    print("Screenshot", web_browser.get_screenshot()[:100])

    # Get a different webpage
    print("Opening a different webpage")
    print("Browser state", web_browser.get_text("https://www.github.com"))

    print("Terminating web browser")
    session = web_browser.terminate()
    print("Session data", session[:100])

# Test the interactive web browser
with WebBrowserContextManager("localhost:50051") as web_browser:
    print("\nRunning interactive web browser")
    session, response_iter = web_browser.run_commands_interactive(
        commands=[
            WebBrowserCommand(
                command_type=WebBrowserCommandType.GOTO,
                data="https://www.google.com",
            ),
            WebBrowserCommand(
                command_type=WebBrowserCommandType.WAIT,
                selector="body",
            ),
        ]
    )
    print(session, response_iter)

    for resp in response_iter:
        print(resp)


# Test the web browser
with WebBrowserContextManager("localhost:50051") as web_browser:
    print("\nRunning web browser")
    content = web_browser.run_commands(
        commands=[
            WebBrowserCommand(
                command_type=WebBrowserCommandType.GOTO,
                data="https://www.google.com",
            ),
            WebBrowserCommand(
                command_type=WebBrowserCommandType.WAIT,
                selector="body",
            ),
        ]
    )
    print(content)

# Get HTML from a URL
with WebBrowserContextManager("localhost:50051") as web_browser:
    print("\nGetting HTML from a URL")
    html = web_browser.get_html_from_page("https://www.google.com")
    print(html)


# Get text from a URL
with WebBrowserContextManager("localhost:50051") as web_browser:
    print("\nGetting text from a URL")
    text = web_browser.get_text_from_page("https://www.google.com")
    print(text)


# Get images from a page
with WebBrowserContextManager("localhost:50051") as web_browser:
    print("\nGetting images from a page")
    images = web_browser.get_images_from_page("https://www.google.com")
    print(images)

# Get links from a page
with WebBrowserContextManager("localhost:50051") as web_browser:
    print("\nGetting links from a page")
    links = web_browser.get_links_from_page("https://www.google.com")
    print(links)

# Get buttons from a page
with WebBrowserContextManager("localhost:50051") as web_browser:
    print("\nGetting buttons from a page")
    buttons = web_browser.get_buttons_from_page("https://www.google.com")
    print(buttons)

# Get input fields from a page
with WebBrowserContextManager("localhost:50051") as web_browser:
    print("\nGetting input fields from a page")
    input_fields = web_browser.get_input_fields_from_page("https://www.google.com")
    print(input_fields)

# Get select fields from a page
with WebBrowserContextManager("localhost:50051") as web_browser:
    print("\nGetting select fields from a page")
    select_fields = web_browser.get_select_fields_from_page("https://www.google.com")
    print(select_fields)

# Get textarea fields from a page
with WebBrowserContextManager("localhost:50051") as web_browser:
    print("\nGetting textarea fields from a page")
    textarea_fields = web_browser.get_textarea_fields_from_page("https://www.google.com")
    print(textarea_fields)

# Test xdotool based commands
with WebBrowser(
    "localhost:50051",
    capture_screenshot=True,
    html=True,
    persist_session=True,
    tags_to_extract=["input", "textarea", "img"],
) as web_browser:
    print("\nTesting xdotool based commands")

    # Navigate to test page
    web_browser.run_command(
        command=WebBrowserCommand(
            command_type=WebBrowserCommandType.GOTO,
            data="https://www.google.com",
        )
    )

    # Test cursor position
    content = web_browser.run_command(
        command=WebBrowserCommand(
            command_type=WebBrowserCommandType.CURSOR_POSITION,
        )
    )
    print("Current cursor position:", content.command_outputs[0].output)

    # Test mouse move
    content = web_browser.run_command(
        command=WebBrowserCommand(command_type=WebBrowserCommandType.MOUSE_MOVE, data='{"x": 100, "y": 200}')
    )
    print("Mouse move result:", content.command_outputs[0].output)

    # Test key press
    content = web_browser.run_command(
        command=WebBrowserCommand(command_type=WebBrowserCommandType.KEY, data="Tab")  # Example key press
    )
    print("Key press result:", content.command_outputs[0].output)

    # Test typing into specific input field
    content = web_browser.run_command(
        command=WebBrowserCommand(
            command_type=WebBrowserCommandType.TYPE,
            selector="input[name='q']",  # Google search input
            data="Hello World",
        )
    )
    print("Typed into search field")

    # Test global typing without selector
    content = web_browser.run_command(
        command=WebBrowserCommand(command_type=WebBrowserCommandType.TYPE, data="Global typing")
    )
    print("Global typing result:", content.command_outputs[0].output if content.command_outputs else "No output")

    # Test typing with ENTER
    content = web_browser.run_commands(
        [
            WebBrowserCommand(command_type=WebBrowserCommandType.TYPE, selector="input[name='q']", data="Search query"),
            WebBrowserCommand(command_type=WebBrowserCommandType.ENTER),
        ]
    )
    print("Typed and pressed enter")

    # Test screenshot
    content = web_browser.run_command(
        command=WebBrowserCommand(
            command_type=WebBrowserCommandType.SCREENSHOT,
        )
    )
    print("Screenshot captured, length:", len(content.command_outputs[0].output))

# Test downloads
with WebBrowser(
    "localhost:50051",
    capture_screenshot=True,
    html=True,
    persist_session=True,
    tags_to_extract=["a", "button"],  # Make sure we can find download links
) as web_browser:
    print("\nTesting downloads")

    content = web_browser.run_commands(
        commands=[
            WebBrowserCommand(
                command_type=WebBrowserCommandType.GOTO,
                data="https://pypi.org/project/langrocks/#files",
            ),
            # Wait for the page to load
            WebBrowserCommand(
                command_type=WebBrowserCommandType.WAIT,
                selector=".file",
            ),
        ]
    )

    # Click on a download link (.tar.gz package as an example)
    content = web_browser.run_commands(
        commands=[
            WebBrowserCommand(
                command_type=WebBrowserCommandType.CLICK,
                selector="a[href$='.tar.gz']",  # Click first link ending with .tar.gz
            ),
            # Wait a bit for the download to start and complete
            WebBrowserCommand(
                command_type=WebBrowserCommandType.WAIT,
                data="5",  # Wait 5 seconds
            ),
        ]
    )

    if content.downloads:
        print(f"\nCaptured additional {len(content.downloads)} downloads:")
        for download in content.downloads:
            print(f"- Download URL: {download.url}")
            print(f"  File name: {download.file.name}")
            print(f"  File type: {download.file.mime_type}")
            print(f"  File size: {len(download.file.data)} bytes")

    else:
        print("No additional downloads were captured")


# Test video recording
with WebBrowser(
    "localhost:50051", capture_screenshot=True, html=True, persist_session=True, record_video=True
) as web_browser:
    print("\nTesting video recording")

    content = web_browser.run_commands(
        commands=[
            WebBrowserCommand(command_type=WebBrowserCommandType.GOTO, data="https://www.google.com"),
            WebBrowserCommand(command_type=WebBrowserCommandType.TERMINATE),
        ]
    )

    # Get the video
    videos = web_browser.get_videos()
    print(f"Received {len(videos)} videos")
