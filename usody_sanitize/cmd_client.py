import argparse
import asyncio
import datetime
import json
import logging
import pathlib
import sys

try:
    from usody_sanitize.erasure import DefaultMethods, auto_erase_disks
except ModuleNotFoundError:
    sys.path.append(
        pathlib.Path(__file__).parent.parent.absolute().as_posix()
    )
    from usody_sanitize.erasure import DefaultMethods, auto_erase_disks

from usody_sanitize import __version__ as app_version

logging.getLogger("CMD")


def parse_args():
    parser = argparse.ArgumentParser(description='sanitize a disk')
    parser.add_argument('-m', '--method', type=str, help='sanitize method',
                        choices=['BASIC', 'BASELINE', 'ENHANCED'])

    disk = parser.add_mutually_exclusive_group(required=True)
    disk.add_argument('-d', '--device', type=str, action='append',
                      help='path to the /dev/{disk} E.G.: /dev/sda')
    disk.add_argument('-a', '--all', action='store_true',
                      help='all disks unless the disk mounted as root')

    parser.add_argument('--confirm', action='store_const', const=True,
                        help='confirm to sanitize disks before proceed')

    parser.add_argument('--version', action='version', version=app_version,
                        help='show the version of usody_sanitize')

    parser.add_argument('-l', '--log-level', dest='log_level', default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR',
                                 'CRITICAL'],
                        help='set the logging level (default: %(default)s)')

    parser.add_argument('-o', '--output', default=".",
                        help='set the output path to save the log file')

    return parser.parse_args()


def run_cmd():
    args = parse_args()
    configure_loggers(args.log_level)

    # Run erasures.
    result = run_coroutine(
        auto_erase_disks(args.method, args.device, confirm=args.confirm)
    )
    logging.debug(json.dumps(result, indent=4))

    if not result:
        return  # End here.

    # Create export directory.
    output_path = pathlib.Path(args.output)
    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)
        logging.debug(f"Creating directory `{output_path}`.")

    # Export the output to a file.
    for item in result:
        item_serial_number = item.get('device_info', {}).get('serial_number')
        current_date = datetime.datetime.now().date().isoformat()

        file_name = f"{current_date}_{item_serial_number}.json"
        with open(output_path / file_name, 'w') as _fh:
            json.dump(item, _fh, indent=4)


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


if __name__ == '__main__':
    run_cmd()
