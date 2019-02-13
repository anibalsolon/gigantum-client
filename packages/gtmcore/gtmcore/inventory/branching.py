# Copyright (c) 2018 FlashX, LLC
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
import re
import subprocess

import git
from typing import Optional, List, Tuple

from gtmcore.exceptions import GigantumException
from gtmcore.logging import LMLogger
# from gtmcore.repository import LabBook
from gtmcore.inventory import Repository
from gtmcore.configuration.utils import call_subprocess

logger = LMLogger.get_logger()


class BranchException(GigantumException):
    pass


class BranchWorkflowViolation(BranchException):
    pass


class MergeConflict(BranchException):
    def __init__(self, message, file_conflicts: List[str]) -> None:
        super().__init__(message)
        # List of file paths (relative to root) that are in conflict
        self.file_conflicts = file_conflicts


class InvalidBranchName(BranchException):
    pass


class BranchManager(object):
    """Responsible for all Git branch and merge operations.

    Intended to be the sole entrypoint for operations to query for
    and perform basic Git branching operations. The Workflows package
    in particular is intended to be the main user of this class, which
    will use the methods provided here to support conflict-free distributed
    workflow among users.

    TODO(billvb): Finish removing all workflow-specific fields
    """

    def __init__(self, repository: Repository, username: Optional[str] = None) -> None:
        self.repository = repository
        self.username = username

    @classmethod
    def is_branch_name_valid(cls, new_branch_name: str) -> bool:
        """Query if the given branch name is can be the name of a new branch"""
        if len(new_branch_name) > 80:
            return False
        return all([(e.replace('.', '').isalnum() and e == e.lower()) for e in new_branch_name.split('-')])

    @property
    def active_branch(self) -> str:
        """Return the name of the current branch."""
        return self.repository.active_branch

    @property
    def workspace_branch(self) -> str:
        """Return the user's primary branch name

        TODO(billvb): Migrate to Workflows (does not belong here).
        """
        return 'master'

    @property
    def branches_remote(self) -> List[str]:
        if self.repository.has_remote:
            return sorted([b.replace('origin/', '') for b in self.repository.get_branches()['remote']])
        else:
            return []

    @property
    def branches_local(self) -> List[str]:
        return sorted(self.repository.get_branches()['local'])

    def fetch(self) -> None:
        """Perform a git fetch"""
        self.repository.git.fetch()

    def create_branch(self, title: str, revision: Optional[str] = None) -> str:
        """Create and checkout (work on) a new managed branch.

        Args:
            title: Branch name
            revision: Git commit hash or branch name to base branch from

        Returns:
            Name of newly created branch.
        """
        if not self.is_branch_name_valid(title):
            raise InvalidBranchName(f'Branch name `{title}` invalid pattern')

        if title in self.branches_local:
            raise InvalidBranchName(f'Branch name `{title}` already exists')

        self.repository.sweep_uncommitted_changes()
        if revision:
            # The following call prints "commit" if {revision} exists in git history.
            result = subprocess.check_output(f'git cat-file -t {revision} || echo "invalid"',
                                             cwd=self.repository.root_dir, shell=True)
            if result.decode().strip() != 'commit':
                logger.error(result.decode().strip())
                raise InvalidBranchName(f'Revision {revision} does not exist in {str(self.repository)};'
                                        f'cannot create branch {title}')
            # Should be in a detached-head, and then make branch from there.
            logger.info(f"Creating rollback branch from revision {revision} in {str(self.repository)}")
            r = subprocess.check_output(f'git checkout {revision}', cwd=self.repository.root_dir, shell=True)
            logger.info(r)
        self.repository.checkout_branch(branch_name=title, new=True)
        logger.info(f'Activated new branch {self.active_branch} in {str(self.repository)}')

        return title

    def remove_branch(self, target_branch: str) -> None:
        """Delete a local feature branch that is NOT the active branch.

        Args:
            target_branch: Full name of feature branch to delete

        Returns:
            None
        """
        if target_branch not in self.branches_local:
            raise InvalidBranchName(f'Cannot delete `{target_branch}`; does not exist')

        if target_branch == self.workspace_branch:
            raise BranchWorkflowViolation(f'Cannot delete workspace branch `{target_branch}` in {str(self.repository)}')

        if target_branch == self.active_branch:
            raise BranchWorkflowViolation(f'Cannot delete current active branch `{target_branch}`')

        logger.info(f'Removing from {str(self.repository)} feature branch `{target_branch}`')
        # Note use "force=True" to prevent warning on merge.
        self.repository.git.delete_branch(target_branch, force=True)

        if target_branch in self.branches_local:
            raise BranchWorkflowViolation(f'Removal of branch `{target_branch}` in {str(self.repository)} failed.')

    def _workon_branch(self, branch_name: str) -> None:
        """Checkouts a branch as the working revision. """

        #if branch_name not in self.branches:
        #    raise InvalidBranchName(f'Target branch `{branch_name}` does not exist')

        self.repository.sweep_uncommitted_changes(extra_msg="Save state on branch change")
        self.repository.checkout_branch(branch_name=branch_name)
        logger.info(f'Checked out branch {self.active_branch} in {str(self.repository)}')

    def workon_branch(self, branch_name: str) -> None:
        """Performs a Git checkout on the given branch_name"""
        try:
            self._workon_branch(branch_name)
        except Exception as e:
            logger.error(e)
            raise BranchException(e)

    def _infer_conflicted_files(self, merge_output: str):
        return [l.split()[-1] for l in merge_output.split('\n')
                if 'CONFLICT' in l and 'Merge conflict in ' in l]

    def merge_from(self, other_branch: str) -> None:
        """Pulls/merges `other_branch` into current branch. If in the event of a
        conflict, it resets to the point prior to merge.

        Args:
            other_branch: Name of other branch to merge from
        """


        if other_branch not in self.branches_local:
            raise InvalidBranchName(f'Branch {other_branch} not found')

        checkpoint = self.repository.git.commit_hash
        try:
            self.repository.sweep_uncommitted_changes()
            try:
                call_subprocess(f'git merge {other_branch}'.split(), cwd=self.repository.root_dir)
            except subprocess.CalledProcessError as merge_error:
                logger.warning(f"Merge conflict syncing {str(self.repository)}")
                # TODO - This should be cleaned up (The UI attempts to match on the token "Cannot merge")
                conflicted_files = self._infer_conflicted_files(merge_error.stdout.decode())
                raise MergeConflict(f"Cannot merge - {merge_error}",
                                    file_conflicts=conflicted_files)
            self.repository.git.commit(f'Merged from branch `{other_branch}`')
        except Exception as e:
            call_subprocess(f'git reset --hard {checkpoint}'.split(), cwd=self.repository.root_dir)
            raise e

    def merge_use_ours(self, other_branch: str):
        self.repository.sweep_uncommitted_changes()
        ot = call_subprocess(f'git merge {other_branch}'.split(), cwd=self.repository.root_dir, check=False)
        conf_files = self._infer_conflicted_files(ot)
        if conf_files:
            call_subprocess(f'git checkout --ours {" ".join(conf_files)}'.split(),
                            cwd=self.repository.root_dir)
        self.repository.sweep_uncommitted_changes(extra_msg=f"Merged {other_branch} using ours.")

    def merge_use_theirs(self, other_branch: str):
        self.repository.sweep_uncommitted_changes()
        ot = call_subprocess(f'git merge {other_branch}'.split(), cwd=self.repository.root_dir, check=False)
        conf_files = self._infer_conflicted_files(ot)
        if conf_files:
            call_subprocess(f'git checkout --theirs {" ".join(conf_files)}'.split(),
                            cwd=self.repository.root_dir)
        self.repository.sweep_uncommitted_changes(extra_msg=f"Merged {other_branch} using theirs.")


    def get_commits_ahead(self, branch_name: Optional[str] = None, remote_name: str = "origin") -> int:
        """Return to number of local commits not present in remote branch.

        Note! It is important to call fetch to ensure correct behavior here."""
        if not self.repository.remote:
            return 0

        bname = branch_name or self.active_branch
        if bname not in self.branches_remote:
            return 0

        git_cmd = f'git rev-list {remote_name}/{bname}..{bname} --count'
        result = call_subprocess(git_cmd.split(), cwd=self.repository.root_dir).strip()
        if result.isdigit():
            return int(result)
        else:
            raise BranchException(f"Unclear commits_ahead result: {result}")

    def get_commits_behind(self, branch_name: Optional[str] = None, remote_name: str = "origin") -> int:
        """Return to number of local commits not present in remote branch.

        Note! It is important to call fetch to ensure correct behavior here."""
        if not self.repository.remote:
            return 0

        bname = branch_name or self.active_branch
        if bname not in self.branches_remote:
            return 0

        git_cmd = f'git rev-list {bname}..{remote_name}/{bname} --count'
        result = call_subprocess(git_cmd.split(), cwd=self.repository.root_dir).strip()
        if result.isdigit():
            return int(result)
        else:
            raise BranchException(f"Unclear commits_behind result: {result}")

    # def get_commits_behind_remote(self, remote_name: str = "origin") -> Tuple[str, int]:
    #     """Return the number of commits local branch is behind remote. Note, only works with
    #     currently checked-out branch. If the local branch is AHEAD of the remote, returns a negative
    #     value.
    #
    #     Args:
    #         remote_name: Name of remote, e.g., "origin"
    #
    #     Returns:
    #         tuple containing branch name, and number of commits behind (zero implies up-to-date,
    #             negative implies local branch is ahead.)
    #     """
    #     # TODO(billvb/dmk/?) - This can be one-lined using some versions of GitPython
    #     # https://stackoverflow.com/questions/17224134/check-status-of-local-python-relative-to-remote-with-gitpython/21431791
    #     # However, it's not clear we will continue to use GitPython going forward or that this implementation
    #     # needs to change right now.
    #     try:
    #         if self.repository.has_remote:
    #             self.repository.git.fetch(remote=remote_name)
    #         result_str = self.repository.git.repo.git.status().replace('\n', ' ')
    #     except Exception as e:
    #         logger.exception(e)
    #         raise GigantumException(e)
    #
    #     if 'branch is up-to-date' in result_str:
    #         return self.active_branch, 0
    #     elif 'branch is behind' in result_str:
    #         m = re.search(' by ([\d]+) commit', result_str)
    #         if m:
    #             assert int(m.groups()[0]) > 0
    #             return self.active_branch, int(m.groups()[0])
    #         else:
    #             logger.error(f"Could not find count in: {result_str}")
    #             raise GigantumException("Unable to determine commit behind-count")
    #     elif 'branch is ahead of' in result_str:
    #         # Return NEGATIVE if your branch is ahead of remote
    #         m = re.search(' by ([\d]+) commit', result_str)
    #         if m:
    #             assert int(m.groups()[0]) > 0
    #             return self.active_branch, -1 * int(m.groups()[0])
    #         else:
    #             logger.error(f"Could not find count in: {result_str}")
    #             raise GigantumException("Unable to determine commit behind-count")
    #     elif 'your branch' in result_str.lower() and 'have diverged' in result_str.lower():
    #         # Note: In cases where there are divergent commits, it is too error-prone to
    #         # precisely parse the output for specific number of commits. So we just say,
    #         # technically, that we are behind by at least one commit. I.e., this is to
    #         # say "there is a pull required"
    #         return self.active_branch, 1
    #     else:
    #         # This branch is local-only
    #         return self.active_branch, 0
