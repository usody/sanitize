import re
import asyncio
import logging

from typing import Optional
from usody_sanitize import schemas

logger = logging.getLogger(__name__)


def get_spaced_numbers(max_num: int, items: int):
    """
    ```python
    step = (100000 - 0) / (6 - 1)
    numbers = [i * step for i in range(6)]
    ```

    :param max_num:
    :param items:
    :return:
    """
    step = (max_num - 1) / (items - 1)
    return [int(i * step) for i in range(items)]


async def print_shred_progress(
        cmd: schemas.ErasureCommand,
        process: asyncio.subprocess.Process
):
    """Example how to process `shred` output."""
    async for line in process.stderr:
        logger.debug(f"{cmd.command}: {line}")


async def print_badblocks_progress(
        cmd: schemas.ErasureCommand,
        process: asyncio.subprocess.Process
):
    """Example how to process `badblocks` output."""
    async for line in process.stderr:
        clean_line = line.decode('UTF-8').replace('\b', '').replace('\n', '')
        logger.debug(f"{cmd.command}: {clean_line}")

    logger.debug("OUT")


def find_text(re_expression: str, string: str) -> Optional[str]:
    """Searches for a regular expression in a string and returns the
    first match. Used to find text in the output of the commands.

    :param str re_expression:
    :param str string:
    :return:

    Example:
    >>> find_text("([0-9]+)", "123")
    """
    text = re.search(re_expression, string)
    if text:
        return text.groups()[0]
