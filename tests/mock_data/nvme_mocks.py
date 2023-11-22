"""This module contains

"""
from unittest.mock import MagicMock, AsyncMock

from config import settings


# Mock `smartctl -aj /dev/nvme0nX_fake` command.
SMARTCTL = b"""{
  "model_name": "Samsung SSD 960 PRO 512GB",
  "serial_number": "S3EWNX0K216135N",
  "logical_block_size": 512,
  "user_capacity": {
    "blocks": 1000215216,
    "bytes": 512110190592
  }
}
"""


# Mock `lsblk -JOad /dev/nvme0nX_fake` command.
LSBLK = b"""{
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

FIRST_READ_BLOCK_stdout = b"""000000000000000000000000000000000000000000000000000000000000
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
000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000
0000
"""
FIRST_READ_BLOCK_stderr = b""""""

SECOND_READ_BLOCK_stdout = b"""000000000000000000000000000000000000000000000000000000000000
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
SECOND_READ_BLOCK_stderr = b""""""

LAST_READ_BLOCK_stdout = b"""38ae1c43331ba9d2cb3a0f6933287dd445c0de7beca5d48f3f2b1acf1930
93316fa35910790d19f1b9bea071f3b1212927f59b0bbcb9c89d09f76b31
4735357438076b3d6194e9ce9e3552a55744d280e08e4c7f203541ef99d5
86ef8d5298d45569cb09e3f2ab118dab26916e41395fccee3e072cca6f9b
af82df66500ea31e68a90f562ba715406220f9d06662d94cb5036e84dc83
fee6be57f762038e54cee4658d70665b8ef86f8d6ec4101845e4033ee571
8a05a7535a249e806764cc00c2ccbdb275b03d0f1626bd641b7582e6161e
99c288ef8b48a6638a2c7014490a265ce5d397e3d45b69e7dc91844e94e7
0b73cb45d5e645b70d4139b08e71c4d439ccb5c58a1e88c25ccd5846cf71
a9d74d6e55c1c842d50ad3920b3bd7a9454f43b2d739adf5d13a77988ac2
115178dadb14ce3301f52a8afb34c34f4a05d7f984b98639825b75794934
fc50e233730e8b63c1512b6d2523639747cafd96114701ef3a876e6556fd
ea4a2ee98c6a18f21419980dbc55a0b0c620ed4496b8992d18447d9fbdde
890e6b2c7d90635ab7c983ce0bd1a285aa0be84e815e04f21b21bc274650
e99f6cfe650d360052aaf09202e1e08e6b25acfd085dac6ef4d4e129e2b2
4ac05b590798294c308e8d13870d696561a39a888a8c8fba6e860a8669f4
360fb33c4c65ef24d3639161419015e0edd52c04480483f3b44c80d0bbe6
efaf
"""
LAST_READ_BLOCK_stderr = b""""""


WRITE_BLOCK_stdout = b""""""
WRITE_BLOCK_stderr = b"""1+0 records in
1+0 records out
512 bytes copied, 0.000158826 s, 3.2 MB/s"""


def subprocess_run():
    yield MagicMock(stdout=SMARTCTL)
    yield MagicMock(stdout=LSBLK)
    assert False, ("`read_lsblk_and_smartctl_generator` has been called more"
                   " times than expected")


def async_run(validation=False):
    if validation:
        # First read.
        for _ in range(settings.sectors_to_validate):
            yield AsyncMock(
                returncode=0,
                stdout=MagicMock(
                    read=AsyncMock(return_value=FIRST_READ_BLOCK_stdout)),
                stderr=MagicMock(
                    read=AsyncMock(return_value=FIRST_READ_BLOCK_stderr)),
                wait=AsyncMock(),
            )

        # Write data.
        for _ in range(settings.sectors_to_validate):
            yield AsyncMock(
                returncode=0,
                stdout=MagicMock(
                    read=AsyncMock(return_value=WRITE_BLOCK_stdout)),
                stderr=MagicMock(
                    read=AsyncMock(return_value=WRITE_BLOCK_stderr)),
                wait=AsyncMock(),
            )

        # Read the data written.
        for _ in range(settings.sectors_to_validate):
            yield AsyncMock(
                returncode=0,
                stdout=MagicMock(
                    read=AsyncMock(return_value=SECOND_READ_BLOCK_stdout)),
                stderr=MagicMock(
                    read=AsyncMock(return_value=SECOND_READ_BLOCK_stderr)),
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

    # Read the data written.
    for _ in range(settings.sectors_to_validate):
        yield AsyncMock(
            returncode=0,
            stdout=MagicMock(
                read=AsyncMock(return_value=LAST_READ_BLOCK_stdout)),
            stderr=MagicMock(
                read=AsyncMock(return_value=LAST_READ_BLOCK_stderr)),
            wait=AsyncMock(),
        )

    assert False, "`async_run` has been called more times than expected."
