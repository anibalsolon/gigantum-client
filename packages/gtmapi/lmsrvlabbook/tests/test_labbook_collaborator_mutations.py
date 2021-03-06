# Copyright (c) 2017 FlashX, LLC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import responses
import pprint

from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request

from lmsrvlabbook.tests.fixtures import fixture_working_dir, property_mocks_fixture, docker_socket_fixture

import pytest
from gtmcore.inventory.inventory import InventoryManager


@pytest.fixture()
def mock_create_labbooks(fixture_working_dir):
    # Create a labbook in the temporary directory
    im = InventoryManager(fixture_working_dir[0])
    lb = im.create_labbook("default", "default", "labbook1", "Test labbook 1")

    yield fixture_working_dir


class TestLabBookCollaboratorMutations(object):
    @responses.activate
    def test_add_collaborator(self, mock_create_labbooks, property_mocks_fixture):
        """Test adding a collaborator to a LabBook"""
        # Setup REST mocks
        responses.add(responses.GET, 'https://repo.gigantum.io/api/v4/users?username=person100',
                      json=[
                                {
                                    "id": 100,
                                    "name": "New Person",
                                    "username": "default",
                                    "state": "active",
                                    "access_level": 30
                                }
                            ],
                      status=200)
        responses.add(responses.POST, 'https://repo.gigantum.io/api/v4/projects/default%2Flabbook1/members',
                      json={
                                "id": 100,
                                "name": "New Person",
                                "username": "default",
                                "state": "active",
                            },
                      status=201)
        responses.add(responses.GET, 'https://repo.gigantum.io/api/v4/projects/default%2Flabbook1',
                      json=[{
                              "id": 27,
                              "description": "",
                            }],
                      status=200)
        responses.add(responses.GET, 'https://repo.gigantum.io/api/v4/projects/default%2Flabbook1/members',
                      json=[
                                {
                                    "id": 29,
                                    "name": "Jane Doe",
                                    "username": "janed",
                                    "access_level": 40,
                                    "expires_at": None
                                },
                                {
                                    "id": 100,
                                    "name": "New Person",
                                    "username": "person100",
                                    "access_level": 30,
                                    "expires_at": None
                                }
                            ],
                      status=200)

        # Mock the request context so a fake authorization header is present
        builder = EnvironBuilder(path='/labbook', method='POST', headers={'Authorization': 'Bearer AJDFHASD'})
        env = builder.get_environ()
        req = Request(environ=env)

        query = """
        mutation AddCollaborator {
          addCollaborator(
            input: {
              owner: "default",
              labbookName: "labbook1",
              username: "default"
              permissions: "readwrite"
            }) {
              updatedLabbook {
                collaborators {
                    collaboratorUsername
                }
                canManageCollaborators
              }
            }
        }
        """
        r = mock_create_labbooks[2].execute(query, context_value=req)
        assert 'errors' not in r
        assert r['data']['addCollaborator']['updatedLabbook']['collaborators'][0]['collaboratorUsername'] == 'janed'
        assert r['data']['addCollaborator']['updatedLabbook']['collaborators'][1]['collaboratorUsername'] == 'person100'
        assert r['data']['addCollaborator']['updatedLabbook']['canManageCollaborators'] is False

    @responses.activate
    def test_add_collaborator_as_owner(self, mock_create_labbooks, property_mocks_fixture):
        """Test adding a collaborator to a LabBook"""
        # Setup REST mocks
        responses.add(responses.GET, 'https://repo.gigantum.io/api/v4/users?username=person100',
                      json=[
                                {
                                    "id": 100,
                                    "name": "New Person",
                                    "username": "default",
                                    "state": "active",
                                }
                            ],
                      status=200)
        responses.add(responses.POST, 'https://repo.gigantum.io/api/v4/projects/default%2Flabbook1/members',
                      json={
                                "id": 100,
                                "name": "New Person",
                                "username": "default",
                                "state": "active",
                            },
                      status=201)
        responses.add(responses.DELETE, 'https://repo.gigantum.io/api/v4/projects/default%2Flabbook1/members/100',
                      status=204)
        responses.add(responses.GET, 'https://repo.gigantum.io/api/v4/projects/default%2Flabbook1',
                      json=[{
                              "id": 27,
                              "description": "",
                            }],
                      status=200)
        responses.add(responses.GET, 'https://repo.gigantum.io/api/v4/projects/default%2Flabbook1/members',
                      json=[
                                {
                                    "id": 29,
                                    "name": "Default User",
                                    "username": "default",
                                    "access_level": 40,
                                    "expires_at": None
                                },
                                {
                                    "id": 100,
                                    "name": "New Person",
                                    "username": "person100",
                                    "access_level": 30,
                                    "expires_at": None
                                }
                            ],
                      status=200)

        # Mock the request context so a fake authorization header is present
        builder = EnvironBuilder(path='/labbook', method='POST', headers={'Authorization': 'Bearer AJDFHASD'})
        env = builder.get_environ()
        req = Request(environ=env)

        query = """
        mutation AddCollaborator {
          addCollaborator(
            input: {
              owner: "default",
              labbookName: "labbook1",
              username: "default"
              permissions: "owner"
            }) {
              updatedLabbook {
                collaborators {
                    collaboratorUsername
                }
                canManageCollaborators
              }
            }
        }
        """
        r = mock_create_labbooks[2].execute(query, context_value=req)
        assert 'errors' not in r
        assert r['data']['addCollaborator']['updatedLabbook']['canManageCollaborators'] is True
        assert r['data']['addCollaborator']['updatedLabbook']['collaborators'][0]['collaboratorUsername'] == 'default'
        assert r['data']['addCollaborator']['updatedLabbook']['collaborators'][1]['collaboratorUsername'] == 'person100'

    @responses.activate
    def test_delete_collaborator(self, mock_create_labbooks, property_mocks_fixture, docker_socket_fixture):
        """Test deleting a collaborator from a LabBook"""
        # Setup REST mocks
        responses.add(responses.GET, 'https://repo.gigantum.io/api/v4/users?username=person100',
                      json=[
                                {
                                    "id": 100,
                                    "name": "New Person",
                                    "username": "default",
                                    "state": "active",
                                }
                            ],
                      status=200)
        responses.add(responses.DELETE, 'https://repo.gigantum.io/api/v4/projects/default%2Flabbook1/members/100',
                      status=204)
        responses.add(responses.GET, 'https://repo.gigantum.io/api/v4/projects/default%2Flabbook1',
                      json=[{
                              "id": 27,
                              "description": "",
                            }],
                      status=200)
        responses.add(responses.GET, 'https://repo.gigantum.io/api/v4/projects/default%2Flabbook1/members',
                      json=[
                                {
                                    "id": 29,
                                    "name": "Jane Doe",
                                    "username": "janed",
                                    "access_level": 40,
                                    "expires_at": None
                                }
                            ],
                      status=200)

        # Mock the request context so a fake authorization header is present
        builder = EnvironBuilder(path='/labbook', method='DELETE', headers={'Authorization': 'Bearer AJDFHASD'})
        env = builder.get_environ()
        req = Request(environ=env)

        query = """
        mutation DeleteCollaborator {
          deleteCollaborator(
            input: {
              owner: "default",
              labbookName: "labbook1",
              username: "default"
            }) {
              updatedLabbook {
                collaborators {
                    collaboratorUsername
                }
              }
            }
        }
        """
        r = mock_create_labbooks[2].execute(query, context_value=req)
        assert 'errors' not in r
        assert r['data']['deleteCollaborator']['updatedLabbook']['collaborators'][0]['collaboratorUsername'] == 'janed'
