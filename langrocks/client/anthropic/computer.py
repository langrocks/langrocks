import asyncio
import base64
import json
import os
import shlex
import shutil
from enum import StrEnum
from pathlib import Path
from typing import Literal, TypedDict
from uuid import uuid4

from anthropic.types.beta import BetaToolComputerUse20241022Param

from langrocks.client.computer import Computer
from langrocks.common.models.computer import ComputerCommand, ComputerCommandType

from .base import BaseAnthropicTool, ToolError, ToolResult

OUTPUT_DIR = "/tmp/outputs"

TYPING_DELAY_MS = 12
TYPING_GROUP_SIZE = 50

Action = Literal[
    "key",
    "type",
    "mouse_move",
    "left_click",
    "left_click_drag",
    "right_click",
    "middle_click",
    "double_click",
    "screenshot",
    "cursor_position",
]


class Resolution(TypedDict):
    width: int
    height: int


# sizes above XGA/WXGA are not recommended (see README.md)
# scale down to one of these targets if ComputerTool._scaling_enabled is set
MAX_SCALING_TARGETS: dict[str, Resolution] = {
    "XGA": Resolution(width=1024, height=768),  # 4:3
    "WXGA": Resolution(width=1280, height=800),  # 16:10
    "FWXGA": Resolution(width=1366, height=768),  # ~16:9
}


class ScalingSource(StrEnum):
    COMPUTER = "computer"
    API = "api"


class ComputerToolOptions(TypedDict):
    display_height_px: int
    display_width_px: int
    display_number: int | None


def chunks(s: str, chunk_size: int) -> list[str]:
    return [s[i : i + chunk_size] for i in range(0, len(s), chunk_size)]


class ComputerTool(BaseAnthropicTool):
    """
    A tool that allows the agent to interact with the screen, keyboard, and mouse of the current computer.
    The tool parameters are compatible with Anthropic Computer Tool
    """

    name: Literal["computer"] = "computer"
    api_type: Literal["computer_20241022"] = "computer_20241022"
    width: int
    height: int
    display_num: int | None

    _screenshot_delay = 2.0
    _scaling_enabled = True

    @property
    def options(self) -> ComputerToolOptions:
        width, height = self.scale_coordinates(ScalingSource.COMPUTER, self.width, self.height)
        return {
            "display_width_px": width,
            "display_height_px": height,
            "display_number": self.display_num,
        }

    def to_params(self) -> BetaToolComputerUse20241022Param:
        return {"name": self.name, "type": self.api_type, **self.options}

    def __init__(self, **kwargs):
        super().__init__()
        self._url = kwargs.get("url") or os.getenv("URL")
        self._base_url = kwargs.get("base_url") or os.getenv("BASE_URL")
        self.width = kwargs.get("width") or int(os.getenv("WIDTH") or 0)
        self.height = kwargs.get("height") or int(os.getenv("HEIGHT") or 0)

        assert self.width and self.height, "WIDTH, HEIGHT must be set"
        self._session_data = None

        self._computer = Computer(
            url=self._url,
            base_url=self._base_url,
            interactive=True,
            capture_screenshot=True,
            session_data=self._session_data,
        )

    async def __call__(
        self,
        *,
        action: Action,
        text: str | None = None,
        coordinate: tuple[int, int] | None = None,
        **kwargs,
    ):
        await asyncio.sleep(0.01)

        with self._computer as computer:
            if action in ("mouse_move", "left_click_drag"):
                if coordinate is None:
                    raise ToolError(f"coordinate is required for {action}")
                if text is not None:
                    raise ToolError(f"text is not accepted for {action}")
                if not isinstance(coordinate, list) or len(coordinate) != 2:
                    raise ToolError(f"{coordinate} must be a tuple of length 2")
                if not all(isinstance(i, int) and i >= 0 for i in coordinate):
                    raise ToolError(f"{coordinate} must be a tuple of non-negative ints")

                x, y = coordinate[0], coordinate[1]
                if action == "mouse_move":
                    coordinates = {"x": x, "y": y}
                    response = computer.run_command(
                        ComputerCommand(
                            command_type=ComputerCommandType.COMPUTER_MOUSE_MOVE, data=json.dumps(coordinates)
                        ),
                    )
                    return ToolResult(
                        output=response.command_outputs[-1].output if response.command_outputs else None,
                        error=response.command_errors[-1].error if response.command_errors else None,
                        base64_image=response.b64_screenshot,
                    )
                elif action == "left_click_drag":
                    response = computer.run_command(
                        ComputerCommand(
                            command_type=ComputerCommandType.COMPUTER_LEFT_CLICK_DRAG, data=json.dumps(coordinates)
                        ),
                    )
                    return ToolResult(
                        output=response.command_outputs[-1].output if response.command_outputs else None,
                        error=response.command_errors[-1].error if response.command_errors else None,
                        base64_image=response.b64_screenshot,
                    )
            if action in ("key", "type"):
                if text is None:
                    raise ToolError(f"text is required for {action}")
                if coordinate is not None:
                    raise ToolError(f"coordinate is not accepted for {action}")
                if not isinstance(text, str):
                    raise ToolError(output=f"{text} must be a string")

                if action == "key":
                    response = computer.run_command(
                        ComputerCommand(command_type=ComputerCommandType.COMPUTER_KEY, data=text),
                    )
                    return ToolResult(
                        output=response.command_outputs[-1].output if response.command_outputs else None,
                        error=response.command_errors[-1].error if response.command_errors else None,
                        base64_image=response.b64_screenshot,
                    )
                elif action == "type":
                    commands = []
                    for chunk in chunks(text, TYPING_GROUP_SIZE):
                        commands.append(ComputerCommand(command_type=ComputerCommandType.COMPUTER_TYPE, data=chunk))
                    response = computer.run_commands(commands)
                    return ToolResult(
                        output=(
                            "".join(output.output or "" for output in response.command_outputs)
                            if response.command_outputs
                            else None
                        ),
                        error=(
                            "".join(error.error or "" for error in response.command_errors)
                            if response.command_errors
                            else None
                        ),
                        base64_image=response.b64_screenshot,
                    )

            if action in (
                "left_click",
                "right_click",
                "double_click",
                "middle_click",
                "screenshot",
                "cursor_position",
            ):
                if text is not None:
                    raise ToolError(f"text is not accepted for {action}")
                if coordinate is not None:
                    raise ToolError(f"coordinate is not accepted for {action}")

                if action == "screenshot":
                    response = computer.run_command(
                        ComputerCommand(command_type=ComputerCommandType.COMPUTER_SCREENSHOT)
                    )
                    return ToolResult(
                        output=response.command_outputs[-1].output if response.command_outputs else None,
                        error=response.command_errors[-1].error if response.command_errors else None,
                        base64_image=response.b64_screenshot,
                    )
                elif action == "cursor_position":
                    response = computer.run_command(
                        ComputerCommand(command_type=ComputerCommandType.COMPUTER_CURSOR_POSITION)
                    )
                    return ToolResult(
                        output=response.command_outputs[-1].output if response.command_outputs else None,
                        error=response.command_errors[-1].error if response.command_errors else None,
                        base64_image=response.b64_screenshot,
                    )
                elif action == "left_click":
                    response = computer.run_command(
                        ComputerCommand(command_type=ComputerCommandType.COMPUTER_LEFT_CLICK)
                    )
                    return ToolResult(
                        output=response.command_outputs[-1].output if response.command_outputs else None,
                        error=response.command_errors[-1].error if response.command_errors else None,
                        base64_image=response.b64_screenshot,
                    )
                elif action == "right_click":
                    response = computer.run_command(
                        ComputerCommand(command_type=ComputerCommandType.COMPUTER_RIGHT_CLICK)
                    )
                    return ToolResult(
                        output=response.command_outputs[-1].output if response.command_outputs else None,
                        error=response.command_errors[-1].error if response.command_errors else None,
                        base64_image=response.b64_screenshot,
                    )
                elif action == "middle_click":
                    response = computer.run_command(
                        ComputerCommand(command_type=ComputerCommandType.COMPUTER_MIDDLE_CLICK)
                    )
                    return ToolResult(
                        output=response.command_outputs[-1].output if response.command_outputs else None,
                        error=response.command_errors[-1].error if response.command_errors else None,
                        base64_image=response.b64_screenshot,
                    )
                elif action == "double_click":
                    response = computer.run_command(
                        ComputerCommand(command_type=ComputerCommandType.COMPUTER_DOUBLE_CLICK)
                    )
                    return ToolResult(
                        output=response.command_outputs[-1].output if response.command_outputs else None,
                        error=response.command_errors[-1].error if response.command_errors else None,
                        base64_image=response.b64_screenshot,
                    )

            raise ToolError(f"Invalid action: {action}")
