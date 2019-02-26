import os
import pytest

import uuid
from aioresponses import aioresponses
import snappy
from mock import patch

from gtmcore.configuration import Configuration
from gtmcore.dataset.io.manager import IOManager
from gtmcore.dataset.manifest import Manifest
from gtmcore.dispatcher import jobs
from gtmcore.fixtures import mock_config_file
from gtmcore.fixtures.datasets import helper_append_file, helper_compress_file

from gtmcore.inventory.inventory import InventoryManager


class TestDatasetBackgroundJobs(object):
    def test_download_dataset_files(self, mock_config_file):
        im = InventoryManager(mock_config_file[0])
        ds = im.create_dataset('default', 'default', "dataset100", storage_type="gigantum_object_v1", description="100")
        m = Manifest(ds, 'default')
        iom = IOManager(ds, m)

        os.makedirs(os.path.join(m.cache_mgr.cache_root, m.dataset_revision, "other_dir"))
        helper_append_file(m.cache_mgr.cache_root, m.dataset_revision, "test1.txt", "asdfadfsdf")
        helper_append_file(m.cache_mgr.cache_root, m.dataset_revision, "test2.txt", "fdsfgfd")
        m.sweep_all_changes()

        obj_to_push = iom.objects_to_push()
        assert len(obj_to_push) == 2
        _, obj_id_1 = obj_to_push[0].object_path.rsplit('/', 1)
        _, obj_id_2 = obj_to_push[1].object_path.rsplit('/', 1)
        obj1_target = obj_to_push[0].object_path
        obj2_target = obj_to_push[1].object_path

        obj1_source = os.path.join('/tmp', uuid.uuid4().hex)
        obj2_source = os.path.join('/tmp', uuid.uuid4().hex)

        assert os.path.exists(obj1_target) is True
        assert os.path.exists(obj2_target) is True
        helper_compress_file(obj1_target, obj1_source)
        helper_compress_file(obj2_target, obj2_source)
        assert os.path.isfile(obj1_target) is False
        assert os.path.isfile(obj2_target) is False
        assert os.path.isfile(obj1_source) is True
        assert os.path.isfile(obj2_source) is True

        # Clear out from linked dir
        os.remove(os.path.join(m.cache_mgr.cache_root, m.dataset_revision, 'test1.txt'))
        os.remove(os.path.join(m.cache_mgr.cache_root, m.dataset_revision, 'test2.txt'))

        with patch.object(Configuration, 'find_default_config', lambda self: mock_config_file[0]):

            with aioresponses() as mocked_responses:
                mocked_responses.get(f'https://api.gigantum.com/object-v1/{ds.namespace}/{ds.name}/{obj_id_1}',
                                     payload={
                                             "presigned_url": f"https://dummyurl.com/{obj_id_1}?params=1",
                                             "namespace": ds.namespace,
                                             "obj_id": obj_id_1,
                                             "dataset": ds.name
                                     },
                                     status=200)

                with open(obj1_source, 'rb') as data1:
                    mocked_responses.get(f"https://dummyurl.com/{obj_id_1}?params=1",
                                         body=data1.read(), status=200,
                                         content_type='application/octet-stream')

                mocked_responses.get(f'https://api.gigantum.com/object-v1/{ds.namespace}/{ds.name}/{obj_id_2}',
                                     payload={
                                             "presigned_url": f"https://dummyurl.com/{obj_id_2}?params=1",
                                             "namespace": ds.namespace,
                                             "obj_id": obj_id_2,
                                             "dataset": ds.name
                                     },
                                     status=200)

                with open(obj2_source, 'rb') as data2:
                    mocked_responses.get(f"https://dummyurl.com/{obj_id_2}?params=1",
                                         body=data2.read(), status=200,
                                         content_type='application/octet-stream')

                dl_kwargs = {
                    'logged_in_username': "default",
                    'access_token': "asdf",
                    'id_token': "1234",
                    'dataset_owner': "default",
                    'dataset_name': "dataset100",
                    'labbook_owner': None,
                    'labbook_name': None,
                    'all_keys': False,
                    'keys': ["test1.txt"]
                }

                result = jobs.download_dataset_files(**dl_kwargs)
                assert os.path.isfile(obj1_target) is True
                assert os.path.isfile(obj2_target) is False

                decompressor = snappy.StreamDecompressor()
                with open(obj1_source, 'rb') as dd:
                    source1 = decompressor.decompress(dd.read())
                    source1 += decompressor.flush()
                with open(obj1_target, 'rt') as dd:
                    dest1 = dd.read()
                assert source1.decode("utf-8") == dest1

                # Download other file
                dl_kwargs = {
                    'logged_in_username': "default",
                    'access_token': "asdf",
                    'id_token': "1234",
                    'dataset_owner': "default",
                    'dataset_name': "dataset100",
                    'labbook_owner': None,
                    'labbook_name': None,
                    'all_keys': False,
                    'keys': ["test2.txt"]
                }

                jobs.download_dataset_files(**dl_kwargs)

                assert os.path.isfile(obj1_target) is True
                assert os.path.isfile(obj2_target) is True

                with open(obj1_source, 'rb') as dd:
                    source1 = decompressor.decompress(dd.read())
                    source1 += decompressor.flush()
                with open(obj1_target, 'rt') as dd:
                    dest1 = dd.read()
                assert source1.decode("utf-8") == dest1

                with open(obj2_source, 'rb') as dd:
                    source1 = decompressor.decompress(dd.read())
                    source1 += decompressor.flush()
                with open(obj2_target, 'rt') as dd:
                    dest1 = dd.read()
                assert source1.decode("utf-8") == dest1

    def test_download_dataset_files_all(self, mock_config_file):
        im = InventoryManager(mock_config_file[0])
        ds = im.create_dataset('default', 'default', "dataset100", storage_type="gigantum_object_v1", description="100")
        m = Manifest(ds, 'default')
        iom = IOManager(ds, m)

        os.makedirs(os.path.join(m.cache_mgr.cache_root, m.dataset_revision, "other_dir"))
        helper_append_file(m.cache_mgr.cache_root, m.dataset_revision, "test1.txt", "asdfadfsdf")
        helper_append_file(m.cache_mgr.cache_root, m.dataset_revision, "test2.txt", "fdsfgfd")
        m.sweep_all_changes()

        obj_to_push = iom.objects_to_push()
        assert len(obj_to_push) == 2
        _, obj_id_1 = obj_to_push[0].object_path.rsplit('/', 1)
        _, obj_id_2 = obj_to_push[1].object_path.rsplit('/', 1)
        obj1_target = obj_to_push[0].object_path
        obj2_target = obj_to_push[1].object_path

        obj1_source = os.path.join('/tmp', uuid.uuid4().hex)
        obj2_source = os.path.join('/tmp', uuid.uuid4().hex)

        assert os.path.exists(obj1_target) is True
        assert os.path.exists(obj2_target) is True
        helper_compress_file(obj1_target, obj1_source)
        helper_compress_file(obj2_target, obj2_source)
        assert os.path.isfile(obj1_target) is False
        assert os.path.isfile(obj2_target) is False
        assert os.path.isfile(obj1_source) is True
        assert os.path.isfile(obj2_source) is True

        # Clear out from linked dir
        os.remove(os.path.join(m.cache_mgr.cache_root, m.dataset_revision, 'test1.txt'))
        os.remove(os.path.join(m.cache_mgr.cache_root, m.dataset_revision, 'test2.txt'))

        with patch.object(Configuration, 'find_default_config', lambda self: mock_config_file[0]):
            with aioresponses() as mocked_responses:
                mocked_responses.get(f'https://api.gigantum.com/object-v1/{ds.namespace}/{ds.name}/{obj_id_1}',
                                     payload={
                                             "presigned_url": f"https://dummyurl.com/{obj_id_1}?params=1",
                                             "namespace": ds.namespace,
                                             "obj_id": obj_id_1,
                                             "dataset": ds.name
                                     },
                                     status=200)

                with open(obj1_source, 'rb') as data1:
                    mocked_responses.get(f"https://dummyurl.com/{obj_id_1}?params=1",
                                         body=data1.read(), status=200,
                                         content_type='application/octet-stream')

                mocked_responses.get(f'https://api.gigantum.com/object-v1/{ds.namespace}/{ds.name}/{obj_id_2}',
                                     payload={
                                             "presigned_url": f"https://dummyurl.com/{obj_id_2}?params=1",
                                             "namespace": ds.namespace,
                                             "obj_id": obj_id_2,
                                             "dataset": ds.name
                                     },
                                     status=200)

                with open(obj2_source, 'rb') as data2:
                    mocked_responses.get(f"https://dummyurl.com/{obj_id_2}?params=1",
                                         body=data2.read(), status=200,
                                         content_type='application/octet-stream')

                dl_kwargs = {
                    'logged_in_username': "default",
                    'access_token': "asdf",
                    'id_token': "1234",
                    'dataset_owner': "default",
                    'dataset_name': "dataset100",
                    'labbook_owner': None,
                    'labbook_name': None,
                    'all_keys': True,
                    'keys': None
                }

                result = jobs.download_dataset_files(**dl_kwargs)

                assert os.path.isfile(obj1_target) is True
                assert os.path.isfile(obj2_target) is True
                assert os.path.isfile(os.path.join(m.cache_mgr.cache_root, m.dataset_revision, 'test1.txt')) is True
                assert os.path.isfile(os.path.join(m.cache_mgr.cache_root, m.dataset_revision, 'test2.txt')) is True

                decompressor = snappy.StreamDecompressor()
                with open(obj1_source, 'rb') as dd:
                    source1 = decompressor.decompress(dd.read())
                    source1 += decompressor.flush()
                with open(obj1_target, 'rt') as dd:
                    dest1 = dd.read()
                assert source1.decode("utf-8") == dest1

                with open(obj2_source, 'rb') as dd:
                    source1 = decompressor.decompress(dd.read())
                    source1 += decompressor.flush()
                with open(obj2_target, 'rt') as dd:
                    dest1 = dd.read()
                assert source1.decode("utf-8") == dest1

    def test_download_dataset_files_error(self, mock_config_file):
        im = InventoryManager(mock_config_file[0])
        ds = im.create_dataset('default', 'default', "dataset100", storage_type="gigantum_object_v1", description="100")
        m = Manifest(ds, 'default')
        iom = IOManager(ds, m)

        os.makedirs(os.path.join(m.cache_mgr.cache_root, m.dataset_revision, "other_dir"))
        helper_append_file(m.cache_mgr.cache_root, m.dataset_revision, "test1.txt", "asdfadfsdf")
        helper_append_file(m.cache_mgr.cache_root, m.dataset_revision, "test2.txt", "fdsfgfd")
        m.sweep_all_changes()

        obj_to_push = iom.objects_to_push()
        assert len(obj_to_push) == 2
        _, obj_id_1 = obj_to_push[0].object_path.rsplit('/', 1)
        _, obj_id_2 = obj_to_push[1].object_path.rsplit('/', 1)
        obj1_target = obj_to_push[0].object_path
        obj2_target = obj_to_push[1].object_path

        obj1_source = os.path.join('/tmp', uuid.uuid4().hex)
        obj2_source = os.path.join('/tmp', uuid.uuid4().hex)

        assert os.path.exists(obj1_target) is True
        assert os.path.exists(obj2_target) is True
        helper_compress_file(obj1_target, obj1_source)
        helper_compress_file(obj2_target, obj2_source)
        assert os.path.isfile(obj1_target) is False
        assert os.path.isfile(obj2_target) is False
        assert os.path.isfile(obj1_source) is True
        assert os.path.isfile(obj2_source) is True

        # Clear out from linked dir
        os.remove(os.path.join(m.cache_mgr.cache_root, m.dataset_revision, 'test1.txt'))
        os.remove(os.path.join(m.cache_mgr.cache_root, m.dataset_revision, 'test2.txt'))

        with patch.object(Configuration, 'find_default_config', lambda self: mock_config_file[0]):
            with aioresponses() as mocked_responses:
                mocked_responses.get(f'https://api.gigantum.com/object-v1/{ds.namespace}/{ds.name}/{obj_id_1}',
                                     payload={
                                             "presigned_url": f"https://dummyurl.com/{obj_id_1}?params=1",
                                             "namespace": ds.namespace,
                                             "obj_id": obj_id_1,
                                             "dataset": ds.name
                                     },
                                     status=200)

                with open(obj1_source, 'rb') as data1:
                    mocked_responses.get(f"https://dummyurl.com/{obj_id_1}?params=1",
                                         body=data1.read(), status=200,
                                         content_type='application/octet-stream')

                mocked_responses.get(f'https://api.gigantum.com/object-v1/{ds.namespace}/{ds.name}/{obj_id_2}',
                                     payload={
                                             "presigned_url": f"https://dummyurl.com/{obj_id_2}?params=1",
                                             "namespace": ds.namespace,
                                             "obj_id": obj_id_2,
                                             "dataset": ds.name
                                     },
                                     status=400)

                dl_kwargs = {
                    'logged_in_username': "default",
                    'access_token': "asdf",
                    'id_token': "1234",
                    'dataset_owner': "default",
                    'dataset_name': "dataset100",
                    'labbook_owner': None,
                    'labbook_name': None,
                    'all_keys': True,
                    'keys': None
                }

                with pytest.raises(SystemExit):
                    jobs.download_dataset_files(**dl_kwargs)
                assert os.path.isfile(obj1_target) is True
                assert os.path.isfile(obj2_target) is False
                assert os.path.isfile(os.path.join(m.cache_mgr.cache_root, m.dataset_revision, 'test1.txt')) is True
                assert os.path.isfile(os.path.join(m.cache_mgr.cache_root, m.dataset_revision, 'test2.txt')) is False
