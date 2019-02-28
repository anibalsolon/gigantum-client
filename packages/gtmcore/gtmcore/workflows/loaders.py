from typing import Optional, Callable, Any, cast
import tempfile
import os

from gtmcore.configuration.utils import call_subprocess
from gtmcore.configuration import Configuration
from gtmcore.dataset.dataset import Dataset
from gtmcore.inventory import Repository
from gtmcore.inventory.branching import BranchManager
from gtmcore.inventory.inventory import InventoryManager
from gtmcore.exceptions import GigantumException
from gtmcore.logging import LMLogger

logger = LMLogger.get_logger()


def _clone(remote_url: str, working_dir: str) -> str:

    # Note, --recursive forces clone of all submodules
    clone_tokens = f"git clone {remote_url}".split()

    # Perform a Git clone
    call_subprocess(clone_tokens, cwd=working_dir)

    # Affirm there is only one directory created
    dirs = os.listdir(working_dir)
    if len(dirs) != 1:
        raise GigantumException('Git clone produced extra directories')

    p = os.path.join(working_dir, dirs[0])
    if not os.path.exists(p):
        raise GigantumException('Could not find expected path of repo after clone')

    # Initialize all submodule references, allowing updates to fail (for permission reasons)
    call_subprocess(['git', 'submodule', 'update', '--rescursive'], cwd=p, check=False)

    return p


def clone_repo(remote_url: str, username: str, owner: str,
               load_repository: Callable[[str], Any],
               put_repository: Callable[[str, str, str], Any],
               make_owner: bool = False) -> Repository:

    with tempfile.TemporaryDirectory() as tempdir:
        # Clone into a temporary directory, such that if anything
        # gets messed up, then this directory will be cleaned up.
        path = _clone(remote_url=remote_url, working_dir=tempdir)
        candidate_repo = load_repository(path)

        if os.environ.get('WINDOWS_HOST'):
            logger.warning("Imported on Windows host - set fileMode to false")
            call_subprocess("git config core.fileMode false".split(),
                            cwd=candidate_repo.root_dir)

        repository = put_repository(candidate_repo.root_dir, username, owner)

    return repository
