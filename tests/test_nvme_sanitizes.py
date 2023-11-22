import asyncio
import logging

import unittest
from unittest.mock import patch, MagicMock, call

# Import mock data for each kind of disk.
from tests.mock_data import nvme_mocks
from usody_sanitize.erasure import auto_erase_disks, DefaultMethods

logger = logging.getLogger(__name__)


class TestNVMESanitizes(unittest.TestCase):
    """Only to test NVMe erasures. The command `nvme`.
    """

    @patch("asyncio.create_subprocess_shell",
           side_effect=nvme_mocks.async_run(
               validation=True,

           ))
    @patch("subprocess.run",
           side_effect=nvme_mocks.subprocess_run())
    @patch("builtins.input", side_effect=[''])
    def test_with_validation(
            self,
            mock_input: MagicMock,
            mock_run: MagicMock,
            mock_async_run: MagicMock,
    ):
        # Do the mocked erasure.
        result = asyncio.run(auto_erase_disks(
            method=DefaultMethods.BASIC.value,
            disks=["/dev/nvme0nX_fake"],
            confirm=True,
        ))

        # Asserts
        for data in result:
            assert data.get('result', False), "Test result is not 'True'"

        assert mock_input.call_args[0][0], \
            "The following devices will be wiped:\n\n" \
            " - [Path: /dev/nvme0nX_fake] [Model: Samsung SSD" \
            " 960 PRO 512GB] [Serial: S3EWNX0K216135N]" \
            " [Size: 476.9G]\n\nPress ENTER to confirm" \
            " or cancel with CTRL+C.\n"

        assert mock_run.call_args[0], \
            ['lsblk', '-JOad', '/dev/nvme0nX_fake']
        assert mock_async_run.call_args[0][0], \
            'nvme format --ses=1 /dev/nvme0nX_fake'

    @patch("asyncio.create_subprocess_shell",
           side_effect=nvme_mocks.async_run(
               validation=True,

           ))
    @patch("subprocess.run",
           side_effect=nvme_mocks.subprocess_run())
    @patch("builtins.input", side_effect=[''])
    def test_no_validation(
            self,
            mock_input: MagicMock,
            mock_run: MagicMock,
            mock_async_run: MagicMock,
    ):
        # Do the mocked erasure.
        result = asyncio.run(auto_erase_disks(
            method=DefaultMethods.BASIC.value,
            disks=["/dev/nvme0nX_fake"],
            confirm=True,
        ))

        # Asserts
        for data in result:
            assert data.get('result', False), "Test result is not 'True'"

        self.assertEqual(
            "The following devices will be wiped:\n\n"
            " - [Path: /dev/nvme0nX_fake] [Model: Samsung SSD"
            " 960 PRO 512GB] [Serial: S3EWNX0K216135N] [Size: 476.9G]"
            "\n\nPress ENTER to confirm or cancel with CTRL+C.\n",
            mock_input.call_args[0][0])

        mock_run.assert_has_calls(
            [
                call(['smartctl', '-aj', '/dev/nvme0nX_fake'],
                     stdout=-1, stderr=-1, timeout=10),
                call(['lsblk', '-JOad', '/dev/nvme0nX_fake'],
                     stdout=-1, stderr=-1, timeout=10)
            ]
        )
        mock_async_run.assert_has_calls(
            [
                call('dd if=/dev/nvme0nX_fake bs=512 count=1 skip=0 | xxd -ps',
                     stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/nvme0nX_fake bs=512'
                    ' count=1 skip=111135023 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/nvme0nX_fake bs=512'
                    ' count=1 skip=222270047 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/nvme0nX_fake bs=512'
                    ' count=1 skip=333405071 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/nvme0nX_fake bs=512'
                    ' count=1 skip=444540095 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/nvme0nX_fake bs=512'
                    ' count=1 skip=555675119 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/nvme0nX_fake bs=512'
                    ' count=1 skip=666810143 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/nvme0nX_fake bs=512'
                    ' count=1 skip=777945167 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/nvme0nX_fake bs=512'
                    ' count=1 skip=889080191 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/nvme0nX_fake bs=512'
                    ' count=1 skip=1000215215 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/random of=/dev/nvme0nX_fake bs=512'
                    ' count=1 seek=0',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/random of=/dev/nvme0nX_fake bs=512'
                    ' count=1 seek=111135023',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/random of=/dev/nvme0nX_fake bs=512'
                    ' count=1 seek=222270047',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/random of=/dev/nvme0nX_fake bs=512'
                    ' count=1 seek=333405071',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/random of=/dev/nvme0nX_fake bs=512'
                    ' count=1 seek=444540095',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/random of=/dev/nvme0nX_fake bs=512'
                    ' count=1 seek=555675119',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/random of=/dev/nvme0nX_fake bs=512'
                    ' count=1 seek=666810143',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/random of=/dev/nvme0nX_fake bs=512'
                    ' count=1 seek=777945167',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/random of=/dev/nvme0nX_fake bs=512'
                    ' count=1 seek=889080191',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/random of=/dev/nvme0nX_fake bs=512'
                    ' count=1 seek=1000215215',
                    stdout=-1, stderr=-1),
                call('dd if=/dev/nvme0nX_fake bs=512 count=1 skip=0 | xxd -ps',
                     stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/nvme0nX_fake bs=512'
                    ' count=1 skip=111135023 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/nvme0nX_fake bs=512'
                    ' count=1 skip=222270047 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/nvme0nX_fake bs=512'
                    ' count=1 skip=333405071 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/nvme0nX_fake bs=512'
                    ' count=1 skip=444540095 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/nvme0nX_fake bs=512'
                    ' count=1 skip=555675119 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/nvme0nX_fake bs=512'
                    ' count=1 skip=666810143 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/nvme0nX_fake bs=512'
                    ' count=1 skip=777945167 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/nvme0nX_fake bs=512'
                    ' count=1 skip=889080191 | xxd -ps',
                    stdout=-1, stderr=-1),
                call(
                    'dd if=/dev/nvme0nX_fake bs=512'
                    ' count=1 skip=1000215215 | xxd -ps',
                    stdout=-1, stderr=-1),
                call('nvme format --ses=1 /dev/nvme0nX_fake', stdout=-1,
                     stderr=-1)
            ]
        )
