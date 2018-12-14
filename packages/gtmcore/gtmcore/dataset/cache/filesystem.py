import os
import pathlib

from gtmcore.dataset.cache.cache import CacheManager


class HostFilesystemCache(CacheManager):
    """A simple cache manager that just users the host filesystem
    """

    @property
    def current_revision_dir(self):
        """Method to return the directory containing files for the current dataset revision

        Returns:
            str
        """
        return os.path.join(self.cache_root, self.dataset.git.repo.head.commit.hexsha)

    @property
    def cache_root(self):
        """The location of the file cache root

        Returns:
            str
        """
        return os.path.join(os.path.expanduser("/mnt/gigantum/.labmanager/datasets"),
                            self.username, self.dataset.namespace, self.dataset.name)

    def initialize(self):
        """Method to configure a file cache for use.

        Returns:
            None
        """
        if not os.path.exists(self.cache_root):
            pathlib.Path(self.cache_root).mkdir(parents=True, exist_ok=True)

        return self.cache_root
