import asyncio
import logging
import functools

import unittest
from unittest.mock import patch, MagicMock

# Import mock data for each kind of disk.
from mock_data import (
    nvme_mocks,
)


from usody_sanitize.erasure import auto_erase_disks, DefaultMethods


logger = logging.getLogger(__name__)


class TestSanitizes(unittest.TestCase):

    @patch("asyncio.create_subprocess_shell")
    @patch("subprocess.run")
    def test_nvme_method(
            self,
            mock_run: MagicMock,
            mock_async_run: MagicMock
    ):
        mock_run.side_effect = nvme_mocks.subprocess_run()
        mock_async_run.side_effect = nvme_mocks.async_run(validation=True)

        # Call the function that uses `create_subprocess_shell`.
        result = asyncio.run(auto_erase_disks(
            method=DefaultMethods.BASIC.value,
            disks=["/dev/nvme0nX_fake"],
            confirm=False,
        ))

        for data in result:
            assert data.get('result', False), "Test result is not 'True'"


if __name__ == '__main__':
    unittest.main()
