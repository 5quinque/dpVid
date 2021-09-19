from dipthid.dip import Dip


def test_options():
    opts = {"--container": "mp4"}
    dip = Dip(opts)

    assert dip.container == "mp4"


def test_mp4():
    opts = {"--container": "mp4", "<path>": "./test_videos/sample-mp4-file.mp4"}
    dip = Dip(opts)

    assert dip.valid_file(opts["<path>"])

    # dip.convert(opts["<path>"])
