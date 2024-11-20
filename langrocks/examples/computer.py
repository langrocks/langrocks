from langrocks.client.computer import Computer, ComputerContextManager
from langrocks.common.models.computer import ComputerCommand, ComputerCommandType

# Test Computer visit a page in browser
with Computer("localhost:50051", interactive=True) as computer:
    # print(computer.get_remote_viewer_url())
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

# Test Mouse move
with Computer("localhost:50051", interactive=True) as computer:
    # print(computer.get_remote_viewer_url())
    coodinates = '{"x": 100, "y": 200}'
    content = computer.run_commands(
        [
            ComputerCommand(command_type=ComputerCommandType.COMPUTER_MOUSE_MOVE, data=coodinates),
            ComputerCommand(command_type=ComputerCommandType.COMPUTER_WAIT, data="1"),
            ComputerCommand(command_type=ComputerCommandType.COMPUTER_CURSOR_POSITION),
        ]
    )
    print(content.command_outputs[-1].output == coodinates)
