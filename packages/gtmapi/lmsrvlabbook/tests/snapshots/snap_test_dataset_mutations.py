# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestDatasetMutations.test_create_dataset 1'] = {
    'data': {
        'createDataset': {
            'dataset': {
                'datasetType': {
                    'description': 'Scalable Dataset storage provided by your Gigantum account',
                    'id': 'RGF0YXNldFR5cGU6Z2lnYW50dW1fb2JqZWN0X3Yx',
                    'name': 'Gigantum Cloud'
                },
                'description': 'my test dataset',
                'id': 'RGF0YXNldDpkZWZhdWx0JnRlc3QtZGF0YXNldC0x',
                'name': 'test-dataset-1',
                'schemaVersion': 1
            }
        }
    }
}

snapshots['TestDatasetMutations.test_create_dataset 2'] = {
    'data': {
        'dataset': {
            'datasetType': {
                'description': 'Scalable Dataset storage provided by your Gigantum account',
                'id': 'RGF0YXNldFR5cGU6Z2lnYW50dW1fb2JqZWN0X3Yx',
                'name': 'Gigantum Cloud'
            },
            'description': 'my test dataset',
            'id': 'RGF0YXNldDpkZWZhdWx0JnRlc3QtZGF0YXNldC0x',
            'name': 'test-dataset-1',
            'schemaVersion': 1
        }
    }
}

snapshots['TestDatasetMutations.test_download_dataset_files 1'] = {
    'data': {
        'downloadDatasetFiles': {
            'updatedFileEdges': [
                {
                    'node': {
                        'isLocal': True,
                        'key': 'test1.txt',
                        'name': 'dataset100',
                        'size': '10'
                    }
                }
            ]
        }
    }
}

snapshots['TestDatasetMutations.test_download_dataset_files 2'] = {
    'data': {
        'downloadDatasetFiles': {
            'updatedFileEdges': [
                {
                    'node': {
                        'id': 'RGF0YXNldEZpbGU6ZGVmYXVsdCZkYXRhc2V0MTAwJnRlc3QyLnR4dA==',
                        'isLocal': True,
                        'name': 'dataset100',
                        'size': '7'
                    }
                }
            ]
        }
    }
}
