import pytest
import os
import time
from pathlib import Path
from collections import OrderedDict

from gtmcore.exceptions import GigantumException
from gtmcore.dataset import Manifest
from gtmcore.fixtures.datasets import mock_dataset_with_cache_dir, helper_append_file


def mock_storage_detail_gen(ds, filename):
    return "dummystr"


class TestManifest(object):
    def test_init(self, mock_dataset_with_cache_dir):
        ds, cache_dir, revision = mock_dataset_with_cache_dir

        m = Manifest(ds, cache_dir)

        assert isinstance(m.manifest, OrderedDict)
        assert m.dataset_revision == ds.git.repo.head.commit.hexsha

    def test_status_created_files(self, mock_dataset_with_cache_dir):
        ds, cache_dir, revision = mock_dataset_with_cache_dir
        m = Manifest(ds, cache_dir)

        os.makedirs(os.path.join(cache_dir, revision, "test_dir"))
        os.makedirs(os.path.join(cache_dir, revision, "other_dir"))
        os.makedirs(os.path.join(cache_dir, revision, "test_dir", "nested"))
        helper_append_file(cache_dir, revision, "test1.txt", "asdfasdf")
        helper_append_file(cache_dir, revision, "test2.txt", "dfg")
        helper_append_file(cache_dir, revision, "test_dir/test3.txt", "asdffdgfghghfjjgh")
        helper_append_file(cache_dir, revision, "test_dir/nested/test4.txt", "565656565")
        helper_append_file(cache_dir, revision, "other_dir/test5.txt", "dfasdfhfgjhg")

        status = m.status()
        assert len(status.created) == 5
        assert len(status.modified) == 0
        assert len(status.deleted) == 0

        assert "test1.txt" in status.created
        assert "test2.txt" in status.created
        assert "test_dir/test3.txt" in status.created
        assert "test_dir/nested/test4.txt" in status.created
        assert "other_dir/test5.txt" in status.created

    def test_update_simple(self, mock_dataset_with_cache_dir):
        ds, cache_dir, revision = mock_dataset_with_cache_dir
        m = Manifest(ds, cache_dir)

        helper_append_file(cache_dir, revision, "test1.txt", "asdfasdf")

        status = m.status()
        assert len(status.created) == 1
        assert len(status.modified) == 0
        assert len(status.deleted) == 0

        assert "test1.txt" in status.created

        m.update(mock_storage_detail_gen, status=status)

        status = m.status()
        assert len(status.created) == 0
        assert len(status.modified) == 0
        assert len(status.deleted) == 0

        helper_append_file(cache_dir, revision, "test1.txt", "asdfasdf")

        status = m.status()
        assert len(status.created) == 0
        assert len(status.modified) == 1
        assert len(status.deleted) == 0

        m.update(mock_storage_detail_gen)

        status = m.status()
        assert len(status.created) == 0
        assert len(status.modified) == 0
        assert len(status.deleted) == 0

    def test_status_deleted_files(self, mock_dataset_with_cache_dir):
        ds, cache_dir, revision = mock_dataset_with_cache_dir
        m = Manifest(ds, cache_dir)

        helper_append_file(cache_dir, revision, "test1.txt", "asdfasdf")

        status = m.status()
        assert len(status.created) == 1
        assert len(status.modified) == 0
        assert len(status.deleted) == 0

        assert "test1.txt" in status.created

        m.update(mock_storage_detail_gen, status=status)

        status = m.status()
        assert len(status.created) == 0
        assert len(status.modified) == 0
        assert len(status.deleted) == 0

        os.remove(os.path.join(cache_dir, revision, "test1.txt"))

        status = m.status()
        assert len(status.created) == 0
        assert len(status.modified) == 0
        assert len(status.deleted) == 1

        m.update(mock_storage_detail_gen)

        status = m.status()
        assert len(status.created) == 0
        assert len(status.modified) == 0
        assert len(status.deleted) == 0

    def test_update_complex(self, mock_dataset_with_cache_dir):
        ds, cache_dir, revision = mock_dataset_with_cache_dir
        m = Manifest(ds, cache_dir)

        os.makedirs(os.path.join(cache_dir, revision, "test_dir"))
        os.makedirs(os.path.join(cache_dir, revision, "other_dir"))
        os.makedirs(os.path.join(cache_dir, revision, "test_dir", "nested"))
        helper_append_file(cache_dir, revision, "test1.txt", "asdfasdf")
        helper_append_file(cache_dir, revision, "test2.txt", "dfg")
        helper_append_file(cache_dir, revision, "test_dir/test3.txt", "asdffdgfghghfjjgh")
        helper_append_file(cache_dir, revision, "test_dir/nested/test4.txt", "565656565")
        helper_append_file(cache_dir, revision, "other_dir/test5.txt", "dfasdfhfgjhg")

        status = m.status()
        assert len(status.created) == 5
        assert len(status.modified) == 0
        assert len(status.deleted) == 0

        assert "test1.txt" in status.created
        assert "test2.txt" in status.created
        assert "test_dir/test3.txt" in status.created
        assert "test_dir/nested/test4.txt" in status.created
        assert "other_dir/test5.txt" in status.created

        m.update(mock_storage_detail_gen)

        status = m.status()
        assert len(status.created) == 0
        assert len(status.modified) == 0
        assert len(status.deleted) == 0

        helper_append_file(cache_dir, revision, "test99.txt", "ghghgh")
        helper_append_file(cache_dir, revision, "test2.txt", "dfghghgfg")
        os.remove(os.path.join(cache_dir, revision, "test_dir", "nested", "test4.txt"))

        status = m.status()
        assert len(status.created) == 1
        assert len(status.modified) == 1
        assert len(status.deleted) == 1
        assert "test99.txt" in status.created
        assert "test2.txt" in status.modified
        assert "test_dir/nested/test4.txt" in status.deleted

        assert os.path.exists(os.path.join(cache_dir, revision, "test_dir", "nested", "test4.txt")) is False
        assert os.path.exists(os.path.join(cache_dir, revision, "test99.txt")) is True

        m.update(mock_storage_detail_gen)

        status = m.status()
        assert len(status.created) == 0
        assert len(status.modified) == 0
        assert len(status.deleted) == 0
