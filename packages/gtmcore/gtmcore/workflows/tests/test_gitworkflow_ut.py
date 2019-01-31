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
# OUT OF OR IN CO
import pytest
import mock
import time
import os

from gtmcore.configuration.utils import call_subprocess
from gtmcore.workflows import GitWorkflowException, LabbookWorkflow, DatasetWorkflow, MergeError, MergeOverride
from gtmcore.fixtures import (_MOCK_create_remote_repo2 as _MOCK_create_remote_repo, mock_labbook_lfs_disabled,
                              mock_config_file)
from gtmcore.inventory.branching import BranchManager, MergeConflict


class TestGitWorkflowsMethods(object):

    @mock.patch('gtmcore.workflows.gitworkflows_utils.create_remote_gitlab_repo', new=_MOCK_create_remote_repo)
    def test_publish__simple(self, mock_labbook_lfs_disabled):
        """Test a simple publish and ensuring master is active branch. """
        username = 'test'
        lb = mock_labbook_lfs_disabled[2]
        bm = BranchManager(lb, username)
        bm.create_branch('test-local-only')
        assert bm.branches_remote == []
        assert bm.branches_local == ['master', 'test-local-only']

        wf = LabbookWorkflow(lb)

        # Test you can only publish on master.
        with pytest.raises(GitWorkflowException):
            wf.publish(username=username)
        assert wf.remote is None

        # Once we return to master branch, then we can publish.
        bm.workon_branch(bm.workspace_branch)
        wf.publish(username=username)
        assert os.path.exists(wf.remote)

        # Assert that publish only pushes up the master branch.
        assert bm.branches_local == ['master', 'test-local-only']
        assert bm.branches_remote == ['master']

    @mock.patch('gtmcore.workflows.gitworkflows_utils.create_remote_gitlab_repo', new=_MOCK_create_remote_repo)
    def test_publish__cannot_overwrite(self, mock_labbook_lfs_disabled):
        """ Test cannot publish a project already published. """
        username = 'test'
        lb = mock_labbook_lfs_disabled[2]
        wf = LabbookWorkflow(lb)
        wf.publish(username=username)
        with pytest.raises(GitWorkflowException):
            wf.publish(username=username)

    @mock.patch('gtmcore.workflows.gitworkflows_utils.create_remote_gitlab_repo', new=_MOCK_create_remote_repo)
    def test_publish__publish_then_import_with_another_user(self, mock_labbook_lfs_disabled, mock_config_file):
        """ Test cannot publish a project already published. """
        username = 'test'
        lb = mock_labbook_lfs_disabled[2]
        wf = LabbookWorkflow(lb)
        wf.publish(username=username)

        other_user = 'other-test-user'
        wf_other = LabbookWorkflow.import_from_remote(remote_url=wf.remote, username=other_user,
                                                      config_file=mock_config_file[0])
        lb_other = wf_other.repository
        assert lb_other.root_dir != lb.root_dir

    @mock.patch('gtmcore.workflows.gitworkflows_utils.create_remote_gitlab_repo', new=_MOCK_create_remote_repo)
    def test_publish__publish_then_import_then_sync(self, mock_labbook_lfs_disabled, mock_config_file):
        """ Test cannot publish a project already published. """
        username = 'test'
        lb = mock_labbook_lfs_disabled[2]
        wf = LabbookWorkflow(lb)
        wf.publish(username=username)

        other_user = 'other-test-user'
        wf_other = LabbookWorkflow.import_from_remote(remote_url=wf.remote, username=other_user,
                                                      config_file=mock_config_file[0])
        with open(os.path.join(wf_other.repository.root_dir, 'testfile'), 'w') as f: f.write('filedata')
        wf_other.repository.sweep_uncommitted_changes()

        wf_other.sync(username=other_user)
        commit_hash = wf_other.repository.git.commit_hash

        assert wf.repository.git.commit_hash != commit_hash
        wf.sync(username=username)
        assert len(wf.repository.git.commit_hash) == len(commit_hash)
        assert wf.repository.git.commit_hash == commit_hash

    @mock.patch('gtmcore.workflows.gitworkflows_utils.create_remote_gitlab_repo', new=_MOCK_create_remote_repo)
    def test_import_from_remote__nominal(self, mock_labbook_lfs_disabled, mock_config_file):
        """ test import_from_remote method """
        username = 'testuser'
        lb = mock_labbook_lfs_disabled[2]
        wf = LabbookWorkflow(lb)
        wf.publish(username=username)

        other_user = 'other-test-user2'
        wf_other = LabbookWorkflow.import_from_remote(wf.remote, username=other_user,
                                                      config_file=mock_config_file[0])
        # The remotes must be the same, cause it's the same remote repo
        assert wf_other.remote == wf.remote
        # The actual path on disk will be different, though
        assert wf_other.repository != wf.repository
        # Check imported into namespace of original owner (testuser)
        assert 'testuser/labbooks/labbook1' in wf_other.repository.root_dir

    @mock.patch('gtmcore.workflows.gitworkflows_utils.create_remote_gitlab_repo', new=_MOCK_create_remote_repo)
    def test_import_from_remote__dataset(self, mock_labbook_lfs_disabled, mock_config_file):
        """ test import_from_remote method """
        assert False

    @mock.patch('gtmcore.workflows.gitworkflows_utils.create_remote_gitlab_repo', new=_MOCK_create_remote_repo)
    def test_sync___simple_push_to_master(self, mock_labbook_lfs_disabled, mock_config_file):
        """ test import_from_remote method """
        username = 'test'
        lb = mock_labbook_lfs_disabled[2]
        wf = LabbookWorkflow(lb)
        wf.publish(username=username)
        fpath = os.path.join(lb.root_dir, 'input', 'testfile')
        with open(fpath, 'w') as f: f.write('filedata')
        lb.sweep_uncommitted_changes()
        wf.sync(username=username)

        # Check hash on remote - make sure it matches local.
        remote_hash = call_subprocess('git log -n 1 --oneline'.split(), cwd=wf.remote).split()[0]
        assert remote_hash in lb.git.commit_hash

    @mock.patch('gtmcore.workflows.gitworkflows_utils.create_remote_gitlab_repo', new=_MOCK_create_remote_repo)
    def test_sync___push_up_new_branch(self, mock_labbook_lfs_disabled, mock_config_file):
        """ test import_from_remote method """
        username = 'test'
        lb = mock_labbook_lfs_disabled[2]
        wf = LabbookWorkflow(lb)
        wf.publish(username=username)
        bm = BranchManager(lb, username='test')
        bm.create_branch('new-branch-to-push')
        assert 'new-branch-to-push' not in bm.branches_remote
        wf.sync('test')
        assert 'new-branch-to-push' in bm.branches_remote

    @mock.patch('gtmcore.workflows.gitworkflows_utils.create_remote_gitlab_repo', new=_MOCK_create_remote_repo)
    def test_sync___push_up_then_sync(self, mock_labbook_lfs_disabled, mock_config_file):
        """ test import_from_remote method """
        username = 'test'
        lb = mock_labbook_lfs_disabled[2]
        wf = LabbookWorkflow(lb)
        wf.publish(username=username)
        bm = BranchManager(lb, username='test')
        bm.create_branch('new-branch-to-push')
        wf.sync('test')

        # Make some change locally and commit, then sync.
        fpath = os.path.join(lb.root_dir, 'input', 'testfile')
        with open(fpath, 'w') as f: f.write('filedata')
        lb.sweep_uncommitted_changes()
        wf.sync(username=username)

    @mock.patch('gtmcore.workflows.gitworkflows_utils.create_remote_gitlab_repo', new=_MOCK_create_remote_repo)
    def test_sync___detect_merge_conflict(self, mock_labbook_lfs_disabled, mock_config_file):
        """ test import_from_remote method """
        username = 'test'
        lb = mock_labbook_lfs_disabled[2]
        wf = LabbookWorkflow(lb)
        wf.publish(username=username)
        bm = BranchManager(lb, username='test')
        bm.create_branch('test-conflict-branch')
        fpath = os.path.join(lb.root_dir, 'input', 'testfile')
        with open(fpath, 'w') as f: f.write('filedata')
        lb.sweep_uncommitted_changes()
        wf.sync('test')

        other_user = 'other-test-user2'
        wf_other = LabbookWorkflow.import_from_remote(wf.remote, username=other_user,
                                                      config_file=mock_config_file[0])
        bm_other = BranchManager(wf_other.labbook, username=other_user)
        bm_other.workon_branch('test-conflict-branch')
        with open(os.path.join(wf_other.labbook.root_dir, 'input', 'testfile'), 'w') as f:
            f.write('conflicting-change-other-user')
        wf_other.labbook.sweep_uncommitted_changes()
        wf_other.sync(username=username)

        with open(fpath, 'w') as f: f.write('conflicting-change-original-user')
        wf.labbook.sweep_uncommitted_changes()
        h = wf.labbook.git.commit_hash
        with pytest.raises(MergeConflict):
            n = wf.sync(username=username)
        assert h == wf.labbook.git.commit_hash

    @mock.patch('gtmcore.workflows.gitworkflows_utils.create_remote_gitlab_repo', new=_MOCK_create_remote_repo)
    def test_sync___override_merge_conflict_theirs(self, mock_labbook_lfs_disabled, mock_config_file):
        """ test sync, with override in case of merge conflict. """
        """ test import_from_remote method """
        username = 'test'
        lb = mock_labbook_lfs_disabled[2]
        wf = LabbookWorkflow(lb)
        wf.publish(username=username)
        bm = BranchManager(lb, username='test')
        bm.create_branch('test-conflict-branch')
        fpath = os.path.join(lb.root_dir, 'input', 'testfile')
        with open(fpath, 'w') as f: f.write('filedata')
        lb.sweep_uncommitted_changes()
        wf.sync('test')

        other_user = 'other-test-user2'
        wf_other = LabbookWorkflow.import_from_remote(wf.remote, username=other_user,
                                                      config_file=mock_config_file[0])
        bm_other = BranchManager(wf_other.labbook, username=other_user)
        bm_other.workon_branch('test-conflict-branch')
        with open(os.path.join(wf_other.labbook.root_dir, 'input', 'testfile'), 'w') as f:
            f.write('conflicting-change-other-user')
        wf_other.labbook.sweep_uncommitted_changes()
        wf_other.sync(username=username)

        assert wf_other.repository.root_dir != wf.repository.root_dir
        fpath = os.path.join(wf.labbook.root_dir, 'input', 'testfile')
        with open(fpath, 'w') as f: f.write('conflicting-change-original-user')
        wf.labbook.sweep_uncommitted_changes()
        assert wf.labbook.is_repo_clean
        h = wf.labbook.git.commit_hash

        n = wf.sync(username=username, override=MergeOverride.THEIRS)
        assert h != wf.labbook.git.commit_hash
        flines = open(os.path.join(wf.labbook.root_dir, 'input', 'testfile')).read()
        assert 'conflicting-change-other-user' == flines

    @mock.patch('gtmcore.workflows.gitworkflows_utils.create_remote_gitlab_repo', new=_MOCK_create_remote_repo)
    def test_sync___override_merge_conflict_ours(self, mock_labbook_lfs_disabled, mock_config_file):
        """ test sync, with override in case of merge conflict. """
        username = 'test'
        lb = mock_labbook_lfs_disabled[2]
        wf = LabbookWorkflow(lb)
        wf.publish(username=username)
        bm = BranchManager(lb, username='test')
        bm.create_branch('test-conflict-branch')
        fpath = os.path.join(lb.root_dir, 'input', 'testfile')
        with open(fpath, 'w') as f: f.write('filedata')
        lb.sweep_uncommitted_changes()
        wf.sync('test')

        other_user = 'other-test-user2'
        wf_other = LabbookWorkflow.import_from_remote(wf.remote, username=other_user,
                                                      config_file=mock_config_file[0])
        bm_other = BranchManager(wf_other.labbook, username=other_user)
        bm_other.workon_branch('test-conflict-branch')
        with open(os.path.join(wf_other.labbook.root_dir, 'input', 'testfile'), 'w') as f:
            f.write('conflicting-change-other-user')
        wf_other.labbook.sweep_uncommitted_changes()
        wf_other.sync(username=username)

        fpath = os.path.join(wf.labbook.root_dir, 'input', 'testfile')
        with open(fpath, 'w') as f: f.write('conflicting-change-original-user')
        wf.labbook.sweep_uncommitted_changes()
        n = wf.sync(username=username, override=MergeOverride.OURS)
        flines = open(os.path.join(wf.labbook.root_dir, 'input', 'testfile')).read()
        assert 'conflicting-change-original-user' == flines

    @mock.patch('gtmcore.workflows.gitworkflows_utils.create_remote_gitlab_repo', new=_MOCK_create_remote_repo)
    def test_reset__no_op(self, mock_labbook_lfs_disabled, mock_config_file):
        """ test reset performs no operation when there's nothing to do """
        username = 'test'
        lb = mock_labbook_lfs_disabled[2]
        wf = LabbookWorkflow(lb)
        wf.reset(username=username)
        wf.publish(username=username)

    @mock.patch('gtmcore.workflows.gitworkflows_utils.create_remote_gitlab_repo', new=_MOCK_create_remote_repo)
    def test_reset__reset_local_change_same_owner(self, mock_labbook_lfs_disabled, mock_config_file):
        """ test reset performs no operation when there's nothing to do """
        username = 'test'
        lb = mock_labbook_lfs_disabled[2]
        wf = LabbookWorkflow(lb)
        wf.publish(username=username)
        commit_to_check = lb.git.commit_hash

        # Make some change locally and commit
        fpath = os.path.join(lb.root_dir, 'input', 'testfile')
        with open(fpath, 'w') as f:
            f.write('filedata')
        lb.sweep_uncommitted_changes()
        assert lb.git.commit_hash != commit_to_check

        # Make an UNTRACKED change locally, make sure it gets clared up
        untracked_file = os.path.join(lb.root_dir, 'output', 'untracked-file')
        with open(untracked_file, 'w') as f:
            f.write('untracked data')

        # Do a reset and make sure state resets appropriately
        wf.reset(username=username)
        assert lb.git.commit_hash == commit_to_check
        assert not os.path.exists(fpath)
        assert not os.path.exists(untracked_file)
        remote_hash = call_subprocess('git log -n 1 --oneline'.split(), cwd=wf.remote).split()[0]
        assert remote_hash in lb.git.commit_hash

