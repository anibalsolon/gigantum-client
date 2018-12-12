# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestDatasetQueries.test_pagination_noargs 1'] = {
    'data': {
        'datasetList': {
            'localDatasets': {
                'edges': [
                    {
                        'cursor': 'MA==',
                        'node': {
                            'description': 'Cats 1',
                            'name': 'dataset1'
                        }
                    },
                    {
                        'cursor': 'MQ==',
                        'node': {
                            'description': 'Cats 2',
                            'name': 'dataset2'
                        }
                    },
                    {
                        'cursor': 'Mg==',
                        'node': {
                            'description': 'Cats 3',
                            'name': 'dataset3'
                        }
                    },
                    {
                        'cursor': 'Mw==',
                        'node': {
                            'description': 'Cats 4',
                            'name': 'dataset4'
                        }
                    },
                    {
                        'cursor': 'NA==',
                        'node': {
                            'description': 'Cats 5',
                            'name': 'dataset5'
                        }
                    },
                    {
                        'cursor': 'NQ==',
                        'node': {
                            'description': 'Cats 6',
                            'name': 'dataset6'
                        }
                    },
                    {
                        'cursor': 'Ng==',
                        'node': {
                            'description': 'Cats 7',
                            'name': 'dataset7'
                        }
                    },
                    {
                        'cursor': 'Nw==',
                        'node': {
                            'description': 'Cats 8',
                            'name': 'dataset8'
                        }
                    },
                    {
                        'cursor': 'OA==',
                        'node': {
                            'description': 'Cats 9',
                            'name': 'dataset9'
                        }
                    },
                    {
                        'cursor': 'OQ==',
                        'node': {
                            'description': 'Cats other',
                            'name': 'dataset-other'
                        }
                    }
                ],
                'pageInfo': {
                    'hasNextPage': False,
                    'hasPreviousPage': False
                }
            }
        }
    }
}

snapshots['TestDatasetQueries.test_pagination_sort_az_reverse 1'] = {
    'data': {
        'datasetList': {
            'localDatasets': {
                'edges': [
                    {
                        'cursor': 'MA==',
                        'node': {
                            'datasetType': {
                                'description': 'Scalable Dataset storage provided by your Gigantum account',
                                'name': 'Gigantum Cloud',
                                'storageType': 'gigantum_object_v1'
                            },
                            'description': 'Cats other',
                            'id': 'RGF0YXNldDp0ZXN0MyZkYXRhc2V0LW90aGVy',
                            'name': 'dataset-other'
                        }
                    },
                    {
                        'cursor': 'MQ==',
                        'node': {
                            'datasetType': {
                                'description': 'Scalable Dataset storage provided by your Gigantum account',
                                'name': 'Gigantum Cloud',
                                'storageType': 'gigantum_object_v1'
                            },
                            'description': 'Cats 9',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQ5',
                            'name': 'dataset9'
                        }
                    },
                    {
                        'cursor': 'Mg==',
                        'node': {
                            'datasetType': {
                                'description': 'Scalable Dataset storage provided by your Gigantum account',
                                'name': 'Gigantum Cloud',
                                'storageType': 'gigantum_object_v1'
                            },
                            'description': 'Cats 8',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQ4',
                            'name': 'dataset8'
                        }
                    },
                    {
                        'cursor': 'Mw==',
                        'node': {
                            'datasetType': {
                                'description': 'Scalable Dataset storage provided by your Gigantum account',
                                'name': 'Gigantum Cloud',
                                'storageType': 'gigantum_object_v1'
                            },
                            'description': 'Cats 7',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQ3',
                            'name': 'dataset7'
                        }
                    },
                    {
                        'cursor': 'NA==',
                        'node': {
                            'datasetType': {
                                'description': 'Scalable Dataset storage provided by your Gigantum account',
                                'name': 'Gigantum Cloud',
                                'storageType': 'gigantum_object_v1'
                            },
                            'description': 'Cats 6',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQ2',
                            'name': 'dataset6'
                        }
                    },
                    {
                        'cursor': 'NQ==',
                        'node': {
                            'datasetType': {
                                'description': 'Scalable Dataset storage provided by your Gigantum account',
                                'name': 'Gigantum Cloud',
                                'storageType': 'gigantum_object_v1'
                            },
                            'description': 'Cats 5',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQ1',
                            'name': 'dataset5'
                        }
                    },
                    {
                        'cursor': 'Ng==',
                        'node': {
                            'datasetType': {
                                'description': 'Scalable Dataset storage provided by your Gigantum account',
                                'name': 'Gigantum Cloud',
                                'storageType': 'gigantum_object_v1'
                            },
                            'description': 'Cats 4',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQ0',
                            'name': 'dataset4'
                        }
                    },
                    {
                        'cursor': 'Nw==',
                        'node': {
                            'datasetType': {
                                'description': 'Scalable Dataset storage provided by your Gigantum account',
                                'name': 'Gigantum Cloud',
                                'storageType': 'gigantum_object_v1'
                            },
                            'description': 'Cats 3',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQz',
                            'name': 'dataset3'
                        }
                    },
                    {
                        'cursor': 'OA==',
                        'node': {
                            'datasetType': {
                                'description': 'Scalable Dataset storage provided by your Gigantum account',
                                'name': 'Gigantum Cloud',
                                'storageType': 'gigantum_object_v1'
                            },
                            'description': 'Cats 2',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQy',
                            'name': 'dataset2'
                        }
                    },
                    {
                        'cursor': 'OQ==',
                        'node': {
                            'datasetType': {
                                'description': 'Scalable Dataset storage provided by your Gigantum account',
                                'name': 'Gigantum Cloud',
                                'storageType': 'gigantum_object_v1'
                            },
                            'description': 'Cats 1',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQx',
                            'name': 'dataset1'
                        }
                    }
                ],
                'pageInfo': {
                    'hasNextPage': False,
                    'hasPreviousPage': False
                }
            }
        }
    }
}

snapshots['TestDatasetQueries.test_pagination_sort_create 1'] = {
    'data': {
        'datasetList': {
            'localDatasets': {
                'edges': [
                    {
                        'cursor': 'MA==',
                        'node': {
                            'description': 'Cats 2',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQy',
                            'name': 'dataset2'
                        }
                    },
                    {
                        'cursor': 'MQ==',
                        'node': {
                            'description': 'Cats 3',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQz',
                            'name': 'dataset3'
                        }
                    },
                    {
                        'cursor': 'Mg==',
                        'node': {
                            'description': 'Cats 4',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQ0',
                            'name': 'dataset4'
                        }
                    },
                    {
                        'cursor': 'Mw==',
                        'node': {
                            'description': 'Cats 5',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQ1',
                            'name': 'dataset5'
                        }
                    },
                    {
                        'cursor': 'NA==',
                        'node': {
                            'description': 'Cats 6',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQ2',
                            'name': 'dataset6'
                        }
                    },
                    {
                        'cursor': 'NQ==',
                        'node': {
                            'description': 'Cats 7',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQ3',
                            'name': 'dataset7'
                        }
                    },
                    {
                        'cursor': 'Ng==',
                        'node': {
                            'description': 'Cats 8',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQ4',
                            'name': 'dataset8'
                        }
                    },
                    {
                        'cursor': 'Nw==',
                        'node': {
                            'description': 'Cats 9',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQ5',
                            'name': 'dataset9'
                        }
                    },
                    {
                        'cursor': 'OA==',
                        'node': {
                            'description': 'Cats other',
                            'id': 'RGF0YXNldDp0ZXN0MyZkYXRhc2V0LW90aGVy',
                            'name': 'dataset-other'
                        }
                    },
                    {
                        'cursor': 'OQ==',
                        'node': {
                            'description': 'Cats 1',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQx',
                            'name': 'dataset1'
                        }
                    }
                ],
                'pageInfo': {
                    'hasNextPage': False,
                    'hasPreviousPage': False
                }
            }
        }
    }
}

snapshots['TestDatasetQueries.test_pagination_sort_create_desc 1'] = {
    'data': {
        'datasetList': {
            'localDatasets': {
                'edges': [
                    {
                        'cursor': 'MA==',
                        'node': {
                            'description': 'Cats 1',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQx',
                            'name': 'dataset1'
                        }
                    },
                    {
                        'cursor': 'MQ==',
                        'node': {
                            'description': 'Cats other',
                            'id': 'RGF0YXNldDp0ZXN0MyZkYXRhc2V0LW90aGVy',
                            'name': 'dataset-other'
                        }
                    },
                    {
                        'cursor': 'Mg==',
                        'node': {
                            'description': 'Cats 9',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQ5',
                            'name': 'dataset9'
                        }
                    },
                    {
                        'cursor': 'Mw==',
                        'node': {
                            'description': 'Cats 8',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQ4',
                            'name': 'dataset8'
                        }
                    },
                    {
                        'cursor': 'NA==',
                        'node': {
                            'description': 'Cats 7',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQ3',
                            'name': 'dataset7'
                        }
                    },
                    {
                        'cursor': 'NQ==',
                        'node': {
                            'description': 'Cats 6',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQ2',
                            'name': 'dataset6'
                        }
                    },
                    {
                        'cursor': 'Ng==',
                        'node': {
                            'description': 'Cats 5',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQ1',
                            'name': 'dataset5'
                        }
                    },
                    {
                        'cursor': 'Nw==',
                        'node': {
                            'description': 'Cats 4',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQ0',
                            'name': 'dataset4'
                        }
                    },
                    {
                        'cursor': 'OA==',
                        'node': {
                            'description': 'Cats 3',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQz',
                            'name': 'dataset3'
                        }
                    },
                    {
                        'cursor': 'OQ==',
                        'node': {
                            'description': 'Cats 2',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQy',
                            'name': 'dataset2'
                        }
                    }
                ],
                'pageInfo': {
                    'hasNextPage': False,
                    'hasPreviousPage': False
                }
            }
        }
    }
}

snapshots['TestDatasetQueries.test_pagination_sort_modified 1'] = {
    'data': {
        'datasetList': {
            'localDatasets': {
                'edges': [
                    {
                        'cursor': 'MA==',
                        'node': {
                            'description': 'Cats 1',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQx',
                            'name': 'dataset1'
                        }
                    },
                    {
                        'cursor': 'MQ==',
                        'node': {
                            'description': 'Cats other',
                            'id': 'RGF0YXNldDp0ZXN0MyZkYXRhc2V0LW90aGVy',
                            'name': 'dataset-other'
                        }
                    },
                    {
                        'cursor': 'Mg==',
                        'node': {
                            'description': 'Cats 9',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQ5',
                            'name': 'dataset9'
                        }
                    },
                    {
                        'cursor': 'Mw==',
                        'node': {
                            'description': 'Cats 8',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQ4',
                            'name': 'dataset8'
                        }
                    },
                    {
                        'cursor': 'NA==',
                        'node': {
                            'description': 'Cats 7',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQ3',
                            'name': 'dataset7'
                        }
                    },
                    {
                        'cursor': 'NQ==',
                        'node': {
                            'description': 'Cats 6',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQ2',
                            'name': 'dataset6'
                        }
                    },
                    {
                        'cursor': 'Ng==',
                        'node': {
                            'description': 'Cats 5',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQ1',
                            'name': 'dataset5'
                        }
                    },
                    {
                        'cursor': 'Nw==',
                        'node': {
                            'description': 'Cats 4',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQ0',
                            'name': 'dataset4'
                        }
                    },
                    {
                        'cursor': 'OA==',
                        'node': {
                            'description': 'Cats 3',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQz',
                            'name': 'dataset3'
                        }
                    },
                    {
                        'cursor': 'OQ==',
                        'node': {
                            'description': 'Cats 2',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQy',
                            'name': 'dataset2'
                        }
                    }
                ],
                'pageInfo': {
                    'hasNextPage': False,
                    'hasPreviousPage': False
                }
            }
        }
    }
}

snapshots['TestDatasetQueries.test_pagination_sort_modified 2'] = {
    'data': {
        'datasetList': {
            'localDatasets': {
                'edges': [
                    {
                        'cursor': 'MA==',
                        'node': {
                            'description': 'Cats 4',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQ0',
                            'name': 'dataset4'
                        }
                    },
                    {
                        'cursor': 'MQ==',
                        'node': {
                            'description': 'Cats 1',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQx',
                            'name': 'dataset1'
                        }
                    },
                    {
                        'cursor': 'Mg==',
                        'node': {
                            'description': 'Cats other',
                            'id': 'RGF0YXNldDp0ZXN0MyZkYXRhc2V0LW90aGVy',
                            'name': 'dataset-other'
                        }
                    },
                    {
                        'cursor': 'Mw==',
                        'node': {
                            'description': 'Cats 9',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQ5',
                            'name': 'dataset9'
                        }
                    },
                    {
                        'cursor': 'NA==',
                        'node': {
                            'description': 'Cats 8',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQ4',
                            'name': 'dataset8'
                        }
                    },
                    {
                        'cursor': 'NQ==',
                        'node': {
                            'description': 'Cats 7',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQ3',
                            'name': 'dataset7'
                        }
                    },
                    {
                        'cursor': 'Ng==',
                        'node': {
                            'description': 'Cats 6',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQ2',
                            'name': 'dataset6'
                        }
                    },
                    {
                        'cursor': 'Nw==',
                        'node': {
                            'description': 'Cats 5',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQ1',
                            'name': 'dataset5'
                        }
                    },
                    {
                        'cursor': 'OA==',
                        'node': {
                            'description': 'Cats 3',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQz',
                            'name': 'dataset3'
                        }
                    },
                    {
                        'cursor': 'OQ==',
                        'node': {
                            'description': 'Cats 2',
                            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQy',
                            'name': 'dataset2'
                        }
                    }
                ],
                'pageInfo': {
                    'hasNextPage': False,
                    'hasPreviousPage': False
                }
            }
        }
    }
}

snapshots['TestDatasetQueries.test_pagination 1'] = {
    'data': {
        'datasetList': {
            'localDatasets': {
                'edges': [
                    {
                        'cursor': 'MA==',
                        'node': {
                            'description': 'Cats 1',
                            'name': 'dataset1'
                        }
                    },
                    {
                        'cursor': 'MQ==',
                        'node': {
                            'description': 'Cats 2',
                            'name': 'dataset2'
                        }
                    }
                ],
                'pageInfo': {
                    'hasNextPage': True,
                    'hasPreviousPage': False
                }
            }
        }
    }
}

snapshots['TestDatasetQueries.test_pagination 2'] = {
    'data': {
        'datasetList': {
            'localDatasets': {
                'edges': [
                    {
                        'cursor': 'Mg==',
                        'node': {
                            'description': 'Cats 3',
                            'name': 'dataset3'
                        }
                    },
                    {
                        'cursor': 'Mw==',
                        'node': {
                            'description': 'Cats 4',
                            'name': 'dataset4'
                        }
                    },
                    {
                        'cursor': 'NA==',
                        'node': {
                            'description': 'Cats 5',
                            'name': 'dataset5'
                        }
                    },
                    {
                        'cursor': 'NQ==',
                        'node': {
                            'description': 'Cats 6',
                            'name': 'dataset6'
                        }
                    },
                    {
                        'cursor': 'Ng==',
                        'node': {
                            'description': 'Cats 7',
                            'name': 'dataset7'
                        }
                    }
                ],
                'pageInfo': {
                    'hasNextPage': True,
                    'hasPreviousPage': False
                }
            }
        }
    }
}

snapshots['TestDatasetQueries.test_pagination 3'] = {
    'data': {
        'datasetList': {
            'localDatasets': {
                'edges': [
                    {
                        'cursor': 'Nw==',
                        'node': {
                            'description': 'Cats 8',
                            'name': 'dataset8'
                        }
                    },
                    {
                        'cursor': 'OA==',
                        'node': {
                            'description': 'Cats 9',
                            'name': 'dataset9'
                        }
                    },
                    {
                        'cursor': 'OQ==',
                        'node': {
                            'description': 'Cats other',
                            'name': 'dataset-other'
                        }
                    }
                ],
                'pageInfo': {
                    'hasNextPage': False,
                    'hasPreviousPage': False
                }
            }
        }
    }
}

snapshots['TestDatasetQueries.test_pagination 4'] = {
    'data': {
        'datasetList': {
            'localDatasets': {
                'edges': [
                ],
                'pageInfo': {
                    'hasNextPage': False,
                    'hasPreviousPage': False
                }
            }
        }
    }
}

snapshots['TestDatasetQueries.test_get_dataset_all_fields 1'] = {
    'data': {
        'dataset': {
            'activityRecords': {
                'edges': [
                    {
                        'node': {
                            'importance': 255,
                            'message': 'Created new Dataset: default/dataset8',
                            'show': True,
                            'tags': [
                            ],
                            'type': 'DATASET'
                        }
                    }
                ],
                'pageInfo': {
                    'hasNextPage': False,
                    'hasPreviousPage': False,
                }
            },
            'datasetType': {
                'description': 'Scalable Dataset storage provided by your Gigantum account',
                'icon': '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',
                'id': 'RGF0YXNldFR5cGU6Z2lnYW50dW1fb2JqZWN0X3Yx',
                'name': 'Gigantum Cloud',
                'readme': '''Gigantum Cloud Datasets are backed by a scalable object storage service that is linked to
your Gigantum account and credentials. It provides efficient storage at the file level and works seamlessly with the 
Client.

This dataset type is fully managed. That means as you modify data, each version will be tracked independently. Syncing
to Gigantum Cloud will count towards your storage quota and include all versions of files.
''',
                'storageType': 'gigantum_object_v1',
                'tags': [
                    'gigantum'
                ]
            },
            'description': 'Cats 8',
            'id': 'RGF0YXNldDpkZWZhdWx0JmRhdGFzZXQ4',
            'name': 'dataset8',
            'schemaVersion': 1
        }
    }
}
