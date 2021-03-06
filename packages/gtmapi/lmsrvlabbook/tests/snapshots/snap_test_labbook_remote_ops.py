# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestLabBookRemoteOperations.test_list_remote_labbooks_az 1'] = {
    'data': {
        'labbookList': {
            'remoteLabbooks': {
                'edges': [
                    {
                        'cursor': 'eyJwYWdlIjogMSwgIml0ZW0iOiAxfQ==',
                        'node': {
                            'creationDateUtc': '2018-08-30T18:01:33.312Z',
                            'description': 'No Description',
                            'id': 'UmVtb3RlTGFiYm9vazp0ZXN0ZXImdGVzdC1wcm9qLTE=',
                            'isLocal': False,
                            'modifiedDateUtc': '2018-08-30T18:01:33.312Z',
                            'name': 'test-proj-1',
                            'owner': 'tester'
                        }
                    },
                    {
                        'cursor': 'eyJwYWdlIjogMSwgIml0ZW0iOiAzfQ==',
                        'node': {
                            'creationDateUtc': '2018-08-29T18:01:33.312Z',
                            'description': 'No Description',
                            'id': 'UmVtb3RlTGFiYm9vazp0ZXN0ZXImdGVzdC1wcm9qLTI=',
                            'isLocal': False,
                            'modifiedDateUtc': '2018-09-01T18:01:33.312Z',
                            'name': 'test-proj-2',
                            'owner': 'tester'
                        }
                    }
                ],
                'pageInfo': {
                    'hasNextPage': True
                }
            }
        }
    }
}

snapshots['TestLabBookRemoteOperations.test_list_remote_labbooks_az 2'] = {
    'data': {
        'labbookList': {
            'remoteLabbooks': {
                'edges': [
                    {
                        'cursor': 'eyJwYWdlIjogMSwgIml0ZW0iOiAzfQ==',
                        'node': {
                            'creationDateUtc': '2018-08-29T18:01:33.312Z',
                            'description': 'No Description',
                            'id': 'UmVtb3RlTGFiYm9vazp0ZXN0ZXImdGVzdC1wcm9qLTI=',
                            'modifiedDateUtc': '2018-09-01T18:01:33.312Z',
                            'name': 'test-proj-2',
                            'owner': 'tester'
                        }
                    },
                    {
                        'cursor': 'eyJwYWdlIjogMSwgIml0ZW0iOiAxfQ==',
                        'node': {
                            'creationDateUtc': '2018-08-30T18:01:33.312Z',
                            'description': 'No Description',
                            'id': 'UmVtb3RlTGFiYm9vazp0ZXN0ZXImdGVzdC1wcm9qLTE=',
                            'modifiedDateUtc': '2018-08-30T18:01:33.312Z',
                            'name': 'test-proj-1',
                            'owner': 'tester'
                        }
                    }
                ],
                'pageInfo': {
                    'hasNextPage': False
                }
            }
        }
    }
}

snapshots['TestLabBookRemoteOperations.test_list_remote_labbooks_modified 1'] = {
    'data': {
        'labbookList': {
            'remoteLabbooks': {
                'edges': [
                    {
                        'cursor': 'eyJwYWdlIjogMSwgIml0ZW0iOiAzfQ==',
                        'node': {
                            'creationDateUtc': '2018-08-29T18:01:33.312Z',
                            'description': 'No Description',
                            'id': 'UmVtb3RlTGFiYm9vazp0ZXN0ZXImdGVzdC1wcm9qLTI=',
                            'isLocal': False,
                            'modifiedDateUtc': '2018-09-01T18:01:33.312Z',
                            'name': 'test-proj-2',
                            'owner': 'tester'
                        }
                    },
                    {
                        'cursor': 'eyJwYWdlIjogMSwgIml0ZW0iOiAxfQ==',
                        'node': {
                            'creationDateUtc': '2018-08-30T18:01:33.312Z',
                            'description': 'No Description',
                            'id': 'UmVtb3RlTGFiYm9vazp0ZXN0ZXImdGVzdC1wcm9qLTE=',
                            'isLocal': False,
                            'modifiedDateUtc': '2018-08-30T18:01:33.312Z',
                            'name': 'test-proj-1',
                            'owner': 'tester'
                        }
                    }
                ],
                'pageInfo': {
                    'hasNextPage': True
                }
            }
        }
    }
}

snapshots['TestLabBookRemoteOperations.test_list_remote_labbooks_modified 2'] = {
    'data': {
        'labbookList': {
            'remoteLabbooks': {
                'edges': [
                    {
                        'cursor': 'eyJwYWdlIjogMSwgIml0ZW0iOiAxfQ==',
                        'node': {
                            'creationDateUtc': '2018-08-30T18:01:33.312Z',
                            'description': 'No Description',
                            'id': 'UmVtb3RlTGFiYm9vazp0ZXN0ZXImdGVzdC1wcm9qLTE=',
                            'modifiedDateUtc': '2018-08-30T18:01:33.312Z',
                            'name': 'test-proj-1',
                            'owner': 'tester'
                        }
                    },
                    {
                        'cursor': 'eyJwYWdlIjogMSwgIml0ZW0iOiAzfQ==',
                        'node': {
                            'creationDateUtc': '2018-08-29T18:01:33.312Z',
                            'description': 'No Description',
                            'id': 'UmVtb3RlTGFiYm9vazp0ZXN0ZXImdGVzdC1wcm9qLTI=',
                            'modifiedDateUtc': '2018-09-01T18:01:33.312Z',
                            'name': 'test-proj-2',
                            'owner': 'tester'
                        }
                    }
                ],
                'pageInfo': {
                    'hasNextPage': False
                }
            }
        }
    }
}

snapshots['TestLabBookRemoteOperations.test_list_remote_labbooks_created 1'] = {
    'data': {
        'labbookList': {
            'remoteLabbooks': {
                'edges': [
                    {
                        'cursor': 'eyJwYWdlIjogMSwgIml0ZW0iOiAxfQ==',
                        'node': {
                            'creationDateUtc': '2018-08-30T18:01:33.312Z',
                            'description': 'No Description',
                            'id': 'UmVtb3RlTGFiYm9vazp0ZXN0ZXImdGVzdC1wcm9qLTE=',
                            'isLocal': False,
                            'modifiedDateUtc': '2018-08-30T18:01:33.312Z',
                            'name': 'test-proj-1',
                            'owner': 'tester'
                        }
                    },
                    {
                        'cursor': 'eyJwYWdlIjogMSwgIml0ZW0iOiAzfQ==',
                        'node': {
                            'creationDateUtc': '2018-08-29T18:01:33.312Z',
                            'description': 'No Description',
                            'id': 'UmVtb3RlTGFiYm9vazp0ZXN0ZXImdGVzdC1wcm9qLTI=',
                            'isLocal': False,
                            'modifiedDateUtc': '2018-09-01T18:01:33.312Z',
                            'name': 'test-proj-2',
                            'owner': 'tester'
                        }
                    }
                ],
                'pageInfo': {
                    'hasNextPage': True
                }
            }
        }
    }
}

snapshots['TestLabBookRemoteOperations.test_list_remote_labbooks_created 2'] = {
    'data': {
        'labbookList': {
            'remoteLabbooks': {
                'edges': [
                    {
                        'cursor': 'eyJwYWdlIjogMSwgIml0ZW0iOiAzfQ==',
                        'node': {
                            'creationDateUtc': '2018-08-29T18:01:33.312Z',
                            'description': 'No Description',
                            'id': 'UmVtb3RlTGFiYm9vazp0ZXN0ZXImdGVzdC1wcm9qLTI=',
                            'modifiedDateUtc': '2018-09-01T18:01:33.312Z',
                            'name': 'test-proj-2',
                            'owner': 'tester'
                        }
                    },
                    {
                        'cursor': 'eyJwYWdlIjogMSwgIml0ZW0iOiAxfQ==',
                        'node': {
                            'creationDateUtc': '2018-08-30T18:01:33.312Z',
                            'description': 'No Description',
                            'id': 'UmVtb3RlTGFiYm9vazp0ZXN0ZXImdGVzdC1wcm9qLTE=',
                            'modifiedDateUtc': '2018-08-30T18:01:33.312Z',
                            'name': 'test-proj-1',
                            'owner': 'tester'
                        }
                    }
                ],
                'pageInfo': {
                    'hasNextPage': False
                }
            }
        }
    }
}

snapshots['TestLabBookRemoteOperations.test_list_remote_labbooks_page 1'] = {
    'data': {
        'labbookList': {
            'remoteLabbooks': {
                'edges': [
                    {
                        'cursor': 'eyJwYWdlIjogMSwgIml0ZW0iOiAxfQ==',
                        'node': {
                            'creationDateUtc': '2018-08-30T18:01:33.312Z',
                            'description': 'No Description',
                            'id': 'UmVtb3RlTGFiYm9vazp0ZXN0ZXImdGVzdC1wcm9qLTE=',
                            'isLocal': False,
                            'modifiedDateUtc': '2018-08-30T18:01:33.312Z',
                            'name': 'test-proj-1',
                            'owner': 'tester'
                        }
                    }
                ],
                'pageInfo': {
                    'hasNextPage': True
                }
            }
        }
    }
}

snapshots['TestLabBookRemoteOperations.test_list_remote_labbooks_page 2'] = {
    'data': {
        'labbookList': {
            'remoteLabbooks': {
                'edges': [
                    {
                        'cursor': 'eyJwYWdlIjogMSwgIml0ZW0iOiAzfQ==',
                        'node': {
                            'creationDateUtc': '2018-08-29T18:01:33.312Z',
                            'description': 'No Description',
                            'id': 'UmVtb3RlTGFiYm9vazp0ZXN0ZXImdGVzdC1wcm9qLTI=',
                            'modifiedDateUtc': '2018-09-01T18:01:33.312Z',
                            'name': 'test-proj-2',
                            'owner': 'tester'
                        }
                    }
                ],
                'pageInfo': {
                    'hasNextPage': True
                }
            }
        }
    }
}
