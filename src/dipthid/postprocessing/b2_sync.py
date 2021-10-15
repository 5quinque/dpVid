import logging
import os
import sys
import time
from pathlib import Path

from b2sdk.v2 import (
    B2Api,
    InMemoryAccountInfo,
    KeepOrDeleteMode,
    NewerFileSyncMode,
    ScanPoliciesManager,
    Synchronizer,
    SyncReport,
    parse_sync_folder,
)

from . import PostProcess

logger = logging.getLogger(__name__)


class B2Sync:
    def __init__(self, bucket_name, key, secret):
        info = InMemoryAccountInfo()
        self.b2_api = B2Api(info)
        self.b2_api.authorize_account("production", key, secret)

        self.bucket_name = bucket_name

        self.synchronizer = Synchronizer(
            max_workers=10,
            policies_manager=ScanPoliciesManager(exclude_all_symlinks=True),
            dry_run=False,
            newer_file_mode=NewerFileSyncMode.REPLACE,
            keep_days_or_delete=KeepOrDeleteMode.DELETE,
        )

    def sync(self, directory_path, dst):
        source = parse_sync_folder(directory_path, self.b2_api)
        destination = parse_sync_folder(f"b2://{self.bucket_name}/{dst}", self.b2_api)

        no_progress = False
        with SyncReport(sys.stdout, no_progress) as reporter:
            self.synchronizer.sync_folders(
                source_folder=source,
                dest_folder=destination,
                now_millis=int(round(time.time() * 1000)),
                reporter=reporter,
            )


class B2Process(PostProcess):
    def __init__(self, filename, mime_type=None, old_filename=None):
        self.sync = B2Sync(
            os.environ.get("B2_BUCKETNAME"),
            os.environ.get("B2_KEY"),
            os.environ.get("B2_SECRET"),
        )

        super().__init__(filename, mime_type, old_filename)

    def processed(self):
        path = Path(self.filename)
        filename = path.name
        logger.info(f"Uploading file <{filename}>")
        self.sync.sync(str(path.parent), str(path.parent.name))
        logger.info(f"Upload of <{filename}> complete")
