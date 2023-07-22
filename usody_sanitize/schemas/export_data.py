"""
Export Data Schema
==================

This module manages the data expected to be returned from the commands
executed to export the device data, those commands are `smartmontools`
and `lsblk`.
"""

from typing import Optional, List

from pydantic import BaseModel, Field


class Block(BaseModel):
    """Defines the schema of an output command as JSON format from
    the `lsblk` command.
    """
    path: str = Field(default=...)
    rota: bool = Field(
        default=...,
        description="Defines if the disk is flash or not."
    )

    ptuuid: Optional[str] = Field(default=None)
    serial: Optional[str] = Field(default=None)

    name: Optional[str] = Field(default=None)
    size: Optional[str] = Field(default=None)
    mode: Optional[str] = Field(default=None)

    model: Optional[str] = Field(default=None)
    vendor: Optional[str] = Field(default=None)
    uuid: Optional[str] = Field(default=None)
    type: Optional[str] = Field(default=None)
    hotplug: Optional[str] = Field(default=None)
    label: Optional[str] = Field(default=None)
    state: Optional[str] = Field(default=None)
    phy_sec: Optional[int] = Field(default=None, alias='phy-sec')

    mountpoint: Optional[str] = Field(default=None)

    children: Optional[List["Block"]] = Field(default=None)

    class Config:
        extra = "allow"


class SmartCTL(BaseModel):
    version: Optional[List[int]] = Field(default=None)
    svn_revision: Optional[str] = Field(default=None)
    platform_info: Optional[str] = Field(default=None)
    build_info: Optional[str] = Field(default=None)
    argv: Optional[List[str]] = Field(default=None)
    drive_database_version: Optional[dict] = Field(default=None)
    messages: Optional[List[dict]] = Field(default=None)
    exit_status: Optional[int] = Field(default=None)

    class Config:
        extra = "allow"


class Device(BaseModel):
    name: Optional[str] = Field(default=None,
                                description="Name of the device.")
    info_name: Optional[str] = Field(default=None)
    type: Optional[str] = Field(default=None)
    protocol: Optional[str] = Field(default=None)


class UserCapacity(BaseModel):
    blocks: Optional[int] = Field(default=None)
    bytes: Optional[int] = Field(default=None)


class Smart(BaseModel):
    """Defines the schema of an output command as JSON format from
    the `smartctl` command.
    """
    json_format_version: List[int] = Field(default=None)
    # smartctl: SmartCTL = Field(default=...)
    smartctl: Optional[dict] = Field(default=None)
    local_time: Optional[dict] = Field(default=None)
    device: Optional[Device] = Field(default=None)
    model_family: Optional[str] = Field(default=None)
    model_name: Optional[str] = Field(default=None)
    serial_number: Optional[str] = Field(default=None)
    wwn: Optional[dict] = Field(default=None)
    firmware_version: Optional[str] = Field(default=None)
    user_capacity: Optional[UserCapacity] = Field(default=None)
    logical_block_size: Optional[int] = Field(default=None)
    physical_block_size: Optional[int] = Field(default=None)
    rotation_rate: Optional[int] = Field(default=None)
    form_factor: Optional[dict] = Field(default=None)
    trim: Optional[dict] = Field(default=None)
    in_smartctl_database: Optional[bool] = Field(default=None)
    ata_version: Optional[dict] = Field(default=None)
    sata_version: Optional[dict] = Field(default=None)
    interface_speed: Optional[dict] = Field(default=None)
    smart_support: Optional[dict] = Field(default=None)
    smart_status: Optional[dict] = Field(default=None)

    class Config:
        extra = "allow"


class ExportData(BaseModel):
    block: Optional[Block] = Field(
        default=None, description="Output of `lsblk`.")
    smart: Optional[Smart] = Field(
        default=None, description="Output of `smartctl`.")

    class Config:
        extra = "allow"
