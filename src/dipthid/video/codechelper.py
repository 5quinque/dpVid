valid_codecs = {
    "mp4": {"audio": ("aac", "flac", "mp3", None), "video": ("av1", "h264", "vp9")},
    "webm": {"audio": ("opus", "vorbis", None), "video": ("av1", "vp8", "vp9")},
}

preferred_codec = {
    "mp4": {"audio": "aac", "video": "h264"},
    "webm": {"audio": "vorbis", "video": "vp8"},
}


def codecs(container, vid):
    valid = valid_codecs.get(container)
    ac = vc = "copy"

    if vid.audio_codec not in valid.get("audio"):
        ac = preferred_codec.get(container).get("audio")
    if vid.video_codec not in valid.get("video"):
        vc = preferred_codec.get(container).get("video")

    return (ac, vc)


def valid_container(mime_type):
    return mime_type in ("video/mp4", "video/webm")
