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

import os
import pprint
import time
import responses

from lmsrvlabbook.tests.fixtures import (property_mocks_fixture, docker_socket_fixture,
    fixture_working_dir_env_repo_scoped, fixture_working_dir, _create_temp_work_dir)

import pytest
from mock import patch
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request

from gtmcore.fixtures import remote_labbook_repo, mock_config_file
from gtmcore.inventory.branching import BranchManager
from gtmcore.inventory.inventory import InventoryManager
from gtmcore.configuration import Configuration
from gtmcore.dispatcher import Dispatcher, JobKey
from gtmcore.files import FileOperations

@pytest.fixture()
def mock_create_labbooks(fixture_working_dir):
    # Create a labbook in the temporary directory
    lb = InventoryManager(fixture_working_dir[0]).create_labbook("default", "default", "sample-repo-lb",
                                                                 description="Cats labbook 1")

    # Create a file in the dir
    with open(os.path.join(fixture_working_dir[1], 'codefile.c'), 'w') as sf:
        sf.write("1234567")
        sf.seek(0)
    FileOperations.insert_file(lb, 'code', sf.name)

    assert os.path.isfile(os.path.join(lb.root_dir, 'code', 'codefile.c'))
    # name of the config file, temporary working directory, the schema
    yield fixture_working_dir, lb


class TestLabbookSharing(object):

    @responses.activate
    def test_import_remote_labbook(self, remote_labbook_repo, fixture_working_dir, property_mocks_fixture,
                                   docker_socket_fixture, monkeypatch):

        # Mock the request context so a fake authorization header is present
        builder = EnvironBuilder(path='/labbook', method='POST', headers={'Authorization': 'Bearer AJDFHASD'})
        env = builder.get_environ()
        req = Request(environ=env)

        monkeypatch.setattr(Configuration, 'find_default_config', lambda x : fixture_working_dir[0])

        def mock_dispatch(*args, **kwargs):
            return JobKey('rq:job:000-000-000')
        monkeypatch.setattr(Dispatcher, 'dispatch_task', mock_dispatch)

        query = f"""
        mutation importFromRemote {{
          importRemoteLabbook(
            input: {{
              owner: "test",
              labbookName: "sample-repo-lb",
              remoteUrl: "{remote_labbook_repo}"
            }}) {{
                jobKey
            }}
        }}
        """
        r = fixture_working_dir[2].execute(query, context_value=req)
        assert 'errors' not in r
        assert r['data']['importRemoteLabbook']['jobKey'] == 'rq:job:000-000-000'

    def test_can_checkout_branch(self, mock_create_labbooks, remote_labbook_repo, fixture_working_dir):
        """Test whether there are uncommitted changes or anything that would prevent
        having a fresh branch checked out. """

        f_dir, lb = mock_create_labbooks

        query = f"""
        {{
            labbook(name: "sample-repo-lb", owner: "default") {{
                isRepoClean
            }}
        }}
        """
        r = fixture_working_dir[2].execute(query)
        assert r['data']['labbook']['isRepoClean'] is True

        os.remove(os.path.join(lb.root_dir, 'code', 'codefile.c'))

        r = fixture_working_dir[2].execute(query)
        # We back-door deleted a file in the LB. The repo should now be unclean - prove it.
        assert r['data']['labbook']['isRepoClean'] is False
