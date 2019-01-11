import pytest
import os
from collections import OrderedDict

from gtmcore.dataset import Manifest
from gtmcore.fixtures.datasets import mock_dataset_with_cache_dir, mock_dataset_with_cache_mgr, helper_append_file, \
    USERNAME


class TestManifest(object):
    def test_init(self, mock_dataset_with_cache_mgr):
        ds, cache_mgr, revision = mock_dataset_with_cache_mgr

        m = Manifest(ds, USERNAME)

        assert isinstance(m.manifest, OrderedDict)
        assert m.dataset_revision == ds.git.repo.head.commit.hexsha

    def test_status_created_files(self, mock_dataset_with_cache_mgr):
        ds, cache_mgr, revision = mock_dataset_with_cache_mgr
        m = Manifest(ds, USERNAME)

        os.makedirs(os.path.join(cache_mgr.cache_root, revision, "test_dir"))
        os.makedirs(os.path.join(cache_mgr.cache_root, revision, "other_dir"))
        os.makedirs(os.path.join(cache_mgr.cache_root, revision, "test_dir", "nested"))
        helper_append_file(cache_mgr.cache_root, revision, "test1.txt", "asdfasdf")
        helper_append_file(cache_mgr.cache_root, revision, "test2.txt", "dfg")
        helper_append_file(cache_mgr.cache_root, revision, "test_dir/test3.txt", "asdffdgfghghfjjgh")
        helper_append_file(cache_mgr.cache_root, revision, "test_dir/nested/test4.txt", "565656565")
        helper_append_file(cache_mgr.cache_root, revision, "other_dir/test5.txt", "dfasdfhfgjhg")

        status = m.status()
        assert len(status.created) == 5
        assert len(status.modified) == 0
        assert len(status.deleted) == 0

        assert "test1.txt" in status.created
        assert "test2.txt" in status.created
        assert "test_dir/test3.txt" in status.created
        assert "test_dir/nested/test4.txt" in status.created
        assert "other_dir/test5.txt" in status.created

    def test_update_simple(self, mock_dataset_with_cache_mgr):
        ds, cache_mgr, revision = mock_dataset_with_cache_mgr
        m = Manifest(ds, USERNAME)

        helper_append_file(cache_mgr.cache_root, revision, "test1.txt", "asdfasdf")

        status = m.status()
        assert len(status.created) == 1
        assert len(status.modified) == 0
        assert len(status.deleted) == 0

        assert "test1.txt" in status.created

        m.update(status=status)

        status = m.status()
        assert len(status.created) == 0
        assert len(status.modified) == 0
        assert len(status.deleted) == 0

        helper_append_file(cache_mgr.cache_root, revision, "test1.txt", "asdfasdf")

        status = m.status()
        assert len(status.created) == 0
        assert len(status.modified) == 1
        assert len(status.deleted) == 0

        m.update()

        status = m.status()
        assert len(status.created) == 0
        assert len(status.modified) == 0
        assert len(status.deleted) == 0

    def test_status_deleted_files(self, mock_dataset_with_cache_mgr):
        ds, cache_mgr, revision = mock_dataset_with_cache_mgr
        m = Manifest(ds, USERNAME)

        helper_append_file(cache_mgr.cache_root, revision, "test1.txt", "asdfasdf")

        status = m.status()
        assert len(status.created) == 1
        assert len(status.modified) == 0
        assert len(status.deleted) == 0

        assert "test1.txt" in status.created

        m.update(status=status)

        status = m.status()
        assert len(status.created) == 0
        assert len(status.modified) == 0
        assert len(status.deleted) == 0

        os.remove(os.path.join(cache_mgr.cache_root, revision, "test1.txt"))

        status = m.status()
        assert len(status.created) == 0
        assert len(status.modified) == 0
        assert len(status.deleted) == 1

        m.update()

        status = m.status()
        assert len(status.created) == 0
        assert len(status.modified) == 0
        assert len(status.deleted) == 0

    def test_update_complex(self, mock_dataset_with_cache_mgr):
        ds, cache_mgr, revision = mock_dataset_with_cache_mgr
        m = Manifest(ds, USERNAME)

        os.makedirs(os.path.join(cache_mgr.cache_root, revision, "test_dir"))
        os.makedirs(os.path.join(cache_mgr.cache_root, revision, "other_dir"))
        os.makedirs(os.path.join(cache_mgr.cache_root, revision, "test_dir", "nested"))
        helper_append_file(cache_mgr.cache_root, revision, "test1.txt", "asdfasdf")
        helper_append_file(cache_mgr.cache_root, revision, "test2.txt", "dfg")
        helper_append_file(cache_mgr.cache_root, revision, "test_dir/test3.txt", "asdffdgfghghfjjgh")
        helper_append_file(cache_mgr.cache_root, revision, "test_dir/nested/test4.txt", "565656565")
        helper_append_file(cache_mgr.cache_root, revision, "other_dir/test5.txt", "dfasdfhfgjhg")

        status = m.status()
        assert len(status.created) == 5
        assert len(status.modified) == 0
        assert len(status.deleted) == 0

        assert "test1.txt" in status.created
        assert "test2.txt" in status.created
        assert "test_dir/test3.txt" in status.created
        assert "test_dir/nested/test4.txt" in status.created
        assert "other_dir/test5.txt" in status.created

        m.update()

        status = m.status()
        assert len(status.created) == 0
        assert len(status.modified) == 0
        assert len(status.deleted) == 0

        helper_append_file(cache_mgr.cache_root, revision, "test99.txt", "ghghgh")
        helper_append_file(cache_mgr.cache_root, revision, "test2.txt", "dfghghgfg")
        os.remove(os.path.join(cache_mgr.cache_root, revision, "test_dir", "nested", "test4.txt"))

        status = m.status()
        assert len(status.created) == 1
        assert len(status.modified) == 1
        assert len(status.deleted) == 1
        assert "test99.txt" in status.created
        assert "test2.txt" in status.modified
        assert "test_dir/nested/test4.txt" in status.deleted

        assert os.path.exists(os.path.join(cache_mgr.cache_root, revision, "test_dir", "nested", "test4.txt")) is False
        assert os.path.exists(os.path.join(cache_mgr.cache_root, revision, "test99.txt")) is True

        m.update()

        status = m.status()
        assert len(status.created) == 0
        assert len(status.modified) == 0
        assert len(status.deleted) == 0

    def test_list(self, mock_dataset_with_cache_mgr):
        ds, cache_mgr, revision = mock_dataset_with_cache_mgr
        m = Manifest(ds, USERNAME)

        os.makedirs(os.path.join(cache_mgr.cache_root, revision, "other_dir"))
        helper_append_file(cache_mgr.cache_root, revision, "test1.txt", "asdfasdf")
        helper_append_file(cache_mgr.cache_root, revision, "test2.txt", "asdfasdf")
        helper_append_file(cache_mgr.cache_root, revision, "test3.txt", "asdfasdf")
        helper_append_file(cache_mgr.cache_root, revision, "other_dir/test4.txt", "dfasdfhfgjhg")
        helper_append_file(cache_mgr.cache_root, revision, "other_dir/test5.txt", "fdghdfgsa")
        m.update()

        file_info = m.list()
        assert len(file_info) == 5
        assert file_info[2]['key'] == "test1.txt"
        assert file_info[2]['size'] == '8'
        assert file_info[2]['is_favorite'] is False
        assert file_info[2]['is_local'] is True
        assert file_info[2]['is_dir'] is False
        assert 'modified_at' in file_info[2]
        assert file_info[0]['key'] == "other_dir/test4.txt"
        assert file_info[1]['key'] == "other_dir/test5.txt"
        assert file_info[3]['key'] == "test2.txt"
        assert file_info[4]['key'] == "test3.txt"

        file_info = m.list(first=1)
        assert len(file_info) == 1
        assert file_info[0]['key'] == "other_dir/test4.txt"

        file_info = m.list(first=2)
        assert len(file_info) == 2
        assert file_info[0]['key'] == "other_dir/test4.txt"
        assert file_info[1]['key'] == "other_dir/test5.txt"

        file_info = m.list(first=3, after_index=2)
        assert len(file_info) == 3
        assert file_info[0]['key'] == "test1.txt"
        assert file_info[1]['key'] == "test2.txt"
        assert file_info[2]['key'] == "test3.txt"

        file_info = m.list(first=300, after_index=3)
        assert len(file_info) == 2
        assert file_info[0]['key'] == "test2.txt"
        assert file_info[1]['key'] == "test3.txt"

        os.remove(os.path.join(cache_mgr.cache_root, revision, "test1.txt"))
        file_info = m.list()
        assert len(file_info) == 5
        assert file_info[2]['key'] == "test1.txt"
        assert file_info[2]['size'] == '8'
        assert file_info[2]['is_favorite'] is False
        assert file_info[2]['is_local'] is False
        assert file_info[2]['is_dir'] is False

    def test_get(self, mock_dataset_with_cache_mgr):
        ds, cache_mgr, revision = mock_dataset_with_cache_mgr
        m = Manifest(ds, USERNAME)

        os.makedirs(os.path.join(cache_mgr.cache_root, revision, "other_dir"))
        helper_append_file(cache_mgr.cache_root, revision, "test1.txt", "asdfasdf")
        helper_append_file(cache_mgr.cache_root, revision, "other_dir/test4.txt", "dfasdfhfgjhg")
        m.update()

        file_info = m.get("test1.txt")
        assert file_info['key'] == "test1.txt"
        assert file_info['size'] == '8'
        assert file_info['is_favorite'] is False
        assert file_info['is_local'] is True
        assert file_info['is_dir'] is False
        assert 'modified_at' in file_info

        file_info = m.get("other_dir/test4.txt")
        assert file_info['key'] == "other_dir/test4.txt"

    def test_file_info_from_filesystem(self, mock_dataset_with_cache_mgr):
        ds, cache_mgr, revision = mock_dataset_with_cache_mgr
        m = Manifest(ds, USERNAME)

        os.makedirs(os.path.join(cache_mgr.cache_root, revision, "other_dir"))
        helper_append_file(cache_mgr.cache_root, revision, "test1.txt", "asdfasdf")
        helper_append_file(cache_mgr.cache_root, revision, "other_dir/test4.txt", "dfasdfhfgjhg")

        file_info = m.gen_file_info("test1.txt")
        assert file_info['key'] == "test1.txt"
        assert file_info['size'] == '8'
        assert file_info['is_favorite'] is False
        assert file_info['is_local'] is True
        assert file_info['is_dir'] is False
        assert 'modified_at' in file_info

        file_info = m.gen_file_info("other_dir/test4.txt")
        assert file_info['key'] == "other_dir/test4.txt"

    def test_sweep_all_changes(self, mock_dataset_with_cache_mgr):
        ds, cache_mgr, revision = mock_dataset_with_cache_mgr
        m = Manifest(ds, USERNAME)

        os.makedirs(os.path.join(cache_mgr.cache_root, revision, "other_dir"))
        helper_append_file(cache_mgr.cache_root, revision, "test1.txt", "asdfasdfdf")
        helper_append_file(cache_mgr.cache_root, revision, "test2.txt", "asdfdf")
        helper_append_file(cache_mgr.cache_root, revision, "test3.txt", "asdfasdf")
        helper_append_file(cache_mgr.cache_root, revision, "other_dir/test4.txt", "dfasdfhfgjhg")
        helper_append_file(cache_mgr.cache_root, revision, "other_dir/test5.txt", "fdghdfgsa")

        assert len(ds.git.log()) == 4

        status = m.status()
        assert len(status.created) == 5
        assert len(status.modified) == 0
        assert len(status.deleted) == 0
        m.sweep_all_changes()
        status = m.status()
        assert len(status.created) == 0
        assert len(status.modified) == 0
        assert len(status.deleted) == 0

        helper_append_file(cache_mgr.cache_root, m.dataset_revision, "test1.txt", "asdfafdfdfdfdsdf")
        status = m.status()
        assert len(status.created) == 0
        assert len(status.modified) == 1
        assert len(status.deleted) == 0
        m.sweep_all_changes()
        status = m.status()
        assert len(status.created) == 0
        assert len(status.modified) == 0
        assert len(status.deleted) == 0

        os.remove(os.path.join(cache_mgr.cache_root, m.dataset_revision, "test1.txt"))
        status = m.status()
        assert len(status.created) == 0
        assert len(status.modified) == 0
        assert len(status.deleted) == 1
        m.sweep_all_changes()
        status = m.status()
        assert len(status.created) == 0
        assert len(status.modified) == 0
        assert len(status.deleted) == 0

        num_records = len(ds.git.log())

        # Should run again, doing nothing and creation 0 new activity records
        m.sweep_all_changes()
        assert num_records == len(ds.git.log())

    @pytest.mark.skip("Currently writing to files when dups exists causes issues with status due to links")
    def test_sweep_all_changes_with_dup_files(self, mock_dataset_with_cache_mgr):
        ds, cache_mgr, revision = mock_dataset_with_cache_mgr
        m = Manifest(ds, USERNAME)

        os.makedirs(os.path.join(cache_mgr.cache_root, revision, "other_dir"))
        helper_append_file(cache_mgr.cache_root, revision, "test1.txt", "asdfasdf")
        helper_append_file(cache_mgr.cache_root, revision, "test2.txt", "asdfasdf")
        helper_append_file(cache_mgr.cache_root, revision, "test3.txt", "asdfasdf")
        helper_append_file(cache_mgr.cache_root, revision, "other_dir/test4.txt", "dfasdfhfgjhg")
        helper_append_file(cache_mgr.cache_root, revision, "other_dir/test5.txt", "fdghdfgsa")

        assert len(ds.git.log()) == 4

        status = m.status()
        assert len(status.created) == 5
        assert len(status.modified) == 0
        assert len(status.deleted) == 0
        m.sweep_all_changes()
        status = m.status()
        assert len(status.created) == 0
        assert len(status.modified) == 0
        assert len(status.deleted) == 0

        helper_append_file(cache_mgr.cache_root, revision, "test1.txt", "asdfasdf")
        status = m.status()
        assert len(status.created) == 0
        assert len(status.modified) == 1
        assert len(status.deleted) == 0
        m.sweep_all_changes()
        status = m.status()
        assert len(status.created) == 0
        assert len(status.modified) == 0
        assert len(status.deleted) == 0
