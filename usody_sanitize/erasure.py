import asyncio
import logging
import sys
from enum import Enum
from typing import List, Union, Optional

from usody_sanitize import schemas, commands
from usody_sanitize.methods import (
    BASIC,
    BASELINE,
    ENHANCED,
)
from usody_sanitize.sanitize import ErasureProcess

logger = logging.getLogger(__name__)


class DefaultMethods(Enum):
    """To easily convert strings to the method pre-defined. Used
    when calling to the sanitizing with string instead with method class.
    """
    BASIC = BASIC
    BASELINE = BASELINE
    ENHANCED = ENHANCED


async def auto_erase_disks(
        method: Optional[Union[schemas.Method, str]] = None,
        disks: Optional[List[str]] = None,
        confirm: bool = False,
) -> Optional[List[dict]]:
    """A main point to erase all disks unless disks mounted at root "/"
    then generates a certificate as JSON with all the information of
    the disk, erasure and the validation of the successful data wiped.

    :param Optional[str] method: A string to select which pre-defined
        methods to use, basic, baseline or enhanced. If none, Basic will
        be selected.
    :param Optional[List[str]] disks: A list of disks to be erased. If
        none, all disks detected will be erased and sanitized.
    :param bool confirm: Print on terminal disks that are going to be deleted/wiped
        before to proceed to confirm the erasure.

    :return:
    """
    # Define the method to execute on all disks.
    if isinstance(method, str):
        try:
            method = DefaultMethods[method.upper()].value
        except ValueError:
            sys.exit("Sanitize method not valid.")

    elif isinstance(method, schemas.Method):
        logger.debug("Selecting custom method.")

    else:
        # Default method when not set by args.
        method = DefaultMethods.BASIC.value
        logger.debug("Selecting default method.")

    logger.info(f"Using sanitize method '{method.name}'.")

    # Get disks to erase.
    selected_disks = disks or commands.get_disks()
    erasures = [ErasureProcess(d, method) for d in selected_disks]

    # Confirmation before erasure.
    if confirm and erasures:
        # Prints on screen the devices selected to run the sanitized process.
        user_message = "The following devices will be wiped:\n\n - " \
                       f"{'|x1n'.join(str(e) for e in erasures)}" \
                       f"\n\nPress ENTER to confirm or cancel with CTRL+C.\n"
        try:
            input(user_message.replace('|x1n', '\n - '))
        except KeyboardInterrupt:
            sys.exit("Process interrupted by user.")

    # Start the sanitize processes here.
    running_tasks = [asyncio.create_task(erase.run()) for erase in erasures]

    [await task for task in running_tasks]
    logger.debug(f">>> {erasures}")
    return [r.export() for r in erasures]
