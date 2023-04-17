from typing import Optional, List
from pydantic import BaseModel, Field

from usody_sanitize.schemas.devices import Device
from usody_sanitize import __version__ as app_version


class ErasureCommand(BaseModel):
    """Main and base class to define a collection of steps to proceed.
    """
    description: Optional[str] = Field(
        default=None, description="Step description")
    command: str = Field(default=..., description="Command used on this step")

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


class ErasureStep(BaseModel):
    """Main and base class to define a collection of steps to proceed.
    """
    step: int = Field(default=..., description="Step number")
    date_init: Optional[float] = Field(
        default=None, description="Date at start of the step")
    date_end: Optional[float] = Field(
        default=None, description="Date at the end of the step")
    duration: Optional[float] = Field(
        default=None, description="Duration of the step")
    commands: List[ErasureCommand] = Field(
        default=[], description="")
    success: bool = Field(default=False, description="Tells if the step has"
                                                     "been executed correctly")


class ErasureValidation(BaseModel):
    """Defines the validation process result.
    """
    result: Optional[bool] = Field(
        default=None, description="Defines if the validation is successful")
    commands: List[ErasureCommand] = Field(
        default=[], description="A list of commands used to "
                                "validate this process")
    data: dict = Field(
        default={}, description="Bytes read from each disk sector")


class ErasureMethod(BaseModel):
    name: str = Field(
        default=..., description="Erasure method name (Basic,"
                                 " Baseline Erasure, Baseline Cryptographic"
                                 " or Enhanced)")
    standard: str = Field(
        default=..., description="Standard name (NIST SP-800-88 /  HMG"
                                 " Infosec Standard 5 Baseline Standard /"
                                 " HMG Infosec Standard 5 Baseline Enhanced")
    description: Optional[str] = Field(
        default=None, description="Description of the method")
    removal_process: Optional[str] = Field(
        default=None, description="Demagnetization / Destruction /"
                                  " Overwriting / Cryptographic erase")
    program: Optional[str] = Field(
        default=None, description="None / shred / badblocks / hdparm")
    verification_enabled: bool = Field(
        default=False, description="Will check if the erasure has deleted"
                                   " all the data on the disk by comparing"
                                   " some data written on the disk before"
                                   " the erasure with the data read after.")
    bad_sectors_enabled: bool = Field(
        default=False, description="If true, bad sectors will be checked"
                                   "on the erasure process")
    # sectors_total: Optional[int] = Field(
    #     default=None, description="Total number of sectors")
    # sectors_bad: Optional[int] = Field(
    #     default=None, description="Total of bad sectors")
    warnings: Optional[str] = Field(
        default=None, description="Summary of the check (no / Bad sectors)")
    overwriting_steps: Optional[int] = Field(
        default=None, description="Number of overwriting steps")

    class Config:
        fields = {
            "name": {"readonly": True},
        }


class ErasureCertificate(BaseModel):
    erasure_steps: List[ErasureStep] = Field(
        default=[], description="A list of erasure steps, each steps contain"
                                " a list of commands and the result of each"
                                " command.")
    validation: Optional[ErasureValidation] = Field(
        default=None, description="Information to certificate"
                                  "the validation process.")

    # Storage Drive
    device_info: Device = Field(
        default=..., description="all info about the device")

    # Method
    method: Optional[ErasureMethod] = Field(
        default=None, description="Erasure method")

    result: bool = Field(
        default=False, description="True means erasure has been pass"
                                   " correctly, False means something"
                                   " failed and the data could not be"
                                   " erased/wipe.")

    sanitize_version: str = Field(
        default=app_version,
        description="Version of usody_sanitize python package.")


