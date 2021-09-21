import mimetypes

import pytest

from dipthid.video import Video
from dipthid.video.codechelper import codecs, valid_container


@pytest.mark.parametrize(
    "video_path, expected_result",
    [
        ("./test_videos/sample-avi-file.avi", ("aac", "h264")),
        ("./test_videos/sample-flv-file.flv", ("aac", "h264")),
        ("./test_videos/sample-mkv-file.mkv", ("copy", "copy")),
        ("./test_videos/sample-mov-file.mov", ("copy", "copy")),
        ("./test_videos/sample-mp4-file.mp4", ("copy", "copy")),
        ("./test_videos/sample-mpg-file.mpg", ("copy", "h264")),
        ("./test_videos/sample-webm-file.webm", ("aac", "h264")),
        ("./test_videos/sample-wmv-file.wmv", ("aac", "h264")),
    ],
)
def test_codec(video_path, expected_result):
    assert codecs("mp4", Video(video_path)) == expected_result


@pytest.mark.parametrize(
    "video_path, expected_result",
    [
        ("./test_videos/sample-avi-file.avi", False),
        ("./test_videos/sample-flv-file.flv", False),
        ("./test_videos/sample-mkv-file.mkv", False),
        ("./test_videos/sample-mov-file.mov", False),
        ("./test_videos/sample-mp4-file.mp4", True),
        ("./test_videos/sample-mpg-file.mpg", False),
        ("./test_videos/sample-webm-file.webm", True),
        ("./test_videos/sample-wmv-file.wmv", False),
    ],
)
def test_mimetype(video_path, expected_result):
    mime_type, _ = mimetypes.guess_type(video_path)
    assert valid_container(mime_type) == expected_result
