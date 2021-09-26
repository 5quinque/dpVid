import logging
import os
import time
from pathlib import Path

from b2sdk.v2 import AbstractProgressListener, B2Api, InMemoryAccountInfo

from . import PostProcess

logger = logging.getLogger(__name__)


class B2Bucket:
    def __init__(self, bucket_name, key, secret):
        info = InMemoryAccountInfo()
        b2_api = B2Api(info)
        b2_api.authorize_account("production", key, secret)

        self.bucket = b2_api.get_bucket_by_name(bucket_name)

    def upload_file(self, local_file, b2_file_name, **file_info):
        self.bucket.upload_local_file(
            local_file=local_file,
            file_name=b2_file_name,
            file_infos=file_info,
            progress_listener=B2ProgressListener(),
        )

    def list_files(self):
        for file_version, folder_name in self.bucket.ls(latest_only=True):
            print(file_version.file_name, file_version.upload_timestamp, folder_name)


class B2ProgressListener(AbstractProgressListener):
    def __init__(self):
        self.percentage = 0
        self.tic = 0

        super().__init__()

    def set_total_bytes(self, total_byte_count):
        self.total_byte_count = total_byte_count
        logger.info(f"Total bytes: {self.total_byte_count}")

    def bytes_completed(self, byte_count):
        percentage = int(100 * float(byte_count) / float(self.total_byte_count))

        if (
            int(time.perf_counter()) - self.tic > 2
            or byte_count == self.total_byte_count
            and percentage != self.percentage
        ):
            logger.info(f"Upload progress: {percentage=}%")
            self.percentage = percentage
            self.tic = int(time.perf_counter())


class B2Upload(PostProcess):
    def __init__(self, filename, new_filename=None, mime_type=None):
        self.bucket = B2Bucket(
            os.environ.get("B2_BUCKETNAME"),
            os.environ.get("B2_KEY"),
            os.environ.get("B2_SECRET"),
        )

        super().__init__(filename, new_filename, mime_type)

    def processed(self):
        filename = Path(self.new_filename).name
        logger.info(f"Uploading file <{filename}>")
        self.bucket.upload_file(self.new_filename, Path(self.new_filename).name)
        logger.info(f"Upload of <{filename}> complete")
