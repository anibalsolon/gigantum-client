import pytest
import os
import tempfile
import uuid
import shutil

from gtmcore.fixtures.fixtures import _create_temp_work_dir
from gtmcore.inventory.inventory import InventoryManager


@pytest.fixture
def mock_dataset_with_cache_dir():
    """A pytest fixture that creates a dataset in a temp working dir. Deletes directory after test"""
    conf_file, working_dir = _create_temp_work_dir()

    im = InventoryManager(conf_file)
    ds = im.create_dataset('tester', 'tester', 'dataset-1', description="my dataset 1",
                           storage_type="gigantum_object_v1")

    cache_dir = os.path.join(tempfile.gettempdir(), uuid.uuid4().hex)
    revision = ds.git.repo.head.commit.hexsha
    os.makedirs(cache_dir)
    os.makedirs(os.path.join(cache_dir, 'objects'))
    os.makedirs(os.path.join(cache_dir, revision))

    yield ds, cache_dir, revision

    shutil.rmtree(cache_dir)
    shutil.rmtree(working_dir)


def helper_append_file(cache_dir, revision, rel_path, content):
    with open(os.path.join(cache_dir, revision, rel_path), 'at') as fh:
        fh.write(content)
