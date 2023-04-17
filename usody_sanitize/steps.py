import time
import logging

from usody_sanitize import schemas, commands, utils

logger = logging.getLogger(__name__)


async def erase_ssd_hdparm(dev_path: str) -> schemas.ErasureStep:
    """
    Generates a erasure step for deleting SSD using hdparm.

    :param str dev_path: Path to the device.
    :return: schemas.ErasureStep

    Example:
    >>> erase_ssd_hdparm("/dev/sda")
    """
    step = schemas.ErasureStep(device=dev_path, step=1)
    step.date_init = time.time()

    # Start first command for this step.
    logger.debug(f"{dev_path}: Start command 1.")
    command1 = f"hdparm -I {dev_path}"
    cmd1: schemas.ErasureCommand = await commands \
        .erasure_command(command1)
    cmd1.description = "Verify that the SSD disc is not frozen."

    if utils.find_text("(not[\t ]*frozen)", cmd1.stdout):
        cmd1.success = True
    else:
        cmd1.success = False

    step.commands.append(cmd1)
    logger.debug(f"{dev_path}: Command 1 finished. \n{cmd1}")
    if cmd1.success is False:
        return step

    # Second command for this step.
    logger.debug(f"{dev_path}: Start command 2.")
    command2 = f"hdparm --user-master u --security-set-pass Usody {dev_path}"
    cmd2 = await commands.erasure_command(command2)
    cmd2.description = "Set a temporal password to lock the device."

    cmd2.success = cmd2.return_code == 0

    step.commands.append(cmd2)
    logger.debug(f"{dev_path}: Command 2 finished. \n{cmd2}")
    if cmd2.success is False:
        logger.warning("")
        return step

    # Third command.
    logger.debug(f"{dev_path}: Start command 3.")
    command3 = f"hdparm --user-master --security-erase Usody {dev_path}"
    cmd3 = await commands.erasure_command(command3)
    cmd3.description = "Erase the SSD changing the encryption key."
    cmd3.success = cmd3.return_code == 0 or cmd3.return_code == 22

    step.commands.append(cmd3)
    logger.debug(f"{dev_path}: command 3 finished. \n{cmd3}")
    if cmd3.success is False:
        return step

    # Fourth command.
    logger.debug(f"{dev_path}: Start command 4.")
    command4 = f"hdparm -I {dev_path}"
    cmd4 = await commands.erasure_command(command4)
    cmd4.description = "Check the drive security is set to disabled"
    # There is no problem if the drive is locked. A validation
    # process of the data been erased is more important.
    # if utils.find_text(" *(not *enabled) *", cmd4.output):
    #     cmd4.success = True
    # else:
    #     cmd4.success = False

    # @TODO: Validation step at the end.

    step.commands.append(cmd4)
    logger.debug(f"{dev_path}: Command 4 finished. {cmd4}")

    # Write final values on the step schema.
    step.date_end = time.time()
    step.duration = step.date_end - step.date_init
    step.success = all(cmd.success for cmd in step.commands)

    logger.debug(f"{dev_path}: hdparm erasure step finished.")
    return step


async def erase_hdd_shred(dev_path: str) -> schemas.ErasureStep:
    """Runs erasure step for deleting HDD using shred.

    Shred is a command line utility for securely deleting files, it
    is the program used for the "Basic" erasure method.

    :param str dev_path: Path to the device.
    :return: schemas.ErasureStep

    Example:
    >>> erase_hdd_shred("/dev/sda")
    """
    step = schemas.ErasureStep(device=dev_path, step=1)
    step.date_init = time.time()

    # Define the command to run, with zeros or random.
    command = f"shred --force --verbose --zero --iterations=0 {dev_path}"
    logger.debug(f"{dev_path} command: {command}")

    # Run the command.
    cmd: schemas.ErasureCommand = await commands.erasure_command(
        command=command, process_manager=utils.print_shred_progress)
    cmd.description = "Write zeros to the disk with `shred`."

    # Write final values on the step schema.
    step.commands.append(cmd)
    step.date_end = time.time()
    step.duration = step.date_end - step.date_init
    step.success = all(cmd.success for cmd in step.commands)

    logger.debug(f"{dev_path}: Badblocks erasure step finished.")
    return step


async def erase_hdd_badblocks(dev_path: str) -> schemas.ErasureStep:
    """Runs erasure step for deleting HDD using `badblocks`.

    badblocks will delete the disk writting data into each sector.

    :param str dev_path: Path to the device.
    :return: schemas.ErasureStep

    Example:
    >>> erase_hdd_badblocks("/dev/sda")
    """
    step = schemas.ErasureStep(device=dev_path, step=1)
    step.date_init = time.time()

    # Todo: Add -e argument to add a maximum of badblocks found.
    # Define the command to run, with zeros or random.
    # Argument `-s` provides a progress info that cannot be received,
    #  causing a exception as no new lines are emitted.
    command = f"badblocks -wv -p 1 -t random {dev_path}"
    logger.debug(f"{dev_path} command: {command}")

    # Run the command.
    cmd: schemas.ErasureCommand = await commands.erasure_command(
        command=command, process_manager=utils.print_badblocks_progress)
    cmd.description = "Write random data into the disk with `badblocks`."

    # Write final values on the step schema.
    step.commands.append(cmd)
    step.date_end = time.time()
    step.duration = step.date_end - step.date_init
    step.success = all(cmd.success for cmd in step.commands)

    logger.debug(f"{dev_path}: Command badblocks erasure step finished.")
    return step

