import pytest
import os
import tempfile
import io
import math
import responses
import uuid
import flask

from snapshottest import snapshot
from lmsrvlabbook.tests.fixtures import fixture_working_dir_env_repo_scoped, fixture_working_dir

from graphene.test import Client
from werkzeug.datastructures import FileStorage

from gtmcore.dispatcher.jobs import export_dataset_as_zip
from gtmcore.files import FileOperations

from gtmcore.inventory.inventory import InventoryManager
from gtmcore.dataset.io.manager import IOManager
from gtmcore.dataset.manifest import Manifest

from lmsrvcore.middleware import error_middleware, DataloaderMiddleware

from gtmcore.fixtures.datasets import mock_dataset_with_cache_dir, mock_dataset_with_cache_mgr, \
    mock_dataset_with_cache_mgr_manifest, helper_append_file

# @pytest.fixture()
# def mock_create_datasets(fixture_working_dir):
#     # Create a dataset in the temporary directory
#     # Create a temporary dataset
#     ds = InventoryManager(fixture_working_dir[0]).create_dataset("default", "default", "dataset1",
#                                                                  "gigantum_object_v1",
#                                                                  description="Cats dataset 1")
#
#     # Create a file in the dir
#     with open(os.path.join(fixture_working_dir[1], 'sillyfile'), 'w') as sf:
#         sf.write("1234567")
#         sf.seek(0)
#     FileOperations.insert_file(ds, 'code', sf.name)
#
#     assert os.path.isfile(os.path.join(ds.root_dir, 'code', 'sillyfile'))
#     # name of the config file, temporary working directory, the schema
#     yield fixture_working_dir


class TestDatasetMutations(object):
    def test_create_dataset(self, fixture_working_dir, snapshot):
        query = """
        mutation myCreateDataset($name: String!, $desc: String!, $storage_type: String!) {
          createDataset(input: {name: $name, description: $desc, 
                                storageType: $storage_type}) {
            dataset {
              id
              name
              description
              schemaVersion
              datasetType{
                name
                id
                description
              }
            }
          }
        }
        """
        variables = {"name": "test-dataset-1", "desc": "my test dataset",
                     "storage_type": "gigantum_object_v1"}

        snapshot.assert_match(fixture_working_dir[2].execute(query, variable_values=variables))

        # Get Dataset you just created
        query = """{
            dataset(name: "test-dataset-1", owner: "default")  {
                  id
                  name
                  description
                  schemaVersion
                  datasetType{
                    name
                    id
                    description
                  }
                }
                }
        """
        snapshot.assert_match(fixture_working_dir[2].execute(query))

    def test_import_dataset(self, fixture_working_dir):
        """Test batch uploading, but not full import"""
        class DummyContext(object):
            def __init__(self, file_handle):
                self.dataset_loader = None
                self.files = {'uploadChunk': file_handle}

        client = Client(fixture_working_dir[3], middleware=[DataloaderMiddleware()])

        # Create a temporary dataset
        ds = InventoryManager(fixture_working_dir[0]).create_dataset("default", "default", "test-export",
                                                                     "gigantum_object_v1",
                                                                     description="Tester")

        # Create a largeish file in the dir
        with open(os.path.join(fixture_working_dir[1], 'testfile.bin'), 'wb') as testfile:
            testfile.write(os.urandom(9000000))
        FileOperations.insert_file(ds, 'input', testfile.name)

        # Export dataset
        zip_file = export_dataset_as_zip(ds.root_dir, tempfile.gettempdir())
        ds_dir = ds.root_dir

        # Get upload params
        chunk_size = 4194304
        file_info = os.stat(zip_file)
        file_size = int(file_info.st_size / 1000)
        total_chunks = int(math.ceil(file_info.st_size/chunk_size))

        with open(zip_file, 'rb') as tf:
            for chunk_index in range(total_chunks):
                chunk = io.BytesIO()
                chunk.write(tf.read(chunk_size))
                chunk.seek(0)
                file = FileStorage(chunk)

                query = f"""
                            mutation myMutation{{
                              importDataset(input:{{
                                chunkUploadParams:{{
                                  uploadId: "jfdjfdjdisdjwdoijwlkfjd",
                                  chunkSize: {chunk_size},
                                  totalChunks: {total_chunks},
                                  chunkIndex: {chunk_index},
                                  fileSizeKb: {file_size},
                                  filename: "{os.path.basename(zip_file)}"
                                }}
                              }}) {{
                                importJobKey
                              }}
                            }}
                            """
                result = client.execute(query, context_value=DummyContext(file))
                assert "errors" not in result
                if chunk_index == total_chunks - 1:
                    assert type(result['data']['importDataset']['importJobKey']) == str
                    assert "rq:job:" in result['data']['importDataset']['importJobKey']

                chunk.close()

    def test_export_dataset(self, fixture_working_dir):
        """Test export"""
        create_query = """
                mutation myCreateDataset($name: String!, $desc: String!, $storage_type: String!) {
                  createDataset(input: {name: $name, description: $desc,
                                        storageType: $storage_type}) {
                    dataset {
                      id
                      name
                      description
                      schemaVersion
                      datasetType{
                        name
                        id
                        description
                      }
                    }
                  }
                }
                """
        create_variables = {"name": "test-dataset-1", "desc": "my test dataset",
                            "storage_type": "gigantum_object_v1"}

        fixture_working_dir[2].execute(create_query, variable_values=create_variables)

        query = """
                mutation myMutation($owner: String!, $datasetName: String!) {
                  exportDataset(input: {owner: $owner, datasetName: $datasetName}) {
                      jobKey
                  }
                }
                """
        variables = {"datasetName": "test-dataset-1", "owner": "default"}
        result = fixture_working_dir[2].execute(query, variable_values=variables)
        assert "errors" not in result
        assert type(result['data']['exportDataset']['jobKey']) == str
        assert "rq:job:" in result['data']['exportDataset']['jobKey']

    def test_fetch_dataset_edge(self, fixture_working_dir):
        """Test export"""
        create_query = """
                mutation myCreateDataset($name: String!, $desc: String!, $storage_type: String!) {
                  createDataset(input: {name: $name, description: $desc,
                                        storageType: $storage_type}) {
                    dataset {
                      id
                      name                     
                    }
                  }
                }
                """
        create_variables = {"name": "test-dataset-2", "desc": "my test dataset",
                            "storage_type": "gigantum_object_v1"}

        result = fixture_working_dir[2].execute(create_query, variable_values=create_variables)
        assert "errors" not in result

        query = """
                mutation myMutation($owner: String!, $datasetName: String!) {
                  fetchDatasetEdge(input: {owner: $owner, datasetName: $datasetName}) {
                      newDatasetEdge {
                        node {
                          id
                          name
                        }
                      }
                  }
                }
                """
        variables = {"datasetName": "test-dataset-2", "owner": "default"}
        result = fixture_working_dir[2].execute(query, variable_values=variables)
        assert "errors" not in result
        assert "test-dataset-2" == result['data']['fetchDatasetEdge']['newDatasetEdge']['node']['name']

    @responses.activate
    def test_download_dataset_files(self, fixture_working_dir, snapshot):
        # Create a bunch of lab books
        im = InventoryManager(fixture_working_dir[0])
        ds = im.create_dataset('default', 'default', "dataset100", storage_type="gigantum_object_v1", description="100")
        m = Manifest(ds, 'default')
        iom = IOManager(ds, m)

        flask.g.access_token = "asdf"
        flask.g.id_token = "1234"

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
        os.rename(obj1_target, obj1_source)
        os.rename(obj2_target, obj2_source)
        assert os.path.isfile(obj1_target) is False
        assert os.path.isfile(obj2_target) is False
        assert os.path.isfile(obj1_source) is True
        assert os.path.isfile(obj2_source) is True

        responses.add(responses.GET, f'https://api.gigantum.com/object-v1/{ds.namespace}/{ds.name}/{obj_id_1}',
                      json={
                              "presigned_url": f"https://dummyurl.com/{obj_id_1}?params=1",
                              "namespace": ds.namespace,
                              "obj_id": obj_id_1,
                              "dataset": ds.name
                      },
                      status=200)

        with open(obj1_source, 'rb') as data1:
            responses.add(responses.GET, f"https://dummyurl.com/{obj_id_1}?params=1",
                          body=data1.read(), status=200,
                          content_type='application/octet-stream',
                          stream=True)

        responses.add(responses.GET, f'https://api.gigantum.com/object-v1/{ds.namespace}/{ds.name}/{obj_id_2}',
                      json={
                              "presigned_url": f"https://dummyurl.com/{obj_id_2}?params=1",
                              "namespace": ds.namespace,
                              "obj_id": obj_id_2,
                              "dataset": ds.name
                      },
                      status=200)

        with open(obj2_source, 'rb') as data2:
            responses.add(responses.GET, f"https://dummyurl.com/{obj_id_2}?params=1",
                          body=data2.read(), status=200,
                          content_type='application/octet-stream',
                          stream=True)
        iom.dataset.backend.set_default_configuration("default", "abcd", '1234')

        query = """
                   mutation myMutation {
                     downloadDatasetFiles(input: {datasetOwner: "default", datasetName: "dataset100", keys: ["test1.txt"]}) {
                         updatedFileEdges {
                           node {
                             name
                             key
                             isLocal
                             size
                           }
                         }
                     }
                   }
                   """
        snapshot.assert_match(fixture_working_dir[2].execute(query))

        assert os.path.isfile(obj1_target) is True
        assert os.path.isfile(obj2_target) is False
        with open(obj1_source, 'rt') as dd:
            source1 = dd.read()
        with open(obj1_target, 'rt') as dd:
            assert source1 == dd.read()

        query = """
                   mutation myMutation {
                     downloadDatasetFiles(input: {datasetOwner: "default", datasetName: "dataset100", keys: ["test2.txt"]}) {
                         updatedFileEdges {
                           node {
                             id
                             name
                             isLocal
                             size
                           }
                         }
                     }
                   }
                   """
        snapshot.assert_match(fixture_working_dir[2].execute(query))

        assert os.path.isfile(obj1_target) is True
        assert os.path.isfile(obj2_target) is True
        with open(obj1_source, 'rt') as dd:
            source1 = dd.read()
        with open(obj1_target, 'rt') as dd:
            assert source1 == dd.read()
        with open(obj2_source, 'rt') as dd:
            source2 = dd.read()
        with open(obj2_target, 'rt') as dd:
            assert source2 == dd.read()
