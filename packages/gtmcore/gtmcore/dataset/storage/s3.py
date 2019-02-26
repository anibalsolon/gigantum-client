from gtmcore.dataset import Dataset
from gtmcore.dataset.storage.backend import UnmanagedStorageBackend
from typing import List, Dict, Callable, Optional
import os

from gtmcore.dataset.io import PullResult, PullObject
from gtmcore.logging import LMLogger
from gtmcore.configuration import Configuration
from gtmcore.dataset.manifest.manifest import Manifest, StatusResult

import boto3
import botocore

logger = LMLogger.get_logger()


class PublicS3Bucket(UnmanagedStorageBackend):

    def _backend_metadata(self) -> dict:
        """Method to specify Storage Backend metadata for each implementation. This is used to render the UI

        Simply implement this method in a child class. Note, 'icon' should be the name of the icon file saved in the
        thumbnails directory. It should be a 128x128 px PNG image.

        Returns:
            dict
        """
        return {"storage_type": "public_s3_bucket",
                "name": "Public S3 Bucket",
                "description": "A type to use data stored in a public S3 bucket",
                "tags": ["unmanaged", "s3", "aws"],
                "icon": "s3.png",
                "url": "https://docs.gigantum.com",
                "readme": """This dataset type simply loads data from a public S3 bucket. It supports automatic 
synchronization with S3 so you don't need to manually enter any information other than the bucket name. 

Due to the possibility of storing lots of data, when updating you can optionally keep all data locally or not. Because
 all files must be hashed when adding to the dataset, they all need to be downloaded by the creator. Once added
 to the dataset, partial downloads of the data is supported. To learn more, check out the docs here:
 [https://docs.gigantum.com](https://docs.gigantum.com)
"""}

    def _required_configuration(self) -> List[Dict[str, str]]:
        """A private method to return a list of parameters that must be set for a backend to be fully configured

        The format is a list of dictionaries, e.g.:

        [
          {
            "parameter": "server",
            "description": "URL of the remote server",
            "type": "str"
          },
          {
            "parameter": "username",
            "description": "The current logged in username",
            "type": "str"
          }
        ]

        "type" must be either `str` or `bool`

        There are 3 parameters that are always automatically populated:
           - username: the gigantum username for the logged in user
           - gigantum_bearer_token: the gigantum bearer token for the current session
           - gigantum_id_token: the gigantum id token for the current session
        """
        return [{'parameter': "Bucket Name",
                 'description': "Name of the public S3 Bucket",
                 'type': "str"
                 },
                {'parameter': "Prefix",
                 'description': "Optional prefix inside the bucket (e.g. `prefix1/sub3/`)",
                 'type': "str"
                 },
                {'parameter': "Discard During Update",
                 'description': "A flag indicating if files should be kept locally during automatic updating "
                                "(unchecked), or that files should be discarded after hashed and added to the"
                                " Dataset (checked).",
                 'type': "bool"
                 }
                ]

    def confirm_configuration(self, dataset, status_update_fn: Callable) -> Optional[str]:
        """Method to verify a configuration and optionally allow the user to confirm before proceeding

        Should return the desired confirmation message if there is one. If no confirmation is required/possible,
        return None

        """
        bucket = self.configuration.get("Bucket Name")
        if not bucket:
            raise ValueError("Bucket Name required to confirm configuration")

        if not self.configuration.get("Prefix"):
            prefix = ""
        else:
            prefix = self.configuration.get("Prefix")

        client = boto3.client('s3')
        # Confirm bucket exists and is public
        try:
            client.head_bucket(Bucket=bucket)
        except botocore.client.ClientError:
            raise ValueError(f"Access denied to {bucket}. Double check Bucket Name")

        # List number of files and total size
        paginator = client.get_paginator('list_objects_v2')
        response_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)

        num_bytes = 0
        num_objects = 0
        for x in response_iterator:
            for item in x.get("Contents"):
                num_bytes += int(item.get('Size'))
                num_objects += 1

        confirm_message = f"Updating this dataset will download {num_objects} files and {float(num_bytes)/(10**9)} GB."

        if self.configuration.get("Discard During Update") is True:
            confirm_message = f"{confirm_message} New files will be discarded during update. Do you wish to continue?"
        else:
            confirm_message = f"{confirm_message} New files will be kept and use {float(num_bytes)/(10**9)} GB of" \
                f" local storage. Do you wish to continue?"

        return confirm_message

    def _get_local_data_dir(self) -> str:
        """Method to get the local data directory inside the current container

        Returns:
            str
        """
        working_dir = Configuration().config['git']['working_directory']
        data_dir = self.configuration.get("Data Directory")
        if not data_dir:
            raise ValueError("Data Directory must be specified.")

        return os.path.join(working_dir, 'local_data', data_dir)

    def prepare_pull(self, dataset, objects: List[PullObject], status_update_fn: Callable) -> None:
        """Gigantum Object Service only requires that the user's tokens have been set

        Args:
            dataset: The current dataset instance
            objects: A list of PushObjects to be pulled
            status_update_fn: A function to update status during pushing

        Returns:
            None
        """
        if not self.is_configured:
            raise ValueError("Local filesystem backend must be fully configured before running pull.")

        status_update_fn(f"Ready to link files for {dataset.namespace}/{dataset.name}")

    def finalize_pull(self, dataset, status_update_fn: Callable) -> None:
        pass

    def pull_objects(self, dataset: Dataset, objects: List[PullObject], status_update_fn: Callable) -> PullResult:
        """High-level method to simply link files from the source dir to the object directory to the revision directory

        Args:
            dataset: The current dataset
            objects: A list of PullObjects the enumerate objects to push
            status_update_fn: A callback to update status and provide feedback to the user

        Returns:
            PushResult
        """
        # Link from local data directory to the object directory
        for obj in objects:
            if os.path.islink(obj.object_path):
                # Re-link to make 100% sure all links are consistent if a link already exists
                os.remove(obj.object_path)
            os.symlink(os.path.join(self._get_local_data_dir(), obj.dataset_path), obj.object_path)

        # link from object dir through to revision dir
        m = Manifest(dataset, self.configuration.get('username'))
        m.link_revision()

        return PullResult(success=objects,
                          failure=[],
                          message="Linked data directory. All files from the manifest should be available")

    def can_update_from_remote(self) -> bool:
        """Property indicating if this backend can automatically update its contents to the latest on the remote

        Returns:
            bool
        """
        return True

    def update_from_remote(self, dataset, status_update_fn: Callable) -> None:
        """Optional method that updates the dataset by comparing against the remote. Not all unmanaged dataset backends
        will be able to do this.

        Args:
            dataset: Dataset object
            status_update_fn: A callable, accepting a string for logging/providing status to the UI

        Returns:
            None
        """
        if 'username' not in self.configuration:
            raise ValueError("Dataset storage backend requires current logged in username to verify contents")
        m = Manifest(dataset, self.configuration.get('username'))

        # walk the local source dir, looking for additions/deletions
        all_files = list()
        added_files = list()
        local_data_dir = self._get_local_data_dir()
        for root, dirs, files in os.walk(local_data_dir):
            _, folder = root.split(local_data_dir)
            if len(folder) > 0:
                if folder[0] == os.path.sep:
                    folder = folder[1:]

            for d in dirs:
                # TODO: Check for ignored
                rel_path = os.path.join(folder, d) + os.path.sep  # All folders are represented with a trailing slash
                all_files.append(rel_path)
                if rel_path not in m.manifest:
                    added_files.append(rel_path)
                    # Create dir in current revision for linking to work
                    os.makedirs(os.path.join(m.cache_mgr.cache_root, m.dataset_revision, rel_path), exist_ok=True)

            for file in files:
                # TODO: Check for ignored
                if file in ['.smarthash', '.DS_STORE', '.DS_Store']:
                    continue

                rel_path = os.path.join(folder, file)
                all_files.append(rel_path)
                if rel_path not in m.manifest:
                    added_files.append(rel_path)
                    # Symlink into current revision for downstream linking to work
                    os.symlink(os.path.join(root, file),
                               os.path.join(m.cache_mgr.cache_root, m.dataset_revision, rel_path))

        deleted_files = sorted(list(set(m.manifest.keys()).difference(all_files)))

        # Create StatusResult to force modifications
        status = StatusResult(created=added_files, modified=[], deleted=deleted_files)

        # Run local update
        self.update_from_local(dataset, status_update_fn, status_result=status)
