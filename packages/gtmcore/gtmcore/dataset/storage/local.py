from gtmcore.dataset import Dataset
from gtmcore.dataset.storage.backend import UnmanagedStorageBackend
from typing import List, Dict, Callable
import os

from gtmcore.dataset.io import PullResult, PullObject
from gtmcore.logging import LMLogger
from gtmcore.configuration import Configuration
from gtmcore.dataset.manifest.manifest import Manifest, StatusResult

logger = LMLogger.get_logger()


class LocalFilesystem(UnmanagedStorageBackend):

    def _backend_metadata(self) -> dict:
        """Method to specify Storage Backend metadata for each implementation. This is used to render the UI

        Simply implement this method in a child class. Note, 'icon' should be the name of the icon file saved in the
        thumbnails directory. It should be a 128x128 px PNG image.

        Returns:
            dict
        """
        return {"storage_type": "local_filesystem",
                "name": "Local Filesystem",
                "description": "Dataset type to use locally stored data. No files will sync with this dataset type.",
                "tags": ["local"],
                "icon": "local_filesystem.png",
                "url": "https://docs.gigantum.com",
                "readme": """Local Filesystem datasets simply mount a local directory for use inside your projects. 
For security reasons, only folders located the 'local_data' directory inside of your Gigantum working directory 
can be specified as the dataset root folder. This means you either need to place data there or symlink it. To learn
more, check out the docs here: [https://docs.gigantum.com](https://docs.gigantum.com)
"""}

    def _required_configuration(self) -> Dict[str, str]:
        """A private method to return a list of keys that must be set for a backend to be fully configured

        The format is a dict of keys and descriptions. E.g.

        {
          "server": "The host name for the remote server",
          "username": "The current logged in username"

        }

        There are 3 keys that are always automatically populated:
           - username: the gigantum username for the logged in user
           - gigantum_bearer_token: the gigantum bearer token for the current session
           - gigantum_id_token: the gigantum id token for the current session

        Returns:

        """
        return {"Data Root": "A folder in <gigantum_working_dir>/local_data/ to use as the dataset source"}

    def _get_local_data_dir(self) -> str:
        """Method to get the local data directory inside the current container

        Returns:
            str
        """
        working_dir = Configuration().config['git']['working_dir']
        return os.path.join(working_dir, 'local_data', self.configuration.get("Data Root"))

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

        status_update_fn(f"Ready to link objects for {dataset.namespace}/{dataset.name}")

    def finalize_pull(self, dataset, status_update_fn: Callable) -> None:
        status_update_fn(f"Done linking objects for {dataset.namespace}/{dataset.name}")

    def pull_objects(self, dataset: Dataset, objects: List[PullObject], status_update_fn: Callable) -> PullResult:
        """High-level method to link files from the source dir to the object directory

        Args:
            dataset: The current dataset
            objects: A list of PullObjects the enumerate objects to push
            status_update_fn: A callback to update status and provide feedback to the user

        Returns:
            PushResult
        """
        for obj in objects:
            os.symlink(os.path.join(self._get_local_data_dir(), obj.dataset_path), obj.object_path)

        return PullResult(success=objects, failure=[], message="Linked data directory. All files should be available")

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

            for file in files:
                # TODO: Check for ignored
                if file in ['.smarthash', '.DS_STORE', '.DS_Store']:
                    continue

                rel_path = os.path.join(folder, file)
                all_files.append(rel_path)
                if rel_path not in m.manifest:
                    added_files.append(rel_path)

        deleted_files = sorted(list(set(m.manifest.keys()).difference(all_files)))

        # Create StatusResult to force modifications
        status = StatusResult(created=added_files, modified=[], deleted=deleted_files)

        # Update the manifest
        m.update(status)

        # Run local update
        self.update_from_local(dataset, status_update_fn)
