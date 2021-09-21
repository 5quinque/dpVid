import pytest

from dipthid.dip import Dip


def test_options():
    opts = {
        "--container": "mp4",
        "--post-processer": "dipthid.postprocessing:PostProcess",
    }
    dip = Dip(opts)

    assert dip.container == "mp4"


@pytest.mark.asyncio
async def test_mp4():
    opts = {
        "--container": "mp4",
        "<path>": "./test_videos/sample-mp4-file.mp4",
        "--post-processer": "dipthid.postprocessing:PostProcess",
    }

    dip = Dip(opts)

    assert dip.valid_file(opts["<path>"])

    await dip.convert(opts["<path>"])
