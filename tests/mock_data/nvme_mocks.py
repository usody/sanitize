"""This module contains

"""
from unittest.mock import MagicMock, AsyncMock

from config import settings


NVME_SMARTCTL = b"""{
  "model_name": "Samsung SSD 960 PRO 512GB",
  "serial_number": "S3EWNX0K216135N",
  "logical_block_size": 512,
  "user_capacity": {
    "blocks": 1000215216,
    "bytes": 512110190592
  }
}
"""


NVME_LSBLK = b"""{
   "blockdevices": [
      {
         "vendor": null,
         "model": "Samsung SSD 960 PRO 512GB",
         "serial": "S3EWNX0K216135N",
         "size": "476.9G",
         "rota": false,
         "path": "/dev/nvme0nX_fake",
         "subsystems": "block:nvme:pci"
      }
   ]
}
"""

NVM_READ_BLOCK_stdout = b"""000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000200
eeffffff01000000af129e3b000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000
55aa
"""
NVM_READ_BLOCK_stderr = b""""""


NVM_WRITE_BLOCK_stdout = b""""""
NVM_WRITE_BLOCK_stderr = b"""1+0 records in
1+0 records out
512 bytes copied, 0.000158826 s, 3.2 MB/s"""


def subprocess_run():
    yield MagicMock(stdout=NVME_SMARTCTL)
    yield MagicMock(stdout=NVME_LSBLK)
    assert False, ("`read_lsblk_and_smartctl_generator` has been called more"
                   " times than expected")


def async_run(validation=False):
    if validation:
        # First read.
        for _ in range(settings.sectors_to_validate):
            yield AsyncMock(
                returncode=0,
                stdout=MagicMock(
                    read=AsyncMock(return_value=NVM_READ_BLOCK_stdout)),
                stderr=MagicMock(
                    read=AsyncMock(return_value=NVM_READ_BLOCK_stderr)),
                wait=AsyncMock(),
            )

        # Write data.
        for _ in range(settings.sectors_to_validate):
            yield AsyncMock(
                returncode=0,
                stdout=MagicMock(
                    read=AsyncMock(return_value=NVM_WRITE_BLOCK_stdout)),
                stderr=MagicMock(
                    read=AsyncMock(return_value=NVM_WRITE_BLOCK_stderr)),
                wait=AsyncMock(),
            )

        # Read the data written.
        for _ in range(settings.sectors_to_validate):
            yield AsyncMock(
                returncode=0,
                stdout=MagicMock(
                    read=AsyncMock(return_value=NVM_WRITE_BLOCK_stdout)),
                stderr=MagicMock(
                    read=AsyncMock(return_value=NVM_WRITE_BLOCK_stderr)),
                wait=AsyncMock(),
            )

    # Erasure mock process.
    yield AsyncMock(
        returncode=0,
        stdout=MagicMock(
            read=AsyncMock(
                return_value=b"""Success formatting namespace:1""")),
        stderr=MagicMock(
            read=AsyncMock(
                return_value=b"""You are about to format nvme0n1, namespace 0x1.
Namespace nvme0n1 has parent controller(s):nvme0

WARNING: Format may irrevocably delete this device's data.
You have 10 seconds to press Ctrl-C to cancel this operation.

Use the force [--force|-f] option to suppress this warning.
Sending format operation ...
""")),
        wait=AsyncMock(),
    )
