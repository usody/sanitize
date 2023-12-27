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
    """An enumeration class representing default methods.

    This class defines three default methods: BASIC, BASELINE, and ENHANCED. These methods
    can be used to specify the default behavior in different scenarios.

    Attributes:
        BASIC: Represents the basic default method.
        BASELINE: Represents the baseline default method.
        ENHANCED: Represents the enhanced default method.
    """
    BASIC = BASIC
    BASELINE = BASELINE
    ENHANCED = ENHANCED


async def auto_erase_disks(
        method: Optional[Union[schemas.Method, str]] = None,
        disks: Optional[List[str]] = None,
        confirm: bool = False,
) -> Optional[List[dict]]:
    """
    The `auto_erase_disks` method is used to automatically erase selected disks using a specified sanitizing method.

    Parameters:
    - `method` (Optional[Union[schemas.Method, str]]): The sanitizing method to be used. It can be either a
      `schemas.Method` enum or a string representing the method. Default is `None`.
    - `disks` (Optional[List[str]]): The list of disks to be erased. Default is `None`, which means
      all available disks will be selected.
    - `confirm` (bool): Boolean value indicating whether to confirm the erasure before starting. Default is `False`.

    Returns:
    - `Optional[List[dict]]`: List of dictionaries representing the erasure results. Each dictionary contains
      the exported information of an `ErasureProcess` object.

    Example usage:

    ```python
    erasures = auto_erase_disks(method=schemas.Method.ZEROFILL, disks=['/dev/sda', '/dev/sdb'], confirm=True)
    for erasure in erasures:
        print(erasure)
    ```

    Note:
    - `set_sanitizing_method` is a helper function used to convert the sanitizing method argument to the proper type if
      necessary.
    - `get_disks_to_erase` is a helper function used to determine the list of disks to be erased based on the provided
      `disks` argument or by selecting all available disks if `disks` is
    * `None`.
    - `ErasureProcess` is a class representing the erasure process for a single disk, with methods to start and track
      the progress of the erasure process.
    - `confirm_erasures` is a helper function used to confirm the erasure process if `confirm` argument is `True`.
    - `create_async_tasks` is a helper function used to create asynchronous tasks for each erasure process.
    - `await_tasks` is a helper function used to wait for the completion of all asynchronous tasks.

    """
    # Prepare erasures.
    method = set_sanitize_method(method)
    selected_disks = get_disks_to_erase(disks)
    erasures = [erasure for erasure in (ErasureProcess(d, method) for d in selected_disks) if not erasure.error]
    confirm_erasures(erasures, confirm)  # Do confirmation prompt if needed.

    # Start erasure tasks.
    running_tasks = [asyncio.create_task(erase.run()) for erase in erasures]
    [await task for task in running_tasks]

    # Show erasures' results.
    return [r.export() for r in erasures]


def set_sanitize_method(method: Optional[Union[DefaultMethods, str]]):
    """
    Set the sanitizing method for data processing.

    Args:
        method (Optional[Union[DefaultMethods, str]]): The sanitizing method to use.
            It can be either a predefined method from DefaultMethods enum or a custom method string.
            If None is provided, the default method BASIC will be used.

    Returns:
        The selected sanitizing method.

    Raises:
        ValueError: If the provided method string is not valid.

    """
    if isinstance(method, str):
        try:
            method = DefaultMethods[method.upper()].value
        except ValueError:
            sys.exit("Sanitize method not valid.")
    elif isinstance(method, schemas.Method):
        logger.debug("Selecting custom method.")
    else:
        method = DefaultMethods.BASIC.value
        logger.debug("Selecting default method.")
    logger.info(f"Using sanitize method '{method.name}'.")
    return method


def get_disks_to_erase(disks):
    selected_disks = disks or commands.get_disks()
    logger.debug(f"Disks: {disks}")
    return selected_disks


def confirm_erasures(erasures: List[ErasureProcess], confirm: bool):
    """
    Asks for a user input to confirm the erasure

    Parameters:
        erasures (List[ErasureProcess]): A list of `ErasureProcess` objects representing the devices
            that will be wiped.
        confirm (bool): Indicates whether to confirm the erasures.

    Returns:
        None

    Raises:
        KeyboardInterrupt: If the user cancels the confirmation process by pressing CTRL+C.

    Usage:
        Call this method to display a confirmation message to the user, indicating the devices that
        will be wiped. If the `confirm` parameter is set to True and there are erasures to confirm,
        the method prompts the user to press ENTER to confirm or cancel with CTRL+C. If the user
        cancels the confirmation, the method exits with a status message.

    Example:
        erasure_processes = [ErasureProcess(device="Device1", process="Wipe")]
        confirm_erasures(erasures=erasure_processes, confirm=True)
    """
    if confirm and erasures:
        user_message = "The following devices will be wiped:\n\n - " \
                       f"{'|x1n'.join(str(e) for e in erasures)}" \
                       f"\n\nPress ENTER to confirm or cancel with CTRL+C.\n"
        try:
            input(user_message.replace('|x1n', '\n - '))
        except KeyboardInterrupt:
            sys.exit("Process interrupted by user.")
