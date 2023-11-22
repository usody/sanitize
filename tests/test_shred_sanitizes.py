import asyncio
import logging

import unittest
from unittest.mock import patch, MagicMock, call

# Import mock data for each kind of disk.
from tests.mock_data import shred_mocks
from usody_sanitize.erasure import auto_erase_disks, DefaultMethods

logger = logging.getLogger(__name__)


class TestShredSanitizes(unittest.TestCase):

    @patch("asyncio.create_subprocess_shell",
           side_effect=shred_mocks.async_run(validation=True))
    @patch("subprocess.run",
           side_effect=shred_mocks.subprocess_run())
    @patch("builtins.input", side_effect=[''])
    def test_default_method(
            self,
            mock_input: MagicMock,
            mock_run: MagicMock,
            mock_async_run: MagicMock,
    ):
        # Do the mocked erasure.
        result = asyncio.run(auto_erase_disks(
            method=DefaultMethods.BASIC.value,
            disks=["/dev/sdX_fake"],
            confirm=True,
        ))

        # Asserts
        for data in result:
            assert data.get('result', False), "Test result is not 'True'"

        self.assertEqual(
            "The following devices will be wiped:"
            "\n\n - [Path: /dev/sdX_fake] [Model: MK3259GSXP]"
            " [Serial: 152D00539000] [Size: 298.1G]\n\n"
            "Press ENTER to confirm or cancel with CTRL+C.\n",
            mock_input.call_args[0][0])

        mock_run.assert_has_calls(
            [
                call(['smartctl', '-aj', '/dev/sdX_fake'],
                     stdout=-1, stderr=-1, timeout=10),
                call(['lsblk', '-JOad', '/dev/sdX_fake'],
                     stdout=-1, stderr=-1, timeout=10)
            ]
        )
        mock_async_run.assert_has_calls(
            [
                call('dd if=/dev/sdX_fake bs=512 count=1 skip=0 | xxd -ps',
                     stdout=-1, stderr=-1),
                call('dd if=/dev/sdX_fake bs=512'
                     ' count=1 skip=69460271 | xxd -ps',
                     stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/sdX_fake bs=512'
                    ' count=1 skip=138920543 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/sdX_fake bs=512'
                    ' count=1 skip=208380815 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/sdX_fake bs=512'
                    ' count=1 skip=277841087 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/sdX_fake bs=512'
                    ' count=1 skip=347301359 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/sdX_fake bs=512'
                    ' count=1 skip=416761631 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/sdX_fake bs=512'
                    ' count=1 skip=486221903 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/sdX_fake bs=512'
                    ' count=1 skip=555682175 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/sdX_fake bs=512'
                    ' count=1 skip=625142447 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/random of=/dev/sdX_fake bs=512 count=1 seek=0',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/random of=/dev/sdX_fake bs=512'
                    ' count=1 seek=69460271',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/random of=/dev/sdX_fake bs=512'
                    ' count=1 seek=138920543',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/random of=/dev/sdX_fake bs=512'
                    ' count=1 seek=208380815',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/random of=/dev/sdX_fake bs=512'
                    ' count=1 seek=277841087',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/random of=/dev/sdX_fake bs=512'
                    ' count=1 seek=347301359',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/random of=/dev/sdX_fake bs=512'
                    ' count=1 seek=416761631',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/random of=/dev/sdX_fake bs=512'
                    ' count=1 seek=486221903',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/random of=/dev/sdX_fake bs=512'
                    ' count=1 seek=555682175',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/random of=/dev/sdX_fake bs=512'
                    ' count=1 seek=625142447',
                    stdout=-1, stderr=-1),
                call('dd if=/dev/sdX_fake bs=512 count=1 skip=0 | xxd -ps',
                     stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/sdX_fake bs=512'
                    ' count=1 skip=69460271 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/sdX_fake bs=512'
                    ' count=1 skip=138920543 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/sdX_fake bs=512'
                    ' count=1 skip=208380815 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/sdX_fake bs=512'
                    ' count=1 skip=277841087 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/sdX_fake bs=512'
                    ' count=1 skip=347301359 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/sdX_fake bs=512'
                    ' count=1 skip=416761631 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/sdX_fake bs=512'
                    ' count=1 skip=486221903 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/sdX_fake bs=512'
                    ' count=1 skip=555682175 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/sdX_fake bs=512'
                    ' count=1 skip=625142447 | xxd -ps',
                    stdout=-1, stderr=-1),
                call('shred --force --verbose --iterations=1 /dev/sdX_fake',
                     stdout=-1, stderr=-1),
                call('dd if=/dev/sdX_fake bs=512 count=1 skip=0 | xxd -ps',
                     stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/sdX_fake bs=512'
                    ' count=1 skip=69460271 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/sdX_fake bs=512'
                    ' count=1 skip=138920543 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/sdX_fake bs=512'
                    ' count=1 skip=208380815 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/sdX_fake bs=512'
                    ' count=1 skip=277841087 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/sdX_fake bs=512'
                    ' count=1 skip=347301359 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/sdX_fake bs=512'
                    ' count=1 skip=416761631 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/sdX_fake bs=512'
                    ' count=1 skip=486221903 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/sdX_fake bs=512'
                    ' count=1 skip=555682175 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/sdX_fake bs=512'
                    ' count=1 skip=625142447 | xxd -ps',
                    stdout=-1, stderr=-1)
            ]
        )
