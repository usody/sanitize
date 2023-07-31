"""
Devices Schema
==============

This module contains the schema of the disk data, `Device.export_data`
contains the output of each command when extracting data. The other
values are duplicated from this `export_data` variable.
"""
from typing import Optional

from pydantic import BaseModel, Field

from .export_data import ExportData


class Device(BaseModel):
    """Information of the device."""
    manufacturer: Optional[str] = Field(default=None)
    model: Optional[str] = Field(default=None)
    serial_number: Optional[str] = Field(default=None)
    connector: Optional[str] = Field(default=None,
                                     description="IDE/SATA/SCSI/SAS/M.2/U.2")
    size: Optional[int] = Field(default=None, description="Disk size in bites")
    storage_medium: Optional[str] = Field(default=None,
                                          description="HDD/SSD/SSDHD")

    export_data: Optional[ExportData] = Field(default=None)
