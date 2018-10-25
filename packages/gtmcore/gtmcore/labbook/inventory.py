import os
import shutil
from natsort import natsorted

from typing import Optional, Generator, List, Tuple

from gtmcore.gitlib import GitAuthor
from gtmcore.logging import LMLogger
from gtmcore.configuration import Configuration
from gtmcore.configuration.utils import call_subprocess
from gtmcore.labbook.labbook import LabBook

logger = LMLogger.get_logger()


class InventoryException(Exception):
    pass


class InventoryManager(object):
    """ This class absorbs the complexity of accepting data structures into the client's
        working directory. We need this class because interacting with the "inventory"
        (i.e., the tree of labbooks located in the user's working directory) can be
        a messy and error-prone process. Any other functionality that needs to insert
        data into the inventory no longer needs to be aware of any specifics of the internal
        structure of it or worry about cleanup. """

    def __init__(self, config_file: Optional[str] = None) -> None:
        self.config_file = config_file
        cfg = Configuration(self.config_file)
        self.inventory_root = os.path.expanduser(cfg.config['git']['working_directory'])

    def __str__(self) -> str:
        return f'<InventoryManager: {self.inventory_root}>'

    def __eq__(self, other) -> bool:
        return isinstance(other, InventoryManager) \
               and self.inventory_root == other.inventory_root

    def _put_labbook(self, path: str, username: str, owner: str) -> LabBook:
        # Validate that given path contains labbook
        temp_lb = self.load_labbook_from_directory(path)

        p = os.path.join(self.inventory_root, username, owner, 'labbooks')
        dname = os.path.basename(path)
        if os.path.exists(p) and dname in os.listdir(p):
            raise InventoryException(f"Project directory {dname} already exists")

        if not os.path.exists(p):
            os.makedirs(p, exist_ok=True)

        if os.path.exists(os.path.join(p, dname)):
            raise InventoryException(f"Project directory {dname} already exists")

        final_path = shutil.move(path, p)
        assert os.path.dirname(final_path) != 'labbooks', \
               f"shutil.move used incorrectly"

        lb = self.load_labbook_from_directory(final_path)
        return lb

    def put_labbook(self, path: str, username: str, owner: str) -> LabBook:
        """ Take given path to a candidate labbook and insert it
        into its proper place in the file system.

        Args:
            path: Path to a given labbook
            username: Active username
            owner: Intended owner of labbook

        Returns:
            LabBook
        """
        try:
            return self._put_labbook(path, username, owner)
        except Exception as e:
            logger.error(e)
            raise InventoryException(e)

    def load_labbook_from_directory(self, path: str) -> LabBook:
        """ Load and return a LabBook object from a given path on disk

        Warning - Deprecated !! Use load_labbook instead

        Args:
            path: Full path on disk to LabBook

        Returns:
            LabBook object
        """
        try:
            lb = LabBook(config_file=self.config_file)
            lb._set_root_dir(path)
            lb._load_labbook_data()
            lb._validate_labbook_data()
            return lb
        except Exception as e:
            logger.error(e)
            raise InventoryException(e)

    def load_labbook(self, username: str, owner: str, labbook_name: str,
                     author: Optional[GitAuthor] = None) -> LabBook:
        try:
            lb = LabBook(self.config_file)
            lbroot = os.path.join(self.inventory_root, username,
                                  owner, 'labbooks', labbook_name)
            lb._set_root_dir(lbroot)
            lb._load_labbook_data()
            lb._validate_labbook_data()
            lb.author = author
            return lb
        except Exception as e:
            raise InventoryException(f"Cannot retrieve "
                                     f"({username}, {owner}, {labbook_name}): {e}")

    def list_labbook_ids(self, username) -> List[Tuple[str, str, str]]:
        """Return a list of (username, owner, labbook-name) tuples corresponding
           to all labbooks whose existence is inferred. Since this method does not
           actually load the labbooks, it returns quite fast.

           Warnings - there *may* exist corrupted labbooks in the returned set -
            no validation is guaranteed.

        Args:
            username: Active username to crawl for

        Returns:
            List of 3-tuples containing (username, owner, labook-name)
        """
        user_root = os.path.join(self.inventory_root, username)
        if not os.path.exists(user_root):
            return []

        owner_dirs = sorted([os.path.join(user_root, d)
                             for d in os.listdir(user_root)
                             if os.path.isdir(os.path.join(user_root, d))])
        labbook_paths = []
        for owner_dir in owner_dirs:
            labbook_dirs = sorted([os.path.join(owner_dir, 'labbooks', l)
                                   for l in os.listdir(os.path.join(owner_dir, 'labbooks'))
                                   if os.path.isdir(os.path.join(owner_dir, 'labbooks', l))])
            for labbook_dir in labbook_dirs:
                labbook_paths.append((username,
                                      os.path.basename(owner_dir),
                                      os.path.basename(labbook_dir)))
        return labbook_paths

    def list_labbooks(self, username: str, sort_mode: str = "name") -> List[LabBook]:
        """ Return list of all available labbooks for a given user

        Args:
            username: Active username
            sort_mode: One of "name", "modified_on" or "created_on"

        Returns:
            Sorted list of LabBook objects
        """
        local_labbooks = []
        for username, owner, lbname in self.list_labbook_ids(username):
            try:
                labbook = self.load_labbook(username, owner, lbname)
                local_labbooks.append(labbook)
            except Exception as e:
                logger.error(e)

        if sort_mode == "name":
            return natsorted(local_labbooks, key=lambda lb: lb.name)
        elif sort_mode == 'modified_on':
            return sorted(local_labbooks, key=lambda lb: lb.modified_on)
        elif sort_mode == 'created_on':
            return sorted(local_labbooks, key=lambda lb: lb.creation_date)
        else:
            raise InventoryException(f"Invalid sort mode {sort_mode}")
