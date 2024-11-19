from langrocks.client.computer import Computer, ComputerContextManager
from langrocks.common.models.computer import ComputerCommand, ComputerCommandType

# Test the web browser
with Computer(
    "localhost:50051", capture_screenshot=True, html=True, persist_session=True, tags_to_extract=["img"]
) as computer:
    print("\nRunning web browser")

    print("Browser state", computer.get_state())

    ws_url = computer.get_wss_url()
    print("WSS_URL", ws_url)

    # Run commands
    print("Running commands")
    content = computer.run_commands(
        commands=[
            ComputerCommand(
                command_type=ComputerCommandType.GOTO,
                data="https://www.google.com",
            ),
        ]
    )
    print("Output from running commands", content.model_dump_json()[:100])

    # Run command
    print("Running command")
    content = computer.run_command(
        command=ComputerCommand(
            command_type=ComputerCommandType.WAIT,
            selector="body",
        )
    )
    print("Output from running command", content.model_dump_json()[:100])

    # Get text from session
    print("Getting text from session")
    print("Text", computer.get_text()[:100])

    # Get HTML from session
    print("Getting HTML from session")
    print("HTML", computer.get_html()[:100])

    # Get images from session
    print("Getting images from session")
    print("Images", computer.get_images()[:3])

    # Get links from session
    print("Getting links from session")
    print("Links", computer.get_links()[:3])

    # Get buttons from session
    print("Getting buttons from session")
    print("Buttons", computer.get_buttons())

    # Get input fields from session
    print("Getting input fields from session")
    print("Input fields", computer.get_input_fields())

    # Get select fields from session
    print("Getting select fields from session")
    print("Select fields", computer.get_select_fields())

    # Get textarea fields from session
    print("Getting textarea fields from session")
    print("Textarea fields", computer.get_textarea_fields())

    # Get screenshot
    print("Getting screenshot")
    print("Screenshot", computer.get_screenshot()[:100])

    # Get a different webpage
    print("Opening a different webpage")
    print("Browser state", computer.get_text("https://www.github.com"))

    print("Terminating web browser")
    session = computer.terminate()
    print("Session data", session[:100])

# Test the interactive web browser
with ComputerContextManager("localhost:50051") as computer:
    print("\nRunning interactive web browser")
    session, response_iter = computer.run_commands_interactive(
        commands=[
            ComputerCommand(
                command_type=ComputerCommandType.GOTO,
                data="https://www.google.com",
            ),
            ComputerCommand(
                command_type=ComputerCommandType.WAIT,
                selector="body",
            ),
        ]
    )
    print(session, response_iter)

    for resp in response_iter:
        print(resp)


# Test the web browser
with ComputerContextManager("localhost:50051") as computer:
    print("\nRunning web browser")
    content = computer.run_commands(
        commands=[
            ComputerCommand(
                command_type=ComputerCommandType.GOTO,
                data="https://www.google.com",
            ),
            ComputerCommand(
                command_type=ComputerCommandType.WAIT,
                selector="body",
            ),
        ]
    )
    print(content)

# Get HTML from a URL
with ComputerContextManager("localhost:50051") as computer:
    print("\nGetting HTML from a URL")
    html = computer.get_html_from_page("https://www.google.com")
    print(html)


# Get text from a URL
with ComputerContextManager("localhost:50051") as computer:
    print("\nGetting text from a URL")
    text = computer.get_text_from_page("https://www.google.com")
    print(text)


# Get images from a page
with ComputerContextManager("localhost:50051") as computer:
    print("\nGetting images from a page")
    images = computer.get_images_from_page("https://www.google.com")
    print(images)

# Get links from a page
with ComputerContextManager("localhost:50051") as computer:
    print("\nGetting links from a page")
    links = computer.get_links_from_page("https://www.google.com")
    print(links)

# Get buttons from a page
with ComputerContextManager("localhost:50051") as computer:
    print("\nGetting buttons from a page")
    buttons = computer.get_buttons_from_page("https://www.google.com")
    print(buttons)

# Get input fields from a page
with ComputerContextManager("localhost:50051") as computer:
    print("\nGetting input fields from a page")
    input_fields = computer.get_input_fields_from_page("https://www.google.com")
    print(input_fields)

# Get select fields from a page
with ComputerContextManager("localhost:50051") as computer:
    print("\nGetting select fields from a page")
    select_fields = computer.get_select_fields_from_page("https://www.google.com")
    print(select_fields)

# Get textarea fields from a page
with ComputerContextManager("localhost:50051") as computer:
    print("\nGetting textarea fields from a page")
    textarea_fields = computer.get_textarea_fields_from_page("https://www.google.com")
    print(textarea_fields)

# Test xdotool based commands
with Computer(
    "localhost:50051",
    capture_screenshot=True,
    html=True,
    persist_session=True,
    tags_to_extract=["input", "textarea", "img"],
) as computer:
    print("\nTesting xdotool based commands")

    # Navigate to test page
    computer.run_command(
        command=ComputerCommand(
            command_type=ComputerCommandType.GOTO,
            data="https://www.google.com",
        )
    )

    # Test cursor position
    content = computer.run_command(
        command=ComputerCommand(
            command_type=ComputerCommandType.CURSOR_POSITION,
        )
    )
    print("Current cursor position:", content.command_outputs[0].output)

    # Test mouse move
    content = computer.run_command(
        command=ComputerCommand(command_type=ComputerCommandType.MOUSE_MOVE, data='{"x": 100, "y": 200}')
    )
    print("Mouse move result:", content.command_outputs[0].output)

    # Test key press
    content = computer.run_command(
        command=ComputerCommand(command_type=ComputerCommandType.KEY, data="Tab")  # Example key press
    )
    print("Key press result:", content.command_outputs[0].output)

    # Test typing into specific input field
    content = computer.run_command(
        command=ComputerCommand(
            command_type=ComputerCommandType.TYPE,
            selector="input[name='q']",  # Google search input
            data="Hello World",
        )
    )
    print("Typed into search field")

    # Test global typing without selector
    content = computer.run_command(command=ComputerCommand(command_type=ComputerCommandType.TYPE, data="Global typing"))
    print("Global typing result:", content.command_outputs[0].output if content.command_outputs else "No output")

    # Test typing with ENTER
    content = computer.run_commands(
        [
            ComputerCommand(command_type=ComputerCommandType.TYPE, selector="input[name='q']", data="Search query"),
            ComputerCommand(command_type=ComputerCommandType.ENTER),
        ]
    )
    print("Typed and pressed enter")

    # Test screenshot
    content = computer.run_command(
        command=ComputerCommand(
            command_type=ComputerCommandType.SCREENSHOT,
        )
    )
    print("Screenshot captured, length:", len(content.command_outputs[0].output))

# Test downloads
with Computer(
    "localhost:50051",
    capture_screenshot=True,
    html=True,
    persist_session=True,
    tags_to_extract=["a", "button"],  # Make sure we can find download links
) as computer:
    print("\nTesting downloads")

    content = computer.run_commands(
        commands=[
            ComputerCommand(
                command_type=ComputerCommandType.GOTO,
                data="https://pypi.org/project/langrocks/#files",
            ),
            # Wait for the page to load
            ComputerCommand(
                command_type=ComputerCommandType.WAIT,
                selector=".file",
            ),
        ]
    )

    # Click on a download link (.tar.gz package as an example)
    content = computer.run_commands(
        commands=[
            ComputerCommand(
                command_type=ComputerCommandType.CLICK,
                selector="a[href$='.tar.gz']",  # Click first link ending with .tar.gz
            ),
            # Wait a bit for the download to start and complete
            ComputerCommand(
                command_type=ComputerCommandType.WAIT,
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
with Computer(
    "localhost:50051", capture_screenshot=True, html=True, persist_session=True, record_video=True
) as computer:
    print("\nTesting video recording")

    content = computer.run_commands(
        commands=[
            ComputerCommand(command_type=ComputerCommandType.GOTO, data="https://www.google.com"),
            ComputerCommand(command_type=ComputerCommandType.TERMINATE),
        ]
    )

    # Get the video
    videos = computer.get_videos()
    print(f"Received {len(videos)} videos")
