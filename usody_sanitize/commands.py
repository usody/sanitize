import asyncio
import json
import logging
import subprocess
import time
from pathlib import Path
from typing import Optional, List, Any

from usody_sanitize import schemas

logger = logging.getLogger(__name__)


def get_disks():
    """Simple way to get the disks that we support. """
    return [p for p in Path('/dev').glob('sd?')] + \
        [p for p in Path('/dev').glob('nvme?n?')]


async def erasure_command(
        command: str,
        process_manager: Optional[Any] = None,
) -> schemas.Exec:
    """Runs the command given, but it returns a `schemas.Exec`
    object with the command executed details.

    :param List[str] command: Command string to be executed like a shell
        on the system.
    :param process_manager: Async function to allow manipulating the
        command process while it is still running.

    :return:
    """
    if isinstance(command, list):
        command = ' '.join(command)

    cmd = schemas.Exec(command=command)
    proc = await asyncio.create_subprocess_shell(
        cmd.command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    if process_manager:
        await process_manager(cmd, proc)

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
) -> schemas.Exec:
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
        dev_path: str,
        sector: int,
        bs: int = 512,
        zeros: bool = False,
) -> schemas.Exec:
    """Write X bytes (bs size must be provided) to the disk sector.

    :param str dev_path: Path to the device. Example: `/dev/sda`
    :param int sector: Sector to read.
    :param int bs: Sector sizes, by default 512 bytes.
    :param bool zeros: The pattern desired to use.

    :return: schemas.ErasureCommand
    """
    write_command = f"dd if={'/dev/zero' if zeros else '/dev/random'}" \
                    f" of=/dev/sda bs={bs} count=1 seek={sector}"
    logger.debug(
        f"{dev_path}: Writing {'zeros' if zeros else 'random'}"
        f" data on sector {sector}.")
    return await erasure_command(write_command)


def get_smart_info(dev_path):
    """
    Get SMART information for a device using smartctl.

    Args:
        dev_path (str): Path to device

    Returns:
        dict: JSON output from smartctl
    """

    # Build command
    command = ["smartctl", "-aj", dev_path]

    # Run command
    proc = subprocess.run(command, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)

    # Parse output
    smart_json = json.loads(proc.stdout.decode('utf-8').rstrip())

    # Print and return result
    print(f"SMART for {dev_path} is: {smart_json}")
    return smart_json


def get_lsblk_info(dev_path):
    """
    Get device information using lsblk.

    Args:
        dev_path (str): Path to device

    Returns:
        dict: Device information from lsblk
    """

    # Build command
    command = ["lsblk", "-JOad", dev_path]

    # Run command
    proc = subprocess.run(command, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)

    # Parse output
    device_info = json.loads(proc.stdout.strip()).get("blockdevices", [])[0]

    # Print and return result
    print(f"{dev_path}: `lsblk` is -> {device_info}")
    return device_info
