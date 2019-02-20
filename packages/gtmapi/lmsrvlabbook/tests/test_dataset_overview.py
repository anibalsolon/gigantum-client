import pytest
import os
import shutil

from gtmcore.dataset import Manifest

from lmsrvlabbook.tests.fixtures import fixture_single_dataset
from gtmcore.fixtures.datasets import helper_append_file


class TestDatasetOverviewQueries(object):
    def test_num_files(self, fixture_single_dataset):
        """Test getting the a Dataset's file count"""
        ds = fixture_single_dataset[3]
        query = """
                    {
                      dataset(owner: "default", name: "test-dataset") {
                        overview {
                          numFiles
                        }
                      }
                    }
                    """
        result = fixture_single_dataset[2].execute(query)
        assert 'errors' not in result
        assert result['data']['dataset']['overview']['numFiles'] == 5

        m = Manifest(ds, 'default')
        current_revision_dir = m.cache_mgr.current_revision_dir
        shutil.rmtree(current_revision_dir)
        os.makedirs(current_revision_dir)
        m.update()

        result = fixture_single_dataset[2].execute(query)
        assert 'errors' not in result
        assert result['data']['dataset']['overview']['numFiles'] == 0

    def test_total_bytes(self, fixture_single_dataset):
        """Test getting the a Dataset's total_bytes"""
        ds = fixture_single_dataset[3]
        query = """
                    {
                      dataset(owner: "default", name: "test-dataset") {
                        overview {
                          totalBytes
                        }
                      }
                    }
                    """
        result = fixture_single_dataset[2].execute(query)
        assert 'errors' not in result
        assert result['data']['dataset']['overview']['totalBytes'] == '35'

        m = Manifest(ds, 'default')
        current_revision_dir = m.cache_mgr.current_revision_dir
        shutil.rmtree(current_revision_dir)
        os.makedirs(current_revision_dir)

        result = fixture_single_dataset[2].execute(query)
        assert 'errors' not in result
        assert result['data']['dataset']['overview']['totalBytes'] == '35'

        # Update manifest after all files have been deleted
        m.update()
        result = fixture_single_dataset[2].execute(query)
        assert 'errors' not in result
        assert result['data']['dataset']['overview']['totalBytes'] == '0'

    def test_local_bytes(self, fixture_single_dataset):
        """Test getting the a Dataset's local_bytes"""
        ds = fixture_single_dataset[3]
        query = """
                    {
                      dataset(owner: "default", name: "test-dataset") {
                        overview {
                          localBytes
                        }
                      }
                    }
                    """
        result = fixture_single_dataset[2].execute(query)
        assert 'errors' not in result
        assert result['data']['dataset']['overview']['localBytes'] == '35'

        # Delete all files
        m = Manifest(ds, 'default')
        current_revision_dir = m.cache_mgr.current_revision_dir
        shutil.rmtree(current_revision_dir)
        os.makedirs(current_revision_dir)

        result = fixture_single_dataset[2].execute(query)
        assert 'errors' not in result
        assert result['data']['dataset']['overview']['localBytes'] == '0'

        # Update manifest after all files have been deleted, should still be 0
        m.update()
        result = fixture_single_dataset[2].execute(query)
        assert 'errors' not in result
        assert result['data']['dataset']['overview']['localBytes'] == '0'

    def test_file_distribution(self, fixture_single_dataset):
        """Test getting the a Dataset's local_bytes"""
        ds = fixture_single_dataset[3]
        query = """
                    {
                      dataset(owner: "default", name: "test-dataset") {
                        overview {
                          fileTypeDistribution
                        }
                      }
                    }
                    """
        result = fixture_single_dataset[2].execute(query)
        assert 'errors' not in result
        assert len(result['data']['dataset']['overview']['fileTypeDistribution']) == 1
        assert result['data']['dataset']['overview']['fileTypeDistribution'] == ['1.00|.txt']

        # Delete all files
        m = Manifest(ds, 'default')
        helper_append_file(m.cache_mgr.cache_root, m.dataset_revision, "test55.csv", "22222")
        helper_append_file(m.cache_mgr.cache_root, m.dataset_revision, "df.csv", "33333")
        helper_append_file(m.cache_mgr.cache_root, m.dataset_revision, ".hidden", "33333")
        helper_append_file(m.cache_mgr.cache_root, m.dataset_revision, "noextension", "33333")
        m.update()

        result = fixture_single_dataset[2].execute(query)
        assert 'errors' not in result
        assert len(result['data']['dataset']['overview']['fileTypeDistribution']) == 2
        assert result['data']['dataset']['overview']['fileTypeDistribution'][0] == '0.71|.txt'
        assert result['data']['dataset']['overview']['fileTypeDistribution'][1] == '0.29|.csv'

    def test_file_info_combined(self, fixture_single_dataset):
        """Test getting the a Dataset's file info"""
        ds = fixture_single_dataset[3]
        query = """
                    {
                      dataset(owner: "default", name: "test-dataset") {
                        overview {
                          fileTypeDistribution
                          localBytes
                          totalBytes
                        }
                      }
                    }
                    """
        result = fixture_single_dataset[2].execute(query)
        assert 'errors' not in result
        assert result['data']['dataset']['overview']['fileTypeDistribution'] == ['1.00|.txt']
        assert result['data']['dataset']['overview']['localBytes'] == '35'
        assert result['data']['dataset']['overview']['totalBytes'] == '35'

        # Delete all files
        m = Manifest(ds, 'default')
        current_revision_dir = m.cache_mgr.current_revision_dir
        shutil.rmtree(current_revision_dir)
        os.makedirs(current_revision_dir)

        result = fixture_single_dataset[2].execute(query)
        assert 'errors' not in result
        assert result['data']['dataset']['overview']['fileTypeDistribution'] == ['1.00|.txt']
        assert result['data']['dataset']['overview']['localBytes'] == '0'
        assert result['data']['dataset']['overview']['totalBytes'] == '35'

        m.update()
        result = fixture_single_dataset[2].execute(query)
        assert 'errors' not in result
        assert result['data']['dataset']['overview']['fileTypeDistribution'] == []
        assert result['data']['dataset']['overview']['localBytes'] == '0'
        assert result['data']['dataset']['overview']['totalBytes'] == '0'

    def test_file_distribution_hidden(self, fixture_single_dataset):
        """"""
        ds = fixture_single_dataset[3]
        query = """
                    {
                      dataset(owner: "default", name: "test-dataset") {
                        overview {
                          fileTypeDistribution
                        }
                      }
                    }
                    """
        result = fixture_single_dataset[2].execute(query)
        assert 'errors' not in result
        assert result['data']['dataset']['overview']['fileTypeDistribution'] == ['1.00|.txt']

        # Delete all files
        m = Manifest(ds, 'default')
        os.makedirs(os.path.join(m.cache_mgr.cache_root, m.dataset_revision, ".hiddendir"))
        os.makedirs(os.path.join(m.cache_mgr.cache_root, m.dataset_revision, ".hiddendir", "subdir"))
        helper_append_file(m.cache_mgr.cache_root, m.dataset_revision, "test55.csv", "22222")
        helper_append_file(m.cache_mgr.cache_root, m.dataset_revision, "df.csv", "11")
        helper_append_file(m.cache_mgr.cache_root, m.dataset_revision, ".hidden", "343")
        helper_append_file(m.cache_mgr.cache_root, m.dataset_revision, "noextension", "6t4")
        helper_append_file(m.cache_mgr.cache_root, m.dataset_revision, ".hiddendir/tester.png", "8544")
        helper_append_file(m.cache_mgr.cache_root, m.dataset_revision, ".hiddendir/subdir/blah.jpeg", "8544")
        helper_append_file(m.cache_mgr.cache_root, m.dataset_revision, ".hiddendir/subdir/.hiddenfile", "jhg")
        m.update()

        result = fixture_single_dataset[2].execute(query)
        assert 'errors' not in result
        assert len(result['data']['dataset']['overview']['fileTypeDistribution']) == 4
        assert result['data']['dataset']['overview']['fileTypeDistribution'][0] == '0.56|.txt'
        assert result['data']['dataset']['overview']['fileTypeDistribution'][1] == '0.22|.csv'
        assert result['data']['dataset']['overview']['fileTypeDistribution'][2] == '0.11|.jpeg'
        assert result['data']['dataset']['overview']['fileTypeDistribution'][3] == '0.11|.png'

    def test_readme(self, fixture_single_dataset):
        """Test getting a datasets's readme document"""
        ds = fixture_single_dataset[3]

        query = """
                    {
                      dataset(owner: "default", name: "test-dataset") {
                        overview {
                          readme
                        }
                      }
                    }
                    """
        result = fixture_single_dataset[2].execute(query)
        assert 'errors' not in result
        assert result['data']['dataset']['overview']['readme'] is None

        ds.write_readme("##Summary\nThis is my readme!!")

        result = fixture_single_dataset[2].execute(query)
        assert 'errors' not in result
        assert result['data']['dataset']['overview']['readme'] == "##Summary\nThis is my readme!!"
