"""Output commands to simulate the responses from a real disk.

Shred command to simulate an HDD connected via USB dock station.

"""
from unittest.mock import MagicMock, AsyncMock

from config import settings


# Mock `smartctl -aj /dev/sdX` command.
SMARTCTL = b"""{
  "model_name": "TOSHIBA MK3259GSXP",
  "serial_number": "42T9CPEGT",
  "logical_block_size": 512,
  "user_capacity": {
    "blocks": 625142448,
    "bytes": 320072933376
  }
}
"""


# Mock `lsblk -JOad /dev/sdX` command.
LSBLK = b"""{
   "blockdevices": [
      {
         "vendor": "TOSHIBA ",
         "model": "MK3259GSXP",
         "serial": "152D00539000",
         "size": "298.1G",
         "rota": true,
         "path": "/dev/sdX_fake",
         "subsystems": "block:scsi:usb:pci"
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

WRITE_BLOCK_STDOUT = b""""""
WRITE_BLOCK_STDERR = b"""1+0 records in
1+0 records out
512 bytes copied, 0.000158826 s, 3.2 MB/s"""


def subprocess_run():
    yield MagicMock(stdout=SMARTCTL)
    yield MagicMock(stdout=LSBLK)
    assert False, "`subprocess_run` has been called more times than expected"


def async_run(validation=False):
    """A simple generator to generate the async expected responses.
    """
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
                    read=AsyncMock(return_value=WRITE_BLOCK_STDOUT)),
                stderr=MagicMock(
                    read=AsyncMock(return_value=WRITE_BLOCK_STDERR)),
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
                return_value=b"""""")),
        stderr=MagicMock(
            read=AsyncMock(
                return_value=b"""shred: /dev/sdX_fake: pass 1/1 (random)...
shred: /dev/sdX_fake: pass 1/1 (random)...350MiB/299GiB 0%
shred: /dev/sdX_fake: pass 1/1 (random)...782MiB/299GiB 0%
shred: /dev/sdX_fake: pass 1/1 (random)...1.1GiB/299GiB 0%
shred: /dev/sdX_fake: pass 1/1 (random)...1.6GiB/299GiB 0%
shred: /dev/sdX_fake: pass 1/1 (random)...2.0GiB/299GiB 0%
shred: /dev/sdX_fake: pass 1/1 (random)...2.4GiB/299GiB 0%
shred: /dev/sdX_fake: pass 1/1 (random)...2.8GiB/299GiB 0%
shred: /dev/sdX_fake: pass 1/1 (random)...3.3GiB/299GiB 1%
shred: /dev/sdX_fake: pass 1/1 (random)...3.7GiB/299GiB 1%
shred: /dev/sdX_fake: pass 1/1 (random)...4.1GiB/299GiB 1%
shred: /dev/sdX_fake: pass 1/1 (random)...4.5GiB/299GiB 1%
shred: /dev/sdX_fake: pass 1/1 (random)...4.9GiB/299GiB 1%
shred: /dev/sdX_fake: pass 1/1 (random)...5.1GiB/299GiB 1%
shred: /dev/sdX_fake: pass 1/1 (random)...5.2GiB/299GiB 1%
shred: /dev/sdX_fake: pass 1/1 (random)...5.5GiB/299GiB 1%
shred: /dev/sdX_fake: pass 1/1 (random)...5.9GiB/299GiB 2%
shred: /dev/sdX_fake: pass 1/1 (random)...6.4GiB/299GiB 2%
shred: /dev/sdX_fake: pass 1/1 (random)...6.8GiB/299GiB 2%
shred: /dev/sdX_fake: pass 1/1 (random)...7.2GiB/299GiB 2%
shred: /dev/sdX_fake: pass 1/1 (random)...7.6GiB/299GiB 2%
shred: /dev/sdX_fake: pass 1/1 (random)...8.0GiB/299GiB 2%
shred: /dev/sdX_fake: pass 1/1 (random)...8.5GiB/299GiB 2%
shred: /dev/sdX_fake: pass 1/1 (random)...8.9GiB/299GiB 2%
shred: /dev/sdX_fake: pass 1/1 (random)...9.3GiB/299GiB 3%
shred: /dev/sdX_fake: pass 1/1 (random)...9.7GiB/299GiB 3%
shred: /dev/sdX_fake: pass 1/1 (random)...10GiB/299GiB 3%
shred: /dev/sdX_fake: pass 1/1 (random)...11GiB/299GiB 3%
shred: /dev/sdX_fake: pass 1/1 (random)...12GiB/299GiB 4%
shred: /dev/sdX_fake: pass 1/1 (random)...13GiB/299GiB 4%
shred: /dev/sdX_fake: pass 1/1 (random)...14GiB/299GiB 4%
shred: /dev/sdX_fake: pass 1/1 (random)...15GiB/299GiB 5%
shred: /dev/sdX_fake: pass 1/1 (random)...16GiB/299GiB 5%
shred: /dev/sdX_fake: pass 1/1 (random)...17GiB/299GiB 5%
shred: /dev/sdX_fake: pass 1/1 (random)...18GiB/299GiB 6%
shred: /dev/sdX_fake: pass 1/1 (random)...19GiB/299GiB 6%
shred: /dev/sdX_fake: pass 1/1 (random)...20GiB/299GiB 6%
shred: /dev/sdX_fake: pass 1/1 (random)...21GiB/299GiB 7%
shred: /dev/sdX_fake: pass 1/1 (random)...22GiB/299GiB 7%
shred: /dev/sdX_fake: pass 1/1 (random)...23GiB/299GiB 7%
shred: /dev/sdX_fake: pass 1/1 (random)...24GiB/299GiB 8%
shred: /dev/sdX_fake: pass 1/1 (random)...25GiB/299GiB 8%
shred: /dev/sdX_fake: pass 1/1 (random)...26GiB/299GiB 8%
shred: /dev/sdX_fake: pass 1/1 (random)...27GiB/299GiB 9%
shred: /dev/sdX_fake: pass 1/1 (random)...28GiB/299GiB 9%
shred: /dev/sdX_fake: pass 1/1 (random)...29GiB/299GiB 9%
shred: /dev/sdX_fake: pass 1/1 (random)...30GiB/299GiB 10%
shred: /dev/sdX_fake: pass 1/1 (random)...31GiB/299GiB 10%
shred: /dev/sdX_fake: pass 1/1 (random)...32GiB/299GiB 10%
shred: /dev/sdX_fake: pass 1/1 (random)...33GiB/299GiB 11%
shred: /dev/sdX_fake: pass 1/1 (random)...34GiB/299GiB 11%
shred: /dev/sdX_fake: pass 1/1 (random)...35GiB/299GiB 11%
shred: /dev/sdX_fake: pass 1/1 (random)...36GiB/299GiB 12%
shred: /dev/sdX_fake: pass 1/1 (random)...37GiB/299GiB 12%
shred: /dev/sdX_fake: pass 1/1 (random)...38GiB/299GiB 12%
shred: /dev/sdX_fake: pass 1/1 (random)...39GiB/299GiB 13%
shred: /dev/sdX_fake: pass 1/1 (random)...40GiB/299GiB 13%
shred: /dev/sdX_fake: pass 1/1 (random)...41GiB/299GiB 13%
shred: /dev/sdX_fake: pass 1/1 (random)...42GiB/299GiB 14%
shred: /dev/sdX_fake: pass 1/1 (random)...43GiB/299GiB 14%
shred: /dev/sdX_fake: pass 1/1 (random)...44GiB/299GiB 14%
shred: /dev/sdX_fake: pass 1/1 (random)...45GiB/299GiB 15%
shred: /dev/sdX_fake: pass 1/1 (random)...46GiB/299GiB 15%
shred: /dev/sdX_fake: pass 1/1 (random)...47GiB/299GiB 15%
shred: /dev/sdX_fake: pass 1/1 (random)...48GiB/299GiB 16%
shred: /dev/sdX_fake: pass 1/1 (random)...49GiB/299GiB 16%
shred: /dev/sdX_fake: pass 1/1 (random)...50GiB/299GiB 16%
shred: /dev/sdX_fake: pass 1/1 (random)...51GiB/299GiB 17%
shred: /dev/sdX_fake: pass 1/1 (random)...52GiB/299GiB 17%
shred: /dev/sdX_fake: pass 1/1 (random)...53GiB/299GiB 17%
shred: /dev/sdX_fake: pass 1/1 (random)...54GiB/299GiB 18%
shred: /dev/sdX_fake: pass 1/1 (random)...55GiB/299GiB 18%
shred: /dev/sdX_fake: pass 1/1 (random)...56GiB/299GiB 18%
shred: /dev/sdX_fake: pass 1/1 (random)...57GiB/299GiB 19%
shred: /dev/sdX_fake: pass 1/1 (random)...58GiB/299GiB 19%
shred: /dev/sdX_fake: pass 1/1 (random)...59GiB/299GiB 19%
shred: /dev/sdX_fake: pass 1/1 (random)...60GiB/299GiB 20%
shred: /dev/sdX_fake: pass 1/1 (random)...61GiB/299GiB 20%
shred: /dev/sdX_fake: pass 1/1 (random)...62GiB/299GiB 20%
shred: /dev/sdX_fake: pass 1/1 (random)...63GiB/299GiB 21%
shred: /dev/sdX_fake: pass 1/1 (random)...64GiB/299GiB 21%
shred: /dev/sdX_fake: pass 1/1 (random)...65GiB/299GiB 21%
shred: /dev/sdX_fake: pass 1/1 (random)...66GiB/299GiB 22%
shred: /dev/sdX_fake: pass 1/1 (random)...67GiB/299GiB 22%
shred: /dev/sdX_fake: pass 1/1 (random)...68GiB/299GiB 22%
shred: /dev/sdX_fake: pass 1/1 (random)...69GiB/299GiB 23%
shred: /dev/sdX_fake: pass 1/1 (random)...70GiB/299GiB 23%
shred: /dev/sdX_fake: pass 1/1 (random)...71GiB/299GiB 23%
shred: /dev/sdX_fake: pass 1/1 (random)...72GiB/299GiB 24%
shred: /dev/sdX_fake: pass 1/1 (random)...73GiB/299GiB 24%
shred: /dev/sdX_fake: pass 1/1 (random)...74GiB/299GiB 24%
shred: /dev/sdX_fake: pass 1/1 (random)...75GiB/299GiB 25%
shred: /dev/sdX_fake: pass 1/1 (random)...76GiB/299GiB 25%
shred: /dev/sdX_fake: pass 1/1 (random)...77GiB/299GiB 25%
shred: /dev/sdX_fake: pass 1/1 (random)...78GiB/299GiB 26%
shred: /dev/sdX_fake: pass 1/1 (random)...79GiB/299GiB 26%
shred: /dev/sdX_fake: pass 1/1 (random)...80GiB/299GiB 26%
shred: /dev/sdX_fake: pass 1/1 (random)...81GiB/299GiB 27%
shred: /dev/sdX_fake: pass 1/1 (random)...82GiB/299GiB 27%
shred: /dev/sdX_fake: pass 1/1 (random)...83GiB/299GiB 27%
shred: /dev/sdX_fake: pass 1/1 (random)...84GiB/299GiB 28%
shred: /dev/sdX_fake: pass 1/1 (random)...85GiB/299GiB 28%
shred: /dev/sdX_fake: pass 1/1 (random)...86GiB/299GiB 28%
shred: /dev/sdX_fake: pass 1/1 (random)...87GiB/299GiB 29%
shred: /dev/sdX_fake: pass 1/1 (random)...88GiB/299GiB 29%
shred: /dev/sdX_fake: pass 1/1 (random)...89GiB/299GiB 29%
shred: /dev/sdX_fake: pass 1/1 (random)...90GiB/299GiB 30%
shred: /dev/sdX_fake: pass 1/1 (random)...91GiB/299GiB 30%
shred: /dev/sdX_fake: pass 1/1 (random)...92GiB/299GiB 30%
shred: /dev/sdX_fake: pass 1/1 (random)...93GiB/299GiB 31%
shred: /dev/sdX_fake: pass 1/1 (random)...94GiB/299GiB 31%
shred: /dev/sdX_fake: pass 1/1 (random)...95GiB/299GiB 31%
shred: /dev/sdX_fake: pass 1/1 (random)...96GiB/299GiB 32%
shred: /dev/sdX_fake: pass 1/1 (random)...97GiB/299GiB 32%
shred: /dev/sdX_fake: pass 1/1 (random)...98GiB/299GiB 32%
shred: /dev/sdX_fake: pass 1/1 (random)...99GiB/299GiB 33%
shred: /dev/sdX_fake: pass 1/1 (random)...100GiB/299GiB 33%
shred: /dev/sdX_fake: pass 1/1 (random)...101GiB/299GiB 33%
shred: /dev/sdX_fake: pass 1/1 (random)...102GiB/299GiB 34%
shred: /dev/sdX_fake: pass 1/1 (random)...103GiB/299GiB 34%
shred: /dev/sdX_fake: pass 1/1 (random)...104GiB/299GiB 34%
shred: /dev/sdX_fake: pass 1/1 (random)...105GiB/299GiB 35%
shred: /dev/sdX_fake: pass 1/1 (random)...106GiB/299GiB 35%
shred: /dev/sdX_fake: pass 1/1 (random)...107GiB/299GiB 35%
shred: /dev/sdX_fake: pass 1/1 (random)...108GiB/299GiB 36%
shred: /dev/sdX_fake: pass 1/1 (random)...109GiB/299GiB 36%
shred: /dev/sdX_fake: pass 1/1 (random)...110GiB/299GiB 36%
shred: /dev/sdX_fake: pass 1/1 (random)...111GiB/299GiB 37%
shred: /dev/sdX_fake: pass 1/1 (random)...112GiB/299GiB 37%
shred: /dev/sdX_fake: pass 1/1 (random)...113GiB/299GiB 37%
shred: /dev/sdX_fake: pass 1/1 (random)...114GiB/299GiB 38%
shred: /dev/sdX_fake: pass 1/1 (random)...115GiB/299GiB 38%
shred: /dev/sdX_fake: pass 1/1 (random)...116GiB/299GiB 38%
shred: /dev/sdX_fake: pass 1/1 (random)...117GiB/299GiB 39%
shred: /dev/sdX_fake: pass 1/1 (random)...118GiB/299GiB 39%
shred: /dev/sdX_fake: pass 1/1 (random)...119GiB/299GiB 39%
shred: /dev/sdX_fake: pass 1/1 (random)...120GiB/299GiB 40%
shred: /dev/sdX_fake: pass 1/1 (random)...121GiB/299GiB 40%
shred: /dev/sdX_fake: pass 1/1 (random)...122GiB/299GiB 40%
shred: /dev/sdX_fake: pass 1/1 (random)...123GiB/299GiB 41%
shred: /dev/sdX_fake: pass 1/1 (random)...124GiB/299GiB 41%
shred: /dev/sdX_fake: pass 1/1 (random)...125GiB/299GiB 41%
shred: /dev/sdX_fake: pass 1/1 (random)...126GiB/299GiB 42%
shred: /dev/sdX_fake: pass 1/1 (random)...127GiB/299GiB 42%
shred: /dev/sdX_fake: pass 1/1 (random)...128GiB/299GiB 42%
shred: /dev/sdX_fake: pass 1/1 (random)...129GiB/299GiB 43%
shred: /dev/sdX_fake: pass 1/1 (random)...130GiB/299GiB 43%
shred: /dev/sdX_fake: pass 1/1 (random)...131GiB/299GiB 43%
shred: /dev/sdX_fake: pass 1/1 (random)...132GiB/299GiB 44%
shred: /dev/sdX_fake: pass 1/1 (random)...133GiB/299GiB 44%
shred: /dev/sdX_fake: pass 1/1 (random)...134GiB/299GiB 44%
shred: /dev/sdX_fake: pass 1/1 (random)...135GiB/299GiB 45%
shred: /dev/sdX_fake: pass 1/1 (random)...136GiB/299GiB 45%
shred: /dev/sdX_fake: pass 1/1 (random)...137GiB/299GiB 45%
shred: /dev/sdX_fake: pass 1/1 (random)...138GiB/299GiB 46%
shred: /dev/sdX_fake: pass 1/1 (random)...139GiB/299GiB 46%
shred: /dev/sdX_fake: pass 1/1 (random)...140GiB/299GiB 46%
shred: /dev/sdX_fake: pass 1/1 (random)...141GiB/299GiB 47%
shred: /dev/sdX_fake: pass 1/1 (random)...142GiB/299GiB 47%
shred: /dev/sdX_fake: pass 1/1 (random)...143GiB/299GiB 47%
shred: /dev/sdX_fake: pass 1/1 (random)...144GiB/299GiB 48%
shred: /dev/sdX_fake: pass 1/1 (random)...145GiB/299GiB 48%
shred: /dev/sdX_fake: pass 1/1 (random)...146GiB/299GiB 48%
shred: /dev/sdX_fake: pass 1/1 (random)...147GiB/299GiB 49%
shred: /dev/sdX_fake: pass 1/1 (random)...148GiB/299GiB 49%
shred: /dev/sdX_fake: pass 1/1 (random)...149GiB/299GiB 49%
shred: /dev/sdX_fake: pass 1/1 (random)...150GiB/299GiB 50%
shred: /dev/sdX_fake: pass 1/1 (random)...151GiB/299GiB 50%
shred: /dev/sdX_fake: pass 1/1 (random)...152GiB/299GiB 50%
shred: /dev/sdX_fake: pass 1/1 (random)...153GiB/299GiB 51%
shred: /dev/sdX_fake: pass 1/1 (random)...154GiB/299GiB 51%
shred: /dev/sdX_fake: pass 1/1 (random)...155GiB/299GiB 51%
shred: /dev/sdX_fake: pass 1/1 (random)...156GiB/299GiB 52%
shred: /dev/sdX_fake: pass 1/1 (random)...157GiB/299GiB 52%
shred: /dev/sdX_fake: pass 1/1 (random)...158GiB/299GiB 53%
shred: /dev/sdX_fake: pass 1/1 (random)...159GiB/299GiB 53%
shred: /dev/sdX_fake: pass 1/1 (random)...160GiB/299GiB 53%
shred: /dev/sdX_fake: pass 1/1 (random)...161GiB/299GiB 54%
shred: /dev/sdX_fake: pass 1/1 (random)...162GiB/299GiB 54%
shred: /dev/sdX_fake: pass 1/1 (random)...163GiB/299GiB 54%
shred: /dev/sdX_fake: pass 1/1 (random)...164GiB/299GiB 55%
shred: /dev/sdX_fake: pass 1/1 (random)...165GiB/299GiB 55%
shred: /dev/sdX_fake: pass 1/1 (random)...166GiB/299GiB 55%
shred: /dev/sdX_fake: pass 1/1 (random)...167GiB/299GiB 56%
shred: /dev/sdX_fake: pass 1/1 (random)...168GiB/299GiB 56%
shred: /dev/sdX_fake: pass 1/1 (random)...169GiB/299GiB 56%
shred: /dev/sdX_fake: pass 1/1 (random)...170GiB/299GiB 57%
shred: /dev/sdX_fake: pass 1/1 (random)...171GiB/299GiB 57%
shred: /dev/sdX_fake: pass 1/1 (random)...172GiB/299GiB 57%
shred: /dev/sdX_fake: pass 1/1 (random)...173GiB/299GiB 58%
shred: /dev/sdX_fake: pass 1/1 (random)...174GiB/299GiB 58%
shred: /dev/sdX_fake: pass 1/1 (random)...175GiB/299GiB 58%
shred: /dev/sdX_fake: pass 1/1 (random)...176GiB/299GiB 59%
shred: /dev/sdX_fake: pass 1/1 (random)...177GiB/299GiB 59%
shred: /dev/sdX_fake: pass 1/1 (random)...178GiB/299GiB 59%
shred: /dev/sdX_fake: pass 1/1 (random)...179GiB/299GiB 60%
shred: /dev/sdX_fake: pass 1/1 (random)...180GiB/299GiB 60%
shred: /dev/sdX_fake: pass 1/1 (random)...181GiB/299GiB 60%
shred: /dev/sdX_fake: pass 1/1 (random)...182GiB/299GiB 61%
shred: /dev/sdX_fake: pass 1/1 (random)...183GiB/299GiB 61%
shred: /dev/sdX_fake: pass 1/1 (random)...184GiB/299GiB 61%
shred: /dev/sdX_fake: pass 1/1 (random)...185GiB/299GiB 62%
shred: /dev/sdX_fake: pass 1/1 (random)...186GiB/299GiB 62%
shred: /dev/sdX_fake: pass 1/1 (random)...187GiB/299GiB 62%
shred: /dev/sdX_fake: pass 1/1 (random)...188GiB/299GiB 63%
shred: /dev/sdX_fake: pass 1/1 (random)...189GiB/299GiB 63%
shred: /dev/sdX_fake: pass 1/1 (random)...190GiB/299GiB 63%
shred: /dev/sdX_fake: pass 1/1 (random)...191GiB/299GiB 64%
shred: /dev/sdX_fake: pass 1/1 (random)...192GiB/299GiB 64%
shred: /dev/sdX_fake: pass 1/1 (random)...193GiB/299GiB 64%
shred: /dev/sdX_fake: pass 1/1 (random)...194GiB/299GiB 65%
shred: /dev/sdX_fake: pass 1/1 (random)...195GiB/299GiB 65%
shred: /dev/sdX_fake: pass 1/1 (random)...196GiB/299GiB 65%
shred: /dev/sdX_fake: pass 1/1 (random)...197GiB/299GiB 66%
shred: /dev/sdX_fake: pass 1/1 (random)...198GiB/299GiB 66%
shred: /dev/sdX_fake: pass 1/1 (random)...199GiB/299GiB 66%
shred: /dev/sdX_fake: pass 1/1 (random)...200GiB/299GiB 67%
shred: /dev/sdX_fake: pass 1/1 (random)...201GiB/299GiB 67%
shred: /dev/sdX_fake: pass 1/1 (random)...202GiB/299GiB 67%
shred: /dev/sdX_fake: pass 1/1 (random)...203GiB/299GiB 68%
shred: /dev/sdX_fake: pass 1/1 (random)...204GiB/299GiB 68%
shred: /dev/sdX_fake: pass 1/1 (random)...205GiB/299GiB 68%
shred: /dev/sdX_fake: pass 1/1 (random)...206GiB/299GiB 69%
shred: /dev/sdX_fake: pass 1/1 (random)...207GiB/299GiB 69%
shred: /dev/sdX_fake: pass 1/1 (random)...208GiB/299GiB 69%
shred: /dev/sdX_fake: pass 1/1 (random)...209GiB/299GiB 70%
shred: /dev/sdX_fake: pass 1/1 (random)...210GiB/299GiB 70%
shred: /dev/sdX_fake: pass 1/1 (random)...211GiB/299GiB 70%
shred: /dev/sdX_fake: pass 1/1 (random)...212GiB/299GiB 71%
shred: /dev/sdX_fake: pass 1/1 (random)...213GiB/299GiB 71%
shred: /dev/sdX_fake: pass 1/1 (random)...214GiB/299GiB 71%
shred: /dev/sdX_fake: pass 1/1 (random)...215GiB/299GiB 72%
shred: /dev/sdX_fake: pass 1/1 (random)...216GiB/299GiB 72%
shred: /dev/sdX_fake: pass 1/1 (random)...217GiB/299GiB 72%
shred: /dev/sdX_fake: pass 1/1 (random)...218GiB/299GiB 73%
shred: /dev/sdX_fake: pass 1/1 (random)...219GiB/299GiB 73%
shred: /dev/sdX_fake: pass 1/1 (random)...220GiB/299GiB 73%
shred: /dev/sdX_fake: pass 1/1 (random)...221GiB/299GiB 74%
shred: /dev/sdX_fake: pass 1/1 (random)...222GiB/299GiB 74%
shred: /dev/sdX_fake: pass 1/1 (random)...223GiB/299GiB 74%
shred: /dev/sdX_fake: pass 1/1 (random)...224GiB/299GiB 75%
shred: /dev/sdX_fake: pass 1/1 (random)...225GiB/299GiB 75%
shred: /dev/sdX_fake: pass 1/1 (random)...226GiB/299GiB 75%
shred: /dev/sdX_fake: pass 1/1 (random)...227GiB/299GiB 76%
shred: /dev/sdX_fake: pass 1/1 (random)...228GiB/299GiB 76%
shred: /dev/sdX_fake: pass 1/1 (random)...229GiB/299GiB 76%
shred: /dev/sdX_fake: pass 1/1 (random)...230GiB/299GiB 77%
shred: /dev/sdX_fake: pass 1/1 (random)...231GiB/299GiB 77%
shred: /dev/sdX_fake: pass 1/1 (random)...232GiB/299GiB 77%
shred: /dev/sdX_fake: pass 1/1 (random)...233GiB/299GiB 78%
shred: /dev/sdX_fake: pass 1/1 (random)...234GiB/299GiB 78%
shred: /dev/sdX_fake: pass 1/1 (random)...235GiB/299GiB 78%
shred: /dev/sdX_fake: pass 1/1 (random)...236GiB/299GiB 79%
shred: /dev/sdX_fake: pass 1/1 (random)...237GiB/299GiB 79%
shred: /dev/sdX_fake: pass 1/1 (random)...238GiB/299GiB 79%
shred: /dev/sdX_fake: pass 1/1 (random)...239GiB/299GiB 80%
shred: /dev/sdX_fake: pass 1/1 (random)...240GiB/299GiB 80%
shred: /dev/sdX_fake: pass 1/1 (random)...241GiB/299GiB 80%
shred: /dev/sdX_fake: pass 1/1 (random)...242GiB/299GiB 81%
shred: /dev/sdX_fake: pass 1/1 (random)...243GiB/299GiB 81%
shred: /dev/sdX_fake: pass 1/1 (random)...244GiB/299GiB 81%
shred: /dev/sdX_fake: pass 1/1 (random)...245GiB/299GiB 82%
shred: /dev/sdX_fake: pass 1/1 (random)...246GiB/299GiB 82%
shred: /dev/sdX_fake: pass 1/1 (random)...247GiB/299GiB 82%
shred: /dev/sdX_fake: pass 1/1 (random)...248GiB/299GiB 83%
shred: /dev/sdX_fake: pass 1/1 (random)...249GiB/299GiB 83%
shred: /dev/sdX_fake: pass 1/1 (random)...250GiB/299GiB 83%
shred: /dev/sdX_fake: pass 1/1 (random)...251GiB/299GiB 84%
shred: /dev/sdX_fake: pass 1/1 (random)...252GiB/299GiB 84%
shred: /dev/sdX_fake: pass 1/1 (random)...253GiB/299GiB 84%
shred: /dev/sdX_fake: pass 1/1 (random)...254GiB/299GiB 85%
shred: /dev/sdX_fake: pass 1/1 (random)...255GiB/299GiB 85%
shred: /dev/sdX_fake: pass 1/1 (random)...256GiB/299GiB 85%
shred: /dev/sdX_fake: pass 1/1 (random)...257GiB/299GiB 86%
shred: /dev/sdX_fake: pass 1/1 (random)...258GiB/299GiB 86%
shred: /dev/sdX_fake: pass 1/1 (random)...259GiB/299GiB 86%
shred: /dev/sdX_fake: pass 1/1 (random)...260GiB/299GiB 87%
shred: /dev/sdX_fake: pass 1/1 (random)...261GiB/299GiB 87%
shred: /dev/sdX_fake: pass 1/1 (random)...262GiB/299GiB 87%
shred: /dev/sdX_fake: pass 1/1 (random)...263GiB/299GiB 88%
shred: /dev/sdX_fake: pass 1/1 (random)...264GiB/299GiB 88%
shred: /dev/sdX_fake: pass 1/1 (random)...265GiB/299GiB 88%
shred: /dev/sdX_fake: pass 1/1 (random)...266GiB/299GiB 89%
shred: /dev/sdX_fake: pass 1/1 (random)...267GiB/299GiB 89%
shred: /dev/sdX_fake: pass 1/1 (random)...268GiB/299GiB 89%
shred: /dev/sdX_fake: pass 1/1 (random)...269GiB/299GiB 90%
shred: /dev/sdX_fake: pass 1/1 (random)...270GiB/299GiB 90%
shred: /dev/sdX_fake: pass 1/1 (random)...271GiB/299GiB 90%
shred: /dev/sdX_fake: pass 1/1 (random)...272GiB/299GiB 91%
shred: /dev/sdX_fake: pass 1/1 (random)...273GiB/299GiB 91%
shred: /dev/sdX_fake: pass 1/1 (random)...274GiB/299GiB 91%
shred: /dev/sdX_fake: pass 1/1 (random)...275GiB/299GiB 92%
shred: /dev/sdX_fake: pass 1/1 (random)...276GiB/299GiB 92%
shred: /dev/sdX_fake: pass 1/1 (random)...277GiB/299GiB 92%
shred: /dev/sdX_fake: pass 1/1 (random)...278GiB/299GiB 93%
shred: /dev/sdX_fake: pass 1/1 (random)...279GiB/299GiB 93%
shred: /dev/sdX_fake: pass 1/1 (random)...280GiB/299GiB 93%
shred: /dev/sdX_fake: pass 1/1 (random)...281GiB/299GiB 94%
shred: /dev/sdX_fake: pass 1/1 (random)...282GiB/299GiB 94%
shred: /dev/sdX_fake: pass 1/1 (random)...283GiB/299GiB 94%
shred: /dev/sdX_fake: pass 1/1 (random)...284GiB/299GiB 95%
shred: /dev/sdX_fake: pass 1/1 (random)...285GiB/299GiB 95%
shred: /dev/sdX_fake: pass 1/1 (random)...286GiB/299GiB 95%
shred: /dev/sdX_fake: pass 1/1 (random)...287GiB/299GiB 96%
shred: /dev/sdX_fake: pass 1/1 (random)...288GiB/299GiB 96%
shred: /dev/sdX_fake: pass 1/1 (random)...289GiB/299GiB 96%
shred: /dev/sdX_fake: pass 1/1 (random)...290GiB/299GiB 97%
shred: /dev/sdX_fake: pass 1/1 (random)...291GiB/299GiB 97%
shred: /dev/sdX_fake: pass 1/1 (random)...292GiB/299GiB 97%
shred: /dev/sdX_fake: pass 1/1 (random)...293GiB/299GiB 98%
shred: /dev/sdX_fake: pass 1/1 (random)...294GiB/299GiB 98%
shred: /dev/sdX_fake: pass 1/1 (random)...295GiB/299GiB 98%
shred: /dev/sdX_fake: pass 1/1 (random)...296GiB/299GiB 99%
shred: /dev/sdX_fake: pass 1/1 (random)...297GiB/299GiB 99%
shred: /dev/sdX_fake: pass 1/1 (random)...298GiB/299GiB 99%
shred: /dev/sdX_fake: pass 1/1 (random)...299GiB/299GiB 100%
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
