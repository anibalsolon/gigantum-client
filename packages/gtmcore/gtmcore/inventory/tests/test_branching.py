import pytest
import os

from gtmcore.inventory.branching import (BranchManager, InvalidBranchName, BranchWorkflowViolation,
    BranchException)
from gtmcore.files import FileOperations
from gtmcore.fixtures import (mock_config_file, mock_labbook, mock_labbook_lfs_disabled,
                               mock_duplicate_labbook, remote_bare_repo, sample_src_file,
                               _MOCK_create_remote_repo2 as _MOCK_create_remote_repo,
                              remote_labbook_repo)

# If importing from remote, does new user's branch get created and does it push properly?

TEST_USER = 'test'


class TestBranching(object):

    def test_init_and_active_branch(self, mock_labbook_lfs_disabled):
        bm = BranchManager(mock_labbook_lfs_disabled[2], username=TEST_USER)
        assert bm.active_branch == f'gm.workspace-{TEST_USER}'
        assert bm.workspace_branch == f'gm.workspace-{TEST_USER}'

    def test_is_branch_name_valid(self):
        bad_strings = ['inval!id', '', '-', '---', '-' * 99, 'cats_' * 12, 'no--no', '-no-no-', 'yikes-' * 50 + 'a',
                       'bad!-bad!', 'no_way-*99', '`cat-99', "nope's-branch", 'nope"s-branch','No-Caps-Or-Anything',
                       'NO-CAPS-AT-ALL-99', 'Violà', 'Güten-Tag']
        for b in bad_strings:
            assert not BranchManager.is_branch_name_valid(b)
        good_strings = ['a', 'hello-there', 'yep-yep-yep', '99', 'hello-99-test', '2-33-44-55-66', 'experiment4',
                        'experiment-4', 'über-weird-name-should-this-work-hmm']
        for g in good_strings:
            assert BranchManager.is_branch_name_valid(g)

    def test_create_branch(self, mock_labbook_lfs_disabled):
        t = "my-first-feature-branch"
        lb = mock_labbook_lfs_disabled[2]
        bm = BranchManager(lb, username=TEST_USER)
        assert bm.active_branch == f'gm.workspace-{TEST_USER}'
        bm.create_branch(title=f"gm.workspace-{TEST_USER}.{t}")
        assert bm.active_branch == f'gm.workspace-{TEST_USER}.{t}'
        assert lb.is_repo_clean is True

    def test_success_create_branch_then_workon_original(self, mock_labbook_lfs_disabled):
        t = 'my-new-example-feature'
        lb = mock_labbook_lfs_disabled[2]
        bm = BranchManager(lb, username=TEST_USER)
        assert bm.active_branch == f'gm.workspace-{TEST_USER}'
        full_branch = bm.create_branch(title=f'gm.workspace-{TEST_USER}.{t}')
        assert lb.is_repo_clean

        bm.workon_branch(bm.workspace_branch)
        assert bm.active_branch == f'gm.workspace-{TEST_USER}'
        assert lb.active_branch == f'gm.workspace-{TEST_USER}'
        assert lb.is_repo_clean

        bm.workon_branch(full_branch)
        assert bm.active_branch == full_branch
        assert lb.active_branch == full_branch
        assert lb.is_repo_clean

    def test_success_merge_from_and_remove_branch(self, mock_labbook_lfs_disabled):
        t = 'my-new-example-feature'
        lb = mock_labbook_lfs_disabled[2]
        bm = BranchManager(lb, username=TEST_USER)
        branch_name = bm.create_branch(title=f'gm.workspace-{TEST_USER}.{t}')

        bm.workon_branch(bm.workspace_branch)
        FileOperations.makedir(lb, 'code/sillyfolder', create_activity_record=True)
        FileOperations.makedir(lb, 'input/newfolder', create_activity_record=True)

        bm.workon_branch(branch_name)
        FileOperations.makedir(lb, 'output/otherdir', create_activity_record=True)
        bm.merge_from(bm.workspace_branch)
        assert os.path.isdir(os.path.join(lb.root_dir, 'code/sillyfolder'))
        assert os.path.isdir(os.path.join(lb.root_dir, 'input/newfolder'))
        assert os.path.isdir(os.path.join(lb.root_dir, 'output/otherdir'))
        assert lb.is_repo_clean

        bm.workon_branch(bm.workspace_branch)
        assert lb.is_repo_clean

        bm.remove_branch(branch_name)
        assert not branch_name in bm.branches
        assert lb.is_repo_clean

    def test_merge_conflics_1(self, mock_labbook_lfs_disabled):

        # In the main branch, make some file
        with open('/tmp/s1.txt', 'w') as s1:
            s1.write('original-file\ndata')
        test_user_lb = mock_labbook_lfs_disabled[2]
        FileOperations.insert_file(test_user_lb, section='code', src_file=s1.name)

        # Create a new branch and make a change to s1.txt
        bm = BranchManager(test_user_lb, username=TEST_USER)
        new_b = bm.create_branch("gm.workspace-test.example-feature-branch")
        with open('/tmp/s1.txt', 'w') as s1:
            s1.write('new-changes-in\nfeature-branch')
        FileOperations.insert_file(test_user_lb, section='code', src_file=s1.name)
        with open(os.path.join(test_user_lb.root_dir, 'output/sample'), 'w') as f:
            f.write('sample data in a file not explicity added - this should be swept up.')
        assert not test_user_lb.is_repo_clean

        # Switch back to the main branch
        bm.workon_branch(bm.workspace_branch)
        assert test_user_lb.is_repo_clean
        assert not os.path.exists(os.path.join(test_user_lb.root_dir, 'output/sample'))
        with open('/tmp/s1.txt', 'w') as s1:
            s1.write('upstream-changes-from-workspace')
        FileOperations.insert_file(test_user_lb, section='code', src_file=s1.name, dst_path='')

        # Switch back to feature branch -- make sure that failed merges rollback to state before merge.
        bm.workon_branch(new_b)
        assert test_user_lb.is_repo_clean
        with pytest.raises(BranchException):
            bm.merge_from(bm.workspace_branch)
        assert test_user_lb.is_repo_clean

        bm.merge_from(bm.workspace_branch, force=True)
        assert open(os.path.join(test_user_lb.root_dir, 'code', 's1.txt')).read(1000) == \
            'upstream-changes-from-workspace'
        assert test_user_lb.is_repo_clean

        # Finally remove that feature branch.
        with pytest.raises(BranchWorkflowViolation):
            bm.remove_branch(bm.workspace_branch)

        with pytest.raises(BranchWorkflowViolation):
            bm.remove_branch(new_b)

        bm.workon_branch(bm.workspace_branch)
        assert test_user_lb.is_repo_clean
        bm.remove_branch(new_b)
        assert not new_b in bm.branches

    def test_success_rollback_branch(self, mock_labbook_lfs_disabled):
        test_user_lb = mock_labbook_lfs_disabled[2]

        FileOperations.makedir(test_user_lb, relative_path='code/folder1', create_activity_record=True)
        commit = test_user_lb.git.commit_hash
        FileOperations.makedir(test_user_lb, relative_path='code/folder2', create_activity_record=True)
        FileOperations.makedir(test_user_lb, relative_path='code/folder3', create_activity_record=True)

        bm = BranchManager(test_user_lb, username=TEST_USER)
        new_b = bm.create_branch('gm.workspace-test.rollback-from-folder-1', revision=commit)
        FileOperations.makedir(test_user_lb, relative_path='input/branch-folder', create_activity_record=True)
        assert os.path.exists(os.path.join(test_user_lb.root_dir, 'code/folder1'))
        assert not os.path.exists(os.path.join(test_user_lb.root_dir, 'code/folder2'))
        assert not os.path.exists(os.path.join(test_user_lb.root_dir, 'code/folder3'))

        assert new_b == bm.active_branch
        FileOperations.makedir(test_user_lb, relative_path='input/branch-1', create_activity_record=True)
        FileOperations.makedir(test_user_lb, relative_path='input/branch-2', create_activity_record=True)
        FileOperations.makedir(test_user_lb, relative_path='input/branch-3', create_activity_record=True)
        assert test_user_lb.is_repo_clean

        # Now try pulling upstream changes back into the rollback branch
        bm.merge_from(bm.workspace_branch)
        assert test_user_lb.is_repo_clean
        assert os.path.exists(os.path.join(test_user_lb.root_dir, 'code/folder2'))
        assert os.path.exists(os.path.join(test_user_lb.root_dir, 'code/folder3'))
        assert os.path.exists(os.path.join(test_user_lb.root_dir, 'input/branch-1'))
        assert os.path.exists(os.path.join(test_user_lb.root_dir, 'input/branch-2'))
        assert os.path.exists(os.path.join(test_user_lb.root_dir, 'input/branch-3'))
        assert test_user_lb.is_repo_clean

        bm.workon_branch(bm.workspace_branch)
        assert test_user_lb.is_repo_clean

    def test_fail_create_rollback_to_invalid_revision(self, mock_labbook_lfs_disabled):
        test_user_lb = mock_labbook_lfs_disabled[2]
        FileOperations.makedir(test_user_lb, relative_path='code/folder1', create_activity_record=True)
        commit = test_user_lb.git.commit_hash
        FileOperations.makedir(test_user_lb, relative_path='code/folder2', create_activity_record=True)
        FileOperations.makedir(test_user_lb, relative_path='code/folder3', create_activity_record=True)

        bm = BranchManager(test_user_lb, username=TEST_USER)
        with pytest.raises(InvalidBranchName):
            bm.create_branch('gm.workspace-test.should-fail', revision='invalidrevision')

    def test_assert_all_branches_can_be_checked_out(self, mock_config_file, remote_labbook_repo,
                                                        mock_labbook_lfs_disabled):
        # Make sure all local branches can be checked out
        lb = mock_labbook_lfs_disabled[2]
        bm = BranchManager(lb, username='test')
        for branch_name in bm.branches:
            bm.workon_branch(branch_name)

        # Make sure all remote branches can be checked out
        # TODO(billvb): Perhaps get branches should strip the "origin/" prefix for remotes
        lb.add_remote("origin", remote_labbook_repo)
        for branch_name in [b.replace('origin/', '') for b in bm.branches]:
            bm.workon_branch(branch_name)

    def test_get_commits_with_local_changes(self, mock_config_file, remote_labbook_repo,
                                            mock_labbook_lfs_disabled):
        # When the branch is up to date, ensure it doesn't report being behind.
        lb = mock_labbook_lfs_disabled[2]
        lb.add_remote("origin", remote_labbook_repo)
        bm = BranchManager(lb, username='test')
        bm.workon_branch("gm.workspace-test.testing-branch")

        # Do some stuff to make commits locally
        FileOperations.makedir(lb, 'code/rand_dir', create_activity_record=True)
        FileOperations.delete_files(lb, 'code', ['rand_dir'])

        # Assert local branch is AHEAD of remote
        r = bm.get_commits_behind_remote("origin")
        assert 'gm.workspace-test.testing-branch' == r[0]
        assert -4 == r[1]

    def test_get_commits_with_remote_changes(self, mock_config_file, remote_labbook_repo,
                                             mock_labbook_lfs_disabled):
        # When the branch is up to date, ensure it doesn't report being behind.
        lb = mock_labbook_lfs_disabled[2]
        lb.add_remote("origin", remote_labbook_repo)
        bm = BranchManager(lb, username='test')
        bm.workon_branch("gm.workspace-test.testing-branch")

        from gtmcore.inventory.inventory import InventoryManager
        remote_lb = InventoryManager(mock_config_file[0]).load_labbook_from_directory(remote_labbook_repo)
        remote_bm = BranchManager(remote_lb, 'test')
        remote_bm.workon_branch("gm.workspace-test.testing-branch")
        FileOperations.makedir(remote_lb, 'code/xyzdir', create_activity_record=True)

        # Assert local branch is AHEAD of remote
        r = bm.get_commits_behind_remote("origin")
        assert 'gm.workspace-test.testing-branch' == r[0]
        assert 2 == r[1]

    def test_count_commits_behind_remote_when_no_change(self, mock_config_file, remote_labbook_repo,
                                                        mock_labbook_lfs_disabled):
        # When the branch is up to date, ensure it doesn't report being behind.
        lb = mock_labbook_lfs_disabled[2]
        bm = BranchManager(lb, username='test')
        bm.create_branch("gm.workspace-test.testing-branch")
        lb.add_remote("origin", remote_labbook_repo)

        r = bm.get_commits_behind_remote("origin")
        assert r[0] == 'gm.workspace-test.testing-branch'
        # Should be up-to-date.
        assert r[1] == 0

    def test_count_commits_behind_for_local_branch(self, mock_config_file, remote_labbook_repo,
                                                   mock_labbook_lfs_disabled):
        # When we're using a local branch, by definition it is never behind.
        lb = mock_labbook_lfs_disabled[2]
        bm = BranchManager(lb, username='test')
        lb.add_remote("origin", remote_labbook_repo)
        bm.create_branch("super-local-branch")

        r = bm.get_commits_behind_remote("origin")
        assert r[0] == 'super-local-branch'
        # Should be up-to-date.
        assert r[1] == 0
