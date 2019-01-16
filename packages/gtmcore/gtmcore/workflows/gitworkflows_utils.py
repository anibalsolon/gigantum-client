# Copyright (c) 2017 FlashX, LLC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import subprocess
import time
import os
from typing import Optional, Callable

from gtmcore.workflows.gitlab import GitLabManager
# from gtmcore.labbook import LabBook
from gtmcore.inventory import Repository
from gtmcore.inventory.inventory import InventoryManager
from gtmcore.exceptions import GigantumException

from gtmcore.logging import LMLogger
from gtmcore.configuration.utils import call_subprocess
from gtmcore.inventory.branching import BranchManager


logger = LMLogger.get_logger()


class WorkflowsException(Exception):
    pass


class MergeError(WorkflowsException):
    pass


class GitLabRemoteError(WorkflowsException):
    pass


def git_garbage_collect(repository: Repository) -> None:
    """Run "git gc" (garbage collect) over the repo. If run frequently enough, this only takes a short time
    even on large repos.

    Note!! This method assumes the subject repository has already been locked!

    Args:
        repository: Subject Repository

    Returns:
        None

    Raises:
        subprocess.CalledProcessError when git gc fails.
        """
    logger.info(f"Running git gc (Garbage Collect) in {str(repository)}...")
    if os.environ.get('WINDOWS_HOST'):
        logger.warning(f"Avoiding `git gc` in {str(repository)} on Windows host fs")
        return

    try:
        call_subprocess(['git', 'gc'], cwd=repository.root_dir)
    except subprocess.CalledProcessError:
        logger.warning(f"Ignore `git gc` error - {str(repository)} repo remains unpruned")


def create_remote_gitlab_repo(repository: Repository, username: str, visibility: str,
                              access_token: Optional[str] = None) -> None:
    """Create a new repository in GitLab,

    Note: It may make more sense to factor this out later on. """

    default_remote = repository.client_config.config['git']['default_remote']
    admin_service = None
    for remote in repository.client_config.config['git']['remotes']:
        if default_remote == remote:
            admin_service = repository.client_config.config['git']['remotes'][remote]['admin_service']
            break

    if not admin_service:
        raise ValueError('admin_service could not be found')

    try:
        # Add collaborator to remote service
        mgr = GitLabManager(default_remote, admin_service,
                            access_token=access_token or 'invalid')
        mgr.configure_git_credentials(default_remote, username)
        mgr.create_labbook(namespace=InventoryManager().query_owner(repository),
                           labbook_name=repository.name,
                           visibility=visibility)
        repository.add_remote("origin", f"https://{default_remote}/{username}/{repository.name}.git")
    except Exception as e:
        raise GitLabRemoteError(e)


def publish_to_remote(repository: Repository, username: str, remote: str,
                      feedback_callback: Callable) -> None:
    bm = BranchManager(repository, username=username)
    if bm.workspace_branch != bm.active_branch:
        raise ValueError(f'Must be on branch {bm.workspace_branch} to publish')

    feedback_callback(f"Preparing to publish {repository.name}")
    git_garbage_collect(repository)

    # Try five attempts to fetch - the remote repo could have been created just milliseconds
    # ago, so may need a few moments to settle before it supports all the git operations.
    for tr in range(5):
        try:
            repository.git.fetch(remote=remote)
            break
        except Exception as e:
            logger.warning(f"Fetch attempt {tr+1}/5 failed for {str(repository)}: {e}")
            time.sleep(1)
    else:
        raise ValueError(f"Timed out trying to fetch repo for {str(repository)}")

    feedback_callback("Pushing up regular objects...")
    call_subprocess(['git', 'push', '--set-upstream', 'origin', bm.workspace_branch],
                    cwd=repository.root_dir)

    if repository.client_config.config["git"]["lfs_enabled"] is True:
        feedback_callback("Pushing up large objects...")
        t0 = time.time()
        call_subprocess(['git', 'lfs', 'push', '--all', 'origin', bm.workspace_branch],
                        cwd=repository.root_dir)
        logger.info(f"Ran in {str(repository)} `git lfs push --all` in {t0-time.time()}s")

    feedback_callback(f"Publish complete.")


def _set_upstream_branch(repository: Repository, branch_name: str, feedback_cb: Callable):
    set_upstream_tokens = ['git', 'push', '--set-upstream', 'origin', branch_name]
    call_subprocess(set_upstream_tokens, cwd=repository.root_dir)

    if repository.client_config.config["git"]["lfs_enabled"] is True:
        feedback_cb('Pushing large files')
        t0 = time.time()
        call_subprocess(['git', 'lfs', 'push', '--all', 'origin', branch_name], cwd=repository.root_dir)
        logger.info(f'Ran in {str(repository)} `git lfs push all` in {t0-time.time()}s')


def _sync_pull_push(repository: Repository, branch_name: str, feedback_cb: Callable):

    # Pull regular Git objects, then LFS
    try:
        call_subprocess(['git', 'pull', 'origin', branch_name],
                    cwd=repository.root_dir)
    except subprocess.CalledProcessError as cp_error:
        if 'Automatic merge failed' in cp_error.stdout.decode():
            raise MergeError(f"Merge conflict pulling in branch {branch_name}")
        else:
            raise

    if repository.client_config.config["git"]["lfs_enabled"] is True:
        feedback_cb("Pulling large files...")
        call_subprocess(['git', 'lfs', 'pull', 'origin', branch_name],
                        cwd=repository.root_dir)

    # Push regular Git objects, then LFS objects
    call_subprocess(['git', 'push', 'origin', branch_name], cwd=repository.root_dir)
    if repository.client_config.config["git"]["lfs_enabled"] is True:
        call_subprocess(['git', 'lfs', 'push', '--all', 'origin', branch_name],
                        cwd=repository.root_dir)


def sync_branch(repository: Repository, username: str, feedback_callback: Callable) -> int:
    """"""
    repository.sweep_uncommitted_changes()
    repository.git.fetch()

    bm = BranchManager(repository, username=username)
    if bm.active_branch not in bm.branches_remote:
        _set_upstream_branch(repository, bm.active_branch, feedback_callback)
        return 0
    else:
        _, pulled_updates_count = bm.get_commits_behind_remote()
        _sync_pull_push(repository, bm.active_branch, feedback_callback)
        return pulled_updates_count
