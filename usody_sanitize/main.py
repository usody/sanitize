import sys
import asyncio
import logging

try:
    from usody_sanitize import erasure, __version__
except ModuleNotFoundError:
    import pathlib
    sys.path.append(
        pathlib.Path(__file__).parent.parent.absolute().as_posix()
    )
    from usody_sanitize import erasure, __version__


logger = logging.getLogger(__name__)


def run():
    """Forces to run the function in a new async loop."""
    loop = asyncio.new_event_loop()

    try:
        logger.info("Starting sanitize main process.")
        erasures = loop.run_until_complete(erasure.auto_erase_disks())

    finally:
        loop.close()

    return erasures


if __name__ == '__main__':
    # Run this one for development.
    # Run it.
    logging.basicConfig(
        force=True,
        stream=sys.stdout,
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s %(name)s -"
               " [%(funcName)s at line %(lineno)d]: %(message)s"
    )
    data = run()

    import json
    with open('/tmp/erasure_output.json', 'w') as _fh:
        json.dump(data, _fh, indent=4)

    # print(erasure.ErasureMethods.baseline_erasure)

