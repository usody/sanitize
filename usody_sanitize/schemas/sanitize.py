import time
from typing import Optional, List

from pydantic import BaseModel, Field

from usody_sanitize import __version__ as app_version
from usody_sanitize.schemas.definition import Method
from usody_sanitize.schemas.devices import Device


class Exec(BaseModel):
    """Define the data collected while executing each command, this is
    used to prove the execution of all commands and steps to properly
    sanitize the device.
    """
    description: Optional[str] = Field(
        default=None, description="command description")
    command: str = Field(default=..., description="command to be executed")

    stdout: Optional[str] = Field(
        default=None, description="normal output from the command executed")
    stderr: Optional[str] = Field(
        default=None, description="error output from the command executed")

    return_code: Optional[int] = Field(
        default=None, description="Command return code")

    success: bool = Field(
        default=False, description="Tells if the step has been executed"
                                   " correctly")

    start_time: float = Field(
        default=..., description="Exact time when the command started")
    end_time: Optional[float] = Field(
        default=None, description="Exact time when the command ended")

    def __init__(self, *args, **kwargs):
        if 'start_time' not in kwargs:
            kwargs['start_time'] = time.time()
        super().__init__(*args, **kwargs)


class Step(BaseModel):
    """Main and base class to define a collection of steps to proceed.
    """
    step: Optional[int] = Field(default=None, description="Step number")
    start_time: Optional[float] = Field(
        default=None, description="start time of the step")
    end_time: Optional[float] = Field(
        default=None, description="end time of the step")
    duration: Optional[float] = Field(
        default=None, description="step duration time")
    commands: List[Exec] = Field(
        default=[], description="a list of commands executed for current step")
    success: bool = Field(
        default=False, description="Tells if the step has"
                                   " been executed correctly")

    def __init__(self, *args, **kwargs):
        if 'start_time' not in kwargs:
            kwargs['start_time'] = time.time()
        super().__init__(*args, **kwargs)

    def end(self):
        self.end_time = time.time()
        # Todo: Remove this duration variable once the tool is more robust.
        self.duration = self.end_time - self.start_time


class SanitizeValidation(BaseModel):
    """Defines the validation process result.
    """
    result: Optional[bool] = Field(
        default=None, description="Defines if the validation is successful")
    commands: List[Exec] = Field(
        default=[], description="A list of commands used to "
                                "validate this process")
    data: dict = Field(
        default={}, description="Bytes read from each disk sector")


class Sanitize(BaseModel):
    """This contains all the data to create a certificate of the
    complete sanitation process.
    """
    steps: List[Step] = Field(
        default=[], description="a list of sanitize steps, each steps contain"
                                " a list of commands and the result of each"
                                " command")
    validation: Optional[SanitizeValidation] = Field(
        default=None, description="information to certificate"
                                  "the validation process")

    # Storage Drive
    device_info: Device = Field(
        default=..., description="all info about the device")

    # Method
    method: Optional[Method] = Field(
        default=None, description="erasure method")

    result: bool = Field(
        default=False, description="true means erasure has been pass"
                                   " correctly, False means something"
                                   " failed and the data could not be"
                                   " erased/wipe")

    version: str = Field(
        default=app_version,
        description="version of usody_sanitize python package")
