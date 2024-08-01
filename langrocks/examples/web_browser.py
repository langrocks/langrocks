from langrocks.client.web_browser import WebBrowserContextManager
from langrocks.common.models.web_browser import WebBrowserCommand, WebBrowserCommandType

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
