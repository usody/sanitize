import sys
import json
import logging
import asyncio

from enum import Enum

from typing import List, Union, Optional
from usody_sanitize import schemas, commands, steps, utils, __version__
from usody_sanitize.methods import (
    BASIC,
    BASELINE,
    ENHANCED,
    CRYPTOGRAPHIC,
)

logger = logging.getLogger(__name__)


class DefaultMethods(Enum):
    """To easily convert strings to the method pre-defined. Used
    when calling to the sanitize with string instead with method class.
    """
    BASIC = BASIC
    BASELINE = BASELINE
    ENHANCED = ENHANCED


async def auto_erase_disks(
        method: Optional[str] = None,
        disks: Optional[List[str]] = None,
) -> Optional[List[dict]]:
    """A main point to erase all disks unless disks mounted at root "/"
    then generates a certificate as JSON with all the information of
    the disk, erasure and the validation of the successful data wiped.

    :param Optional[str] method: A string to select which pre-defined
        methods to use, basic, baseline or enhanced. If none, Basic will
        be selected.
    :param Optional[List[str]] disks: A list of disks to be erased. If
        none, all disks detected will be erased and sanitized.

    :return:
    """
    # Select method.
    if method:
        try:
            method = DefaultMethods[method.upper()].value
        except ValueError:
            sys.exit("Sanitize method not valid.")
    else:
        # Default method when not set by args.
        method = DefaultMethods.BASIC.value
    logger.info(f"Using sanitize method '{method.name}'.")

    # Get disks.
    blocks: List[schemas.Block] = await commands.list_blocks(children=True)
    erasures: List[ErasureProcess] = []
    tasks: List[asyncio.Task] = []

    for blk in blocks:

        if blk.type != "disk":
            logger.debug(f"Skipping {blk.path}")
            continue  # Skip non disk volumes.

        if disks is not None:
            if blk.path in disks:
                disks.remove(blk.path)
            else:
                continue

        # Detect if one of those drives has a mounted partition as root.
        if blk.children:

            if any([cld.mountpoint == "/" for cld in blk.children
                    if cld.mountpoint is not None]):
                logger.warning(f"Skipping disk {blk.path} mounted as root.")
                continue

        logger.debug(f"Processing disk {blk.path}.")
        erasure = ErasureProcess(blk, method)
        erasures.append(erasure)

        # Start erasure task.
        tasks.append(asyncio.create_task(erasure.run()))

    if disks:
        logger.warning(f"Disks [{', '.join(disks)}] not found.")

    [await task for task in tasks]
    logger.debug(f">>> {erasures}")
    return [r.export() for r in erasures]


class ErasureProcess:
    def __init__(
            self,
            block: schemas.Block,
            method: Union[schemas.ErasureMethod, str] = None
    ):
        if isinstance(method, str):
            # Todo: convert to schema.
            pass

        logger.info(f"Selected device {block.path} for sanitization.")
        self._device = schemas.Device(
            export_data=schemas.ExportData(
                block=block,  # Data from `lsblk`
            )
        )
        validation = schemas.ErasureValidation()
        self._certificate = schemas.ErasureCertificate(
            device_info=self._device,
            validation=validation,
            usody_sanitize=__version__
        )
        # --> HERE SELECT THE DEFAULT ERASURE METHOD <--
        self._certificate.method = BASIC if method is None else method

    @property
    def blk(self) -> Optional[schemas.Block]:
        return self._device.export_data.block

    @property
    def smart(self) -> Optional[schemas.Smart]:
        return self._device.export_data.smart

    def export(self) -> dict:
        return self._certificate.dict()

    async def extract_device_info(self):
        """Get the basic info from the `lsblk` command and store it
        into the device schema. As the name of the function says,

        :return:
        """
        # Check if the device is SSD or HDD.
        if self.smart.rotation_rate == 0:  # Is SSD.
            if self.blk.rota == 1:  # `lsblk` says is a HDD.
                logger.debug("SSD \n\t"
                             f"`lsblk` rotate = {self.blk.rota}\n\t"
                             "`smartctl` rotation_rate"
                             f" = {self.smart.rotation_rate}")

            self._device.storage_medium = "SSD"

        else:
            self._device.storage_medium = "HDD"

        logger.debug(f"Device {self.blk.path} has been validated.")

    async def run(self):
        # Do `smartctl` here
        self._device.export_data.smart = await commands \
            .get_smart_info(self.blk.path)

        # Extract device info from `lsblk` and `smartctl`.
        await self.extract_device_info()

        logger.debug(f"Erasure process for {self.blk.path} started.")

        if self._certificate.method.verification_enabled:
            # Pre validation steps before erasure.
            await self._pre_validation()

        if self._certificate.device_info.storage_medium == 'HDD':
            # If rotates, means it has magnetic disks.
            logger.info(f"Device {self.blk.path} is a HDD")
            logger.debug(f"Data of the device: {self.blk}")
            await self._erase_hdd()

        elif self._certificate.device_info.storage_medium == 'SSD':
            logger.info(f"Device {self.blk.path} is an SSD")
            logger.debug(f"Data of the device: {self.blk}")
            await self._erase_ssd()
        else:
            # Todo: Research about SSDHD types.
            raise Exception("Unknown method for SSDHD")

        if self._certificate.method.verification_enabled:
            # Validation step after erasure.
            await self._validation()

        # The result depends on the validation
        if self._certificate.method.verification_enabled:
            self._certificate.result = self._certificate.validation.result
        elif self._certificate.erasure_steps:
            # IF validation is disabled, just check the erase command.
            self._certificate.result = self._certificate \
                .erasure_steps[-1].success
        else:
            # If there is no steps and neither validation,
            # there is no erasure.
            self._certificate.result = False

        # Show info when the erasure is done.
        logger.debug(f"{self.blk.path}: Erasure finished, results:"
                     f" {json.dumps(self._certificate.dict(), indent=4)}")

    async def _pre_validation(self):
        """Check if the disk is not mounted and if it is not a
        read-only device.

        :return:
        """
        bs = self.smart.logical_block_size
        max_sectors = await commands.get_total_sectors(self.blk.path)
        sectors = utils.get_spaced_numbers(max_sectors, 10)

        def _successful_command(
                _cmd: schemas.ErasureCommand,
        ):
            self._certificate.validation.commands.append(_cmd)
            if _cmd.return_code != 0:
                _cmd.success = False
                # Todo: Clean only the data from sectors.
                self._certificate.validation.data = {}
                logger.warning(f"Validation step {_cmd.command} failed.")
                return False
            return True

        for s in sectors:
            # First command.
            cmd1 = await commands.read_from_sector(self.blk.path, s, bs)
            cmd1.description = f"Read data from sector {s} to validate" \
                               " if have been changed."
            if not _successful_command(cmd1):
                return False
            self._certificate.validation.data[s] = cmd1.stdout
            cmd1.stdout = "Private"

        for s in sectors:
            # Second command.
            cmd2 = await commands.write_to_sector(self.blk.path, s, bs)
            cmd2.description = "Write the data to validate into the sectors"
            if not _successful_command(cmd2):
                return False

        for s in sectors:
            # Third command.
            cmd3 = await commands.read_from_sector(self.blk.path, s, bs)
            cmd3.description = "Check if new bytes has been written"
            if not _successful_command(cmd3):
                return False

            elif self._certificate.validation.data[s] == cmd3.stdout:
                logger.warning(
                    f"{self.blk.path}: "
                    f"Validation failed: Sector {s} has not been changed")
                return False
            # Successful write, update the sector with new value.
            self._certificate.validation.data[s] = cmd3.stdout

        logger.debug(f"{self.blk.path}: Pre validation step finished.")
        return True

    async def _validation(self):
        """
        :return:
        """
        for sector in self._certificate.validation.data:
            cmd = await commands.read_from_sector(
                self.blk.path, sector, self.smart.logical_block_size)

            if cmd.stdout == self._certificate.validation.data[sector]:
                self._certificate.validation.result = False
                logger.warning(f"{self.blk.path}: Erasure validation failed.")
                return

        self._certificate.validation.result = True
        logger.debug(f"Validation passed.")

    async def _erase_hdd(self):
        """Reads the erasure method name for the erasure and calls the
        right method with the right arguments to automatically erase
        the disk as defined.
        :return:
        """
        # @TODO: create a pre step for validation, first format
        #   the drive and create some content to be deleted latter.
        #   OR use dd to write a few bytes to the disk and check if
        #   they are still there after the erasure.

        current_method = self._certificate.method.program

        logger.debug(f"Using '{current_method}' for `{self.blk.path}`.")
        # Todo: Run the erasure as many steps as defined in the method.
        for n in range(self._certificate.method.overwriting_steps):
            # Erasure steps.
            if current_method == 'shred':
                step = await steps.erase_hdd_shred(self.blk.path)
                self._certificate.erasure_steps.append(step)
            elif current_method == 'badblocks':
                step = await steps.erase_hdd_badblocks(self.blk.path)
                self._certificate.erasure_steps.append(step)
            else:
                logger.error(
                    f"'{self._certificate.method.program}' not implemented.")

    async def _erase_ssd(self):
        """To erase an SSD, the only method allowed right now is the
        Baseline Cryptographic, so the method will be overwritten.
        :return:
        """
        # SSD can only be erased with method Cryptographic. Overwriting
        # erasures damages the disk.
        self._certificate.method = CRYPTOGRAPHIC

        # Create the step schema and set initial values.
        logger.debug(f"Starting erasure step for {self.blk} as SSD.")
        self._certificate.erasure_steps.append(
            await steps.erase_ssd_hdparm(self.blk.path),
        )
