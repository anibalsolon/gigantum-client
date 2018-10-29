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

from gtmcore.gitlib.gitlab import GitLabManager
from gtmcore.labbook import LabBook
from gtmcore.exceptions import GigantumException

from gtmcore.logging import LMLogger
from gtmcore.configuration.utils import call_subprocess

logger = LMLogger.get_logger()


class WorkflowsException(Exception):
    pass


class MergeError(WorkflowsException):
    pass


class GitLabRemoteError(WorkflowsException):
    pass


def git_garbage_collect(labbook: LabBook) -> None:
    """Run "git gc" (garbage collect) over the repo. If run frequently enough, this only takes a short time
    even on large repos.

    Note!! This method assumes the subject labbook has already been locked!

    Args:
        labbook: Subject LabBook

    Returns:
        None

    Raises:
        subprocess.CalledProcessError when git gc fails.
        """
    logger.info(f"Running git gc (Garbage Collect) in {str(labbook)}...")
    if os.environ.get('WINDOWS_HOST'):
        logger.warning(f"Avoiding `git gc` in {str(labbook)} on Windows host fs")
        return

    try:
        call_subprocess(['git', 'gc'], cwd=labbook.root_dir)
    except subprocess.CalledProcessError:
        logger.warning(f"Ignore `git gc` error - {str(labbook)} repo remains unpruned")


def push(labbook: LabBook, remote: str) -> None:
    """Push commits to a remote git repository. Assume current working branch.

    Args:
        labbook: Subject labbook
        remote: Git remote (usually always origin).
    Returns:
        None
    """
    try:
        logger.info(f"Fetching from remote {remote}")
        labbook.git.fetch(remote=remote)

        if labbook.active_branch not in labbook.get_branches()['remote']:
            logger.info(f"Pushing and setting upstream branch {labbook.active_branch}")
            labbook.git.repo.git.push("--set-upstream", remote, labbook.active_branch)
        else:
            logger.info(f"Pushing to {remote}")
            labbook.git.publish_branch(branch_name=labbook.active_branch, remote_name=remote)
    except Exception as e:
        raise GitLabRemoteError(e)


def create_remote_gitlab_repo(labbook: LabBook, username: str, visibility: str,
                              access_token: Optional[str] = None) -> None:
    """Create a new repository in GitLab,

    Note: It may make more sense to factor this out later on. """

    default_remote = labbook.client_config.config['git']['default_remote']
    admin_service = None
    for remote in labbook.client_config.config['git']['remotes']:
        if default_remote == remote:
            admin_service = labbook.client_config.config['git']['remotes'][remote]['admin_service']
            break

    if not admin_service:
        raise ValueError('admin_service could not be found')

    try:
        # Add collaborator to remote service
        mgr = GitLabManager(default_remote, admin_service,
                            access_token=access_token or 'invalid')
        mgr.configure_git_credentials(default_remote, username)
        mgr.create_labbook(namespace=labbook.owner['username'], labbook_name=labbook.name,
                           visibility=visibility)
        labbook.add_remote("origin", f"https://{default_remote}/{username}/{labbook.name}.git")
    except Exception as e:
        raise GitLabRemoteError(e)


def publish_to_remote(labbook: LabBook, username: str, remote: str,
                      feedback_callback: Callable) -> None:
    # TODO - This should be called from the dispatcher
    # Current branch must be the user's workspace.
    if f'gm.workspace-{username}' != labbook.active_branch:
        raise ValueError('User workspace must be active branch to publish')

    # The gm.workspace branch must exist (if not, then there is a problem in Labbook.new())
    if 'gm.workspace' not in labbook.get_branches()['local']:
        raise ValueError('Branch gm.workspace does not exist in local Labbook branches')

    feedback_callback("Preparing to publish")
    git_garbage_collect(labbook)

    # Try five attempts to fetch - the remote repo could have been created just milliseconds
    # ago, so may need a few moments to settle before it supports all the git operations.
    for tr in range(5):
        try:
            labbook.git.fetch(remote=remote)
            break
        except Exception as e:
            logger.warning(f"Fetch attempt {tr+1}/5 failed for {str(labbook)}: {e}")
            time.sleep(1)
    else:
        raise ValueError(f"Timed out trying to fetch repo for {str(labbook)}")

    # Make sure user's workspace is synced (in case they are working on it on other machines)
    if labbook.get_commits_behind_remote(remote_name=remote)[1] > 0:
        raise ValueError(f'Cannot publish since {labbook.active_branch} is not synced')

    # Make sure the master workspace is synced before attempting to publish.
    feedback_callback("Checking out primary branch...")
    labbook.checkout_branch("gm.workspace")

    if labbook.get_commits_behind_remote(remote_name=remote)[1] > 0:
        raise ValueError(f'Cannot publish since {labbook.active_branch} is not synced')

    feedback_callback("Merging with user workspace...")
    # Now, it should be safe to pull the user's workspace into the master workspace.
    call_subprocess(['git', 'merge', f'gm.workspace-{username}'], cwd=labbook.root_dir)
    labbook.git.add_all(labbook.root_dir)
    labbook.git.commit(f"Merged gm.workspace-{username}")

    feedback_callback("Pushing up regular objects...")
    call_subprocess(['git', 'push', '--set-upstream', 'origin', 'gm.workspace'], cwd=labbook.root_dir)

    feedback_callback("Pushing up large objects...")
    if labbook.client_config.config["git"]["lfs_enabled"] is True:
        t0 = time.time()
        call_subprocess(['git', 'lfs', 'push', '--all', 'origin', 'gm.workspace'], cwd=labbook.root_dir)
        logger.info(f"Ran in {str(labbook)} `git lfs push --all` in {t0-time.time()}s")

    feedback_callback(f"Returning to {username} workspace ...")
    # Return to the user's workspace, merge it with the global workspace (as a precaution)
    labbook.checkout_branch(branch_name=f'gm.workspace-{username}')
    feedback_callback(f"Publish complete.")


def sync_with_remote(labbook: LabBook, username: str, remote: str,
                     force: bool, feedback_callback: Callable) -> int:
    """Sync workspace and personal workspace with the remote.

    Args:
        labbook: Subject labbook
        username(str): Username of current user (populated by API)
        remote(str): Name of the Git remote
        force: Force overwrite
        feedback_callback: Place to ingest user-facing updates

    Returns:
        int: Number of commits pulled from remote (0 implies no upstream changes pulled in).

    Raises:
        GigantumException on any problems.
    """

    # Note, BVB: For now, this method only supports the initial branching workflow of having
    # "workspace" and "workspace-{user}" branches. In the future, its signature will change to support
    # user feature-branches.

    try:
        if labbook.active_branch != f'gm.workspace-{username}':
            raise ValueError(f"Must be on user workspace (gm.workspace-{username}) to sync")

        if not labbook.has_remote:
            sync_locally(labbook, username)
            return 0

        feedback_callback(f"Sweeping {str(labbook)} uncommitted changes...")
        labbook.sweep_uncommitted_changes()
        git_garbage_collect(labbook)

        tokens = ['git', 'pull', '--commit', 'origin', 'gm.workspace']
        tokens_force = ['git', 'pull', '--commit', '-s', 'recursive', '-X', 'theirs', 'origin',
                        'gm.workspace']

        checkpoint = labbook.git.commit_hash
        try:
            feedback_callback("Pulling any upstream changes...")
            call_subprocess(tokens if not force else tokens_force, cwd=labbook.root_dir)
            if labbook.client_config.config["git"]["lfs_enabled"] is True:
                feedback_callback("Pulling large files...")
                call_subprocess(['git', 'lfs', 'pull', 'origin', 'gm.workspace'], cwd=labbook.root_dir)
        except subprocess.CalledProcessError as x:
            logger.error(f"{str(labbook)} cannot merge with remote; resetting to revision {checkpoint}...")
            call_subprocess(['git', 'merge', '--abort'], cwd=labbook.root_dir)
            call_subprocess(['git', 'reset', '--hard', checkpoint], cwd=labbook.root_dir)
            raise GigantumException('Merge conflict pulling upstream changes')

        feedback_callback("Merging with upstream changes...")
        checkpoint2 = labbook.git.commit_hash
        # TODO - A lot of this can be removed
        call_subprocess(['git', 'checkout', 'gm.workspace'], cwd=labbook.root_dir)
        call_subprocess(['git', 'merge', f'gm.workspace-{username}'], cwd=labbook.root_dir)

        feedback_callback("Pushing local changes back to remote...")
        call_subprocess(['git', 'push', 'origin', 'gm.workspace'], cwd=labbook.root_dir)
        if labbook.client_config.config["git"]["lfs_enabled"] is True:
            t0 = time.time()
            call_subprocess(['git', 'lfs', 'push', '--all', 'origin', 'gm.workspace'], cwd=labbook.root_dir)
            logger.info(f'Ran in {str(labbook)} `git lfs push all` in {t0-time.time()}s')

        feedback_callback(f"Returning to {username} workspace...")
        labbook.checkout_branch(f"gm.workspace-{username}")
        feedback_callback(f"Sync complete.")

        updates = 0 if checkpoint == checkpoint2 else 1

        # Return 1 if there have been updates made
        return updates

    except GigantumException as m:
        raise MergeError(m)
    except Exception as e:
        raise WorkflowsException(e)
    finally:
        # We should (almost) always have the user's personal workspace checked out.
        labbook.checkout_branch(f"gm.workspace-{username}")


def sync_locally(labbook: LabBook, username: Optional[str] = None) -> None:
    """Sync locally only to gm.workspace branch - don't do anything with remote. Creates a user's
     local workspace if necessary.

    Args:
        labbook: Subject labbook instance
        username: Active username

    Returns:
        None

    Raises:
        GigantumException
    """
    try:
        labbook.sweep_uncommitted_changes()

        git_garbage_collect(labbook)

        if username and f"gm.workspace-{username}" not in labbook.get_branches()['local']:
            labbook.checkout_branch("gm.workspace")
            labbook.checkout_branch(f"gm.workspace-{username}", new=True)
            labbook.git.merge("gm.workspace")
            labbook.git.commit(f"Created and merged new user workspace gm.workspace-{username}")
        else:
            orig_branch = labbook.active_branch
            labbook.checkout_branch("gm.workspace")
            labbook.git.merge(orig_branch)
            labbook.git.commit(f"Merged from local workspace")
            labbook.checkout_branch(orig_branch)
    except Exception as e:
        logger.error(e)
        raise GigantumException(e)
