import pytest
import os
from snapshottest import snapshot
from lmsrvlabbook.tests.fixtures import fixture_working_dir

from gtmcore.inventory.inventory import InventoryManager


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
