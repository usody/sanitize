from typing import Optional, List

from pydantic import BaseModel, Field


class Execution(BaseModel):
    tool: str = Field(
        default=..., description="None / shred / badblocks / hdparm / nvme")
    pattern: str = Field(default=None, description="erasure pattern")


class Method(BaseModel):
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
    verification_enabled: bool = Field(
        default=False, description="Will check if the erasure has deleted"
                                   " all the data on the disk by comparing"
                                   " some data written on the disk before"
                                   " the erasure with the data read after.")
    bad_sectors_enabled: bool = Field(
        default=False, description="If true, bad sectors will be checked"
                                   "on the erasure process")
    warnings: Optional[str] = Field(
        default=None, description="Summary of the check (no / Bad sectors)")
    overwriting_steps: List[Execution] = Field(
        default=[], description="a list of execution steps")

    class Config:
        fields = {
            "name": {"readonly": True},
        }
