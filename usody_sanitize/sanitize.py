import json
import logging
import sys
from pathlib import Path
from typing import Union, Optional

from usody_sanitize import schemas, steps, commands, utils
from usody_sanitize.methods import (
    BASIC,
    CRYPTOGRAPHIC_ATA,  # SSD
    CRYPTOGRAPHIC_NVME,  # M.2
)

logger = logging.getLogger(__name__)


class ErasureProcess:
    def __init__(
            self,
            dev_path: Union[str, Path],
            method: schemas.Method,
    ):
        self.path: Path = Path(dev_path.as_posix())
        logger.info(f"Selected device `{self.path}` for sanitization.")

        # Init disk schema.
        self._device = schemas.Device(
            # Export data from disk.
            export_data=schemas.ExportData(
                smart=commands.get_smart_info(self.path.as_posix()),
                block=commands.get_lsblk_info(self.path.as_posix()),
            )
        )

        self._sanitize = schemas.Sanitize(
            device_info=self._device,
            validation=schemas.SanitizeValidation(),
        )
        # --> HERE SET THE DEFAULT ERASURE METHOD <--
        self._sanitize.method = BASIC if method is None else method
        self._extract_device_info()

    def __str__(self):
        return f"[Path: {self.blk.path}]" \
               f" [Model: {self._device.model}]" \
               f" [Serial: {self._device.serial_number}]" \
               f" [Size: {self._device.size}]"

    @property
    def blk(self) -> Optional[schemas.Block]:
        return self._device.export_data.block

    @property
    def smart(self) -> Optional[schemas.Smart]:
        return self._device.export_data.smart

    def export(self) -> dict:
        return self._sanitize.dict()

    def _extract_device_info(self):
        """Extract the data from the disk and process it to get the
        main values and disk type before running the erasure.

        Here we will run the smartmontools and lsblk to get the device
        info.

        :return:
        """
        # Extract the important data.
        self._device.manufacturer = self.blk.vendor or self.smart.model_family
        self._device.model = self.blk.model or self.smart.model_name
        self._device.serial_number = self.blk.serial \
                                     or self.smart.serial_number
        self._device.connector = self.blk.subsystems
        self._device.size = self.blk.size

        # Check if the device is SSD or HDD.
        if self.smart.rotation_rate is None:
            # Set the value from `lsblk` instead smart when smart is None.
            self._device.storage_medium = "HDD" if self.blk.rota else "SSD"

        elif self.smart.rotation_rate == 0:  # Is SSD.
            if self.blk.rota == 1:  # `lsblk` says is a HDD.
                logger.debug("SSD \n\t"
                             f"`lsblk` rotate = {self.blk.rota}\n\t"
                             "`smartctl` rotation_rate"
                             f" = {self.smart.rotation_rate}")

            self._device.storage_medium = "SSD"

        else:
            self._device.storage_medium = "HDD"

        logger.debug(f"{self.path}: Information extracted.")

    async def run(self):
        logger.debug(f"{self.blk.path}: Running sanitize process.")

        if self._sanitize.method.verification_enabled:
            # Pre validation steps before erasure.
            await self._pre_validation()

            logger.debug(self._sanitize.validation)
            # noinspection PySimplifyBooleanCheck
            if not self._sanitize.validation.result:
                logger.warning(
                    f"{self.blk.path}: Validation failed. Stopping process.")
                return

        if self._sanitize.device_info.storage_medium == 'HDD':
            logger.info(f"{self.blk}: Detected as HDD.")

        elif self._sanitize.device_info.storage_medium == 'SSD':
            # Overwriting erasures damages the disk.

            if self.blk.path.startswith("/dev/nvme"):
                # M.2 needs to use another command for PCIe interface.
                # Todo: Keep the validation method before changing the method.
                self._sanitize.method = CRYPTOGRAPHIC_NVME
                logger.info(f"{self.blk}: Detected as NVME.")
            else:
                # SSD can be erased via ATA interface.
                # Todo: Keep the validation method before changing the method.
                self._sanitize.method = CRYPTOGRAPHIC_ATA
                logger.info(f"{self.blk}: Detected as SSD.")

        else:
            # Todo: Research about SSDHD types.
            raise Exception("Unknown method.")

        # Now run the method execution steps.
        await self._run_erase_steps()

        # If validation was enabled, finish the validation.
        if self._sanitize.method.verification_enabled:
            await self._validation()

        # The result depends on the validation
        if self._sanitize.method.verification_enabled:
            self._sanitize.result = self._sanitize.validation.result
        elif self._sanitize.steps:
            # IF validation is disabled, just check the erase command.
            self._sanitize.result = self._sanitize.steps[-1].success
        else:
            # If there are no steps and neither validation,
            # there is no erasure.
            self._sanitize.result = False

        # Show info when the erasure is done.
        logger.debug(f"{self.blk.path}: Erasure finished, results:"
                     f" {json.dumps(self._sanitize.dict(), indent=4)}")

    async def _pre_validation(self):
        """Check if the disk is not mounted and if it is not a
        read-only device.

        :return:
        """
        if self.blk.phy_sec != self.smart.logical_block_size:
            sys.exit("Information missmatch, can not continue.")

        bs = self.smart.logical_block_size
        max_sector = self.smart.user_capacity.bytes // bs
        sectors = utils.get_spaced_numbers(max_sector, 10)

        def _successful_command(
                _cmd: schemas.Exec,
        ):
            self._sanitize.validation.commands.append(_cmd)
            if _cmd.return_code != 0:
                _cmd.success = False
                # Todo: Clean only the data from sectors.
                self._sanitize.validation.data = {}
                logger.warning(f"{self.blk.path}:"
                               f" Validation step {_cmd.command} failed.")
                return False
            return True

        for s in sectors:
            # First command.
            cmd1 = await commands.read_from_sector(self.blk.path, s, bs)
            cmd1.description = f"Read data from sector {s} to validate" \
                               " if have been changed."
            if not _successful_command(cmd1):
                self._sanitize.validation.result = False
                return
            self._sanitize.validation.data[s] = cmd1.stdout
            cmd1.stdout = "Private"

        for s in sectors:
            # Second command.
            cmd2 = await commands.write_to_sector(self.blk.path, s, bs)
            cmd2.description = "Write the data to validate into the sectors"
            if not _successful_command(cmd2):
                self._sanitize.validation.result = False
                return

        for s in sectors:
            # Third command.
            cmd3 = await commands.read_from_sector(self.blk.path, s, bs)
            cmd3.description = "Check if new bytes has been written"
            if not _successful_command(cmd3):
                self._sanitize.validation.result = False
                return

            elif self._sanitize.validation.data[s] == cmd3.stdout:
                logger.warning(
                    f"{self.blk.path}:"
                    f" Validation failed: Sector {s} has not been changed")
                self._sanitize.validation.result = False
                return
            # Successfully written, update the sector with the new value.
            self._sanitize.validation.data[s] = cmd3.stdout

        self._sanitize.validation.result = True
        logger.debug(f"{self.blk.path}: Pre validation step finished.")

    async def _validation(self):
        """
        :return:
        """
        for sector in self._sanitize.validation.data:
            cmd = await commands.read_from_sector(
                self.blk.path, sector, self.smart.logical_block_size)

            if cmd.stdout == self._sanitize.validation.data[sector]:
                self._sanitize.validation.result = False
                logger.warning(f"{self.blk.path}: Erasure validation failed.")
                return

        self._sanitize.validation.result = True
        logger.debug(f"Validation passed.")

    async def _run_erase_steps(self):
        """Runs the commands described on the overwriting_steps of the
        current method. Automatically runs them in the same order.
        """
        for execution in self._sanitize.method.overwriting_steps:
            logger.debug(f"{self.blk.path}: Running new step: {execution}")
            if execution.tool == 'shred':
                step = await steps.erase_hdd_shred(
                    self.blk.path, pattern=execution.pattern)
                self._sanitize.steps.append(step)
            elif execution.tool == 'badblocks':
                step = await steps.erase_hdd_badblocks(
                    self.blk.path, pattern=execution.pattern)
                self._sanitize.steps.append(step)
            elif execution.tool == 'nvme':
                step = await steps.erase_nvme_nvmecli(self.blk.path)
                self._sanitize.steps.append(step)
            elif execution.tool == 'hdparm':
                step = await steps.erase_ssd_hdparm(self.blk.path)
                self._sanitize.steps.append(step)

        logger.debug(f"{self.blk.path}: Erasure steps finished.")
