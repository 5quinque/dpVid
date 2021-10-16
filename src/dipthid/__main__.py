#!/usr/bin/env python


"""
dpVid / dipthid

Usage:
    dipthid watch <dir> [--consumers=CONSUMERS] [options]
    dipthid <path> [options]

Options:
    --consumers=CONSUMERS           Number of consumers that will convert videos asynchronously [default: 2]
    --log-level=LEVEL               Set logger level, one of DEBUG, INFO, WARNING, ERROR, CRITICAL [default: INFO]
    --post-processor=CLASS          The python class that handles post processing [default: dipthid.postprocessing:PostProcessLog]
    --strict                        [TODO]
"""

import asyncio
import logging

from docopt import docopt

from .dip import Dip

logger = logging.getLogger(__name__)


def setup_logging(opts):
    logging.basicConfig(
        level=opts["--log-level"],
        format="[%(asctime)s] <%(levelname)s> [%(name)s] %(message)s",
        force=True,
    )


def main():
    opts = docopt(__doc__)

    setup_logging(opts)

    dip = Dip(opts)

    if opts["watch"]:
        asyncio.run(dip.watch(opts))
    else:
        # Will only run convert_file synchronously
        asyncio.run(dip.convert(opts["<path>"]))


if __name__ == "__main__":
    main()
