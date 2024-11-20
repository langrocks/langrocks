<p align="center">
  <a href="https://langrocks.com/"><img src="https://raw.githubusercontent.com/langrocks/web/refs/heads/main/static/img/langrocks.png" alt="Langrocks" width="500px"></a>
</p>
<p align="center">
    <em>Langrocks is a collection of tools for LLMs.</em>
</p>
<p align="center">
    <a href="https://langrocks.com/docs/intro" target="_blank">Quickstart</a> | <a href="https://langrocks.com/docs/intro" target="_blank">Documentation</a> | <a href="https://langrocks.com" target="_blank">Langrocks</a>
</p>

## Installation

Install Langrocks using pip:

```bash
pip install -U langrocks
```

this will install the Langrocks CLI and the necessary dependencies. Make sure you have Docker installed on your system.

## Getting Started

Start the Langrocks server by running:

```bash
langrocks
```

This will start the necessary containers and make the server available at `localhost:3000` by default.

## Examples

Langrocks comes with several example scripts in the `langrocks/examples` directory. Here are some key features:

### Web Browser

You can use the web browser to navigate the web and extract information, get screenshots, downloads and more based on your interaction with the LLM.

```python
from langrocks.client.web_browser import WebBrowser
from langrocks.common.models.web_browser import WebBrowserCommand, WebBrowserCommandType

with WebBrowser("localhost:3000", capture_screenshot=True, html=True) as web_browser:
    # Navigate to a webpage
    content = web_browser.run_commands([
        WebBrowserCommand(
            command_type=WebBrowserCommandType.GOTO,
            data="https://www.google.com"
        ),
        WebBrowserCommand(
            command_type=WebBrowserCommandType.WAIT,
            selector="body"
        )
    ])

    # Extract content
    text = web_browser.get_text()
    html = web_browser.get_html()
    images = web_browser.get_images()    
```

### Computer

You can use the computer tool to control a remote computer and interact with it by operating the mouse and keyboard. This is useful for models like Anthropic's claude with computer use.

```python
from langrocks.client.computer import Computer
from langrocks.common.models.computer import ComputerCommand, ComputerCommandType

with Computer("localhost:3000", interactive=True) as computer:
    print(computer.get_remote_viewer_url())
    content = computer.run_commands(
        [
            ComputerCommand(command_type=ComputerCommandType.COMPUTER_KEY, data="ctrl+l"),
            ComputerCommand(command_type=ComputerCommandType.COMPUTER_WAIT, data="1"),
            ComputerCommand(command_type=ComputerCommandType.COMPUTER_TYPE, data="https://www.google.com"),
            ComputerCommand(command_type=ComputerCommandType.COMPUTER_WAIT, data="1"),
            ComputerCommand(command_type=ComputerCommandType.COMPUTER_KEY, data="Return"),
            ComputerCommand(command_type=ComputerCommandType.COMPUTER_TERMINATE),
        ]
    )
```


### File Operations

You can use the file operations tool to convert between different file formats.

```python
from langrocks.client.files import FileOperations
from langrocks.common.models.files import FileMimeType

DATA = r"""
\documentclass[a4paper,10pt]{article}
\usepackage[a4paper,margin=0.75in]{geometry}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{hyperref}
\usepackage{multicol}
...
...
"""

with FileOperations("localhost:3000") as fops:
    print("\nRunning file converter")

    # Convert file
    print("Converting file")
    response = fops.convert_file(
        data=DATA.encode(),
        filename="resume.tex",
        input_mime_type=FileMimeType.LATEX,
        output_mime_type=FileMimeType.PDF,
        options=["-V", "geometry:margin=0.5in"],
    )
```
