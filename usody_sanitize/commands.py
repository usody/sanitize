import json
import time
import asyncio
import logging
import subprocess

from typing import Optional, List, Any
from usody_sanitize import schemas

logger = logging.getLogger(__name__)


async def list_blocks(
        dev_path: Optional[str] = None,
        children: bool = False,
) -> List[schemas.Block]:
    """Runs the command `lsblk` to get the information about devices.

    Used maily to detect USB, live USB or disk attached.

    :param Optional[str] dev_path:
    :param bool children: Get partitions of each device.

    :return:
    """
    command = ["lsblk", "-JOa" if children else "-JOad"]
    logger.debug(f"Running command: `{command}`")
    if dev_path:
        command += [dev_path]
    output_text = subprocess.check_output(command, text=True)

    logger.debug(f"Processing `{command}` output.")
    devices_json = json.loads(output_text.strip()).get("blockdevices", [])
    return [schemas.Block.parse_obj(dev) for dev in devices_json]


async def get_smart_info(dev_path: str) -> schemas.Smart:
    """Gets the information of the device with the `smartctl` command.

    Used to detect when a disk is SSD or HDD correctly, as lsblk don't
    detect this value correctly.

    :param str dev_path:
    :return:
    """
    command = ["smartctl", "-aj", dev_path]
    proc = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await proc.wait()
    output = await proc.stdout.read()
    smart_json = json.loads(output.decode('UTF-8').rstrip())
    logger.debug(f"Smart for {dev_path} is: {smart_json}")
    return schemas.Smart.parse_obj(smart_json)


async def get_total_sectors(dev_path: str) -> int:
    """Get the total
    """
    command = ["blockdev", "--getsz", dev_path]
    proc = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await proc.wait()
    if proc.returncode:
        raise Exception(f"Can not get total disk sectors from {dev_path}")
    return int(await proc.stdout.read())


async def erasure_command(
        command: str,
        process_manager: Optional[Any] = None,
) -> schemas.ErasureCommand:
    """Runs the command given, but it returns a `schemas.ErasureCommand`
    object with the processed data.

    :param List[str] command: Command string to be executed like a shell
        on the system.
    :param process_manager: Async function to allow to manipulate the
        command process while still running.

    :return:
    """
    if isinstance(command, list):
        command = ' '.join(command)

    cmd = schemas.ErasureCommand(command=command, start_time=time.time())
    proc = await asyncio.create_subprocess_shell(
        # "timeout 30 " +
        cmd.command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    if process_manager:
        await process_manager(cmd, proc)

    # await proc.communicate()
    await proc.wait()
    cmd.end_time = time.time()

    if cmd.stdout is None:
        stdout = await proc.stdout.read()
        cmd.stdout = stdout.decode('UTF-8').rstrip()

    if cmd.stderr is None:
        stderr = await proc.stderr.read()
        cmd.stderr = stderr.decode('UTF-8').rstrip()

    cmd.return_code = proc.returncode
    cmd.success = proc.returncode == 0

    return cmd


async def read_from_sector(
        path_to_dev: str,
        sector: int,
        bs: int = 512,
) -> schemas.ErasureCommand:
    """Read the X bytes (bs) from a disk sector.

    :param str path_to_dev: Path to the device. Example: `/dev/sda`
    :param int sector: Sector to read on the disk.
    :param int bs: Sector sizes, by default 512 bytes.

    :return: schemas.ErasureCommand
    """
    read_command = f"dd if={path_to_dev} bs={bs} count=1 skip={sector}" \
                   " | xxd -ps"
    logger.debug(f"{path_to_dev}: Read data on sector {sector}.")
    return await erasure_command(read_command)


async def write_to_sector(
        path_to_dev: str,
        sector: int,
        bs: int = 512,
        zeros: bool = False,
) -> schemas.ErasureCommand:
    """Write X bytes (bs size must be provided) to the disk sector.

    :param str path_to_dev: Path to the device. Example: `/dev/sda`
    :param int sector: Sector to read.
    :param int bs: Sector sizes, by default 512 bytes.
    :param bool zeros: The pattern desired to use.

    :return: schemas.ErasureCommand
    """
    write_command = f"dd if={'/dev/zero' if zeros else '/dev/random'}"\
                    f" of=/dev/sda bs={bs} count=1 seek={sector}"
    logger.debug(
        f"Writing {'zeros' if zeros else 'random'} data into {path_to_dev}.")
    return await erasure_command(write_command)
