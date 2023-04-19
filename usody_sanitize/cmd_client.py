import sys
import json
import logging
import asyncio
import argparse

try:
    from usody_sanitize.erasure import DefaultMethods, auto_erase_disks
except ModuleNotFoundError:
    import pathlib
    sys.path.append(
        pathlib.Path(__file__).parent.parent.absolute().as_posix()
    )
    from usody_sanitize.erasure import DefaultMethods, auto_erase_disks

from usody_sanitize import __version__ as app_version


logging.getLogger("CMD")


def run_cmd():
    args = parse_args()
    configure_loggers(args.log_level)

    # Run erasures.
    result = run_coroutine(auto_erase_disks(args.method, args.device))

    # Todo: Add function to handle the result exports.
    logging.debug(json.dumps(result, indent=4))
    with open('/tmp/erasure_output.json', 'w') as _fh:
        json.dump(result, _fh, indent=4)


def configure_loggers(level="INFO"):
    logging.basicConfig(
        force=True,
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(levelname)s: %(message)s"
    )


def run_coroutine(coro):
    """Forces to run the function in a new async loop."""
    loop = asyncio.new_event_loop()

    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def parse_args():
    parser = argparse.ArgumentParser(description='sanitize a disk')
    parser.add_argument('-m', '--method', type=str,
                        help='sanitize method')

    # Select the
    disk = parser.add_mutually_exclusive_group(required=True)
    disk.add_argument('-d', '--device', type=str, action='append',
                      help='path to the /dev/{disk} E.G.: /dev/sda')
    disk.add_argument('-a', '--all', action='store_true',
                      help='all disks unless the disk mounted as root')

    parser.add_argument('--version', action='version', version=app_version,
                        help='show the version of usody_sanitize')

    parser.add_argument('-l', '--log-level', dest='log_level', default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR',
                                 'CRITICAL'],
                        help='set the logging level (default: %(default)s)')

    # Todo: Add output/export option.

    return parser.parse_args()


if __name__ == '__main__':
    run_cmd()
