import logging
import os
import time
from pathlib import Path

from b2sdk.v2 import B2Api, InMemoryAccountInfo, TqdmProgressListener

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
            progress_listener=TqdmProgressListener(b2_file_name),
        )

    def list_files(self):
        for file_version, folder_name in self.bucket.ls(latest_only=True):
            print(file_version.file_name, file_version.upload_timestamp, folder_name)


class B2Upload(PostProcess):
    def __init__(self, filename, mime_type=None, old_filename=None):
        self.bucket = B2Bucket(
            os.environ.get("B2_BUCKETNAME"),
            os.environ.get("B2_KEY"),
            os.environ.get("B2_SECRET"),
        )

        super().__init__(filename, mime_type, old_filename)

    def processed(self):
        filename = Path(self.filename).name
        logger.info(f"Uploading file <{filename}>")
        self.bucket.upload_file(self.filename, Path(self.filename).name)
        logger.info(f"Upload of <{filename}> complete")
