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
import pytest
import re
import getpass

from gtmcore.environment.apt import AptPackageManager
from gtmcore.fixtures.container import build_lb_image_for_env, mock_config_with_repo


class TestAptPackageManager(object):
    def test_search(self, build_lb_image_for_env):
        """Test search command"""
        lb = build_lb_image_for_env[0]
        username = build_lb_image_for_env[1]
        mrg = AptPackageManager()
        result = mrg.search("libtiff", lb, username)
        assert len(result) == 7
        assert 'libtiff5' in result

    def test_list_versions(self, build_lb_image_for_env):
        """Test list_versions command"""
        mrg = AptPackageManager()
        lb = build_lb_image_for_env[0]
        username = build_lb_image_for_env[1]
        result = mrg.list_versions("libtiff5", lb, username)

        assert len(result) == 1

        # assert result == "4.0.9-5"
        assert re.match('\d.\d.\d-\d', result[0])

    def test_latest_version(self, build_lb_image_for_env):
        """Test latest_version command"""
        mrg = AptPackageManager()
        lb = build_lb_image_for_env[0]
        username = build_lb_image_for_env[1]

        result = mrg.latest_version("libtiff5", lb, username)

        # assert result == "4.0.9-5"
        assert re.match('\d.\d.\d-\d', result)

    def test_list_installed_packages(self, build_lb_image_for_env):
        """Test list_installed_packages command

        Note, if the contents of the container change, this test will break and need to be updated. Because of this,
        only limited asserts are made to make sure things are coming back in a reasonable format
        """
        mrg = AptPackageManager()
        lb = build_lb_image_for_env[0]
        username = build_lb_image_for_env[1]
        result = mrg.list_installed_packages(lb, username)

        assert type(result) == list
        assert len(result) > 50
        assert type(result[0]) == dict
        assert type(result[0]['name']) == str
        assert type(result[0]['version']) == str

    @pytest.mark.skip(reason="Cannot test for updates yet.")
    def test_list_available_updates(self, build_lb_image_for_env):
        """Test list_available_updates command

        Note, if the contents of the container change, this test will break and need to be updated. Because of this,
        only limited asserts are made to make sure things are coming back in a reasonable format
        """
        mrg = AptPackageManager()
        lb = build_lb_image_for_env[0]
        username = build_lb_image_for_env[1]
        result = mrg.list_available_updates(lb, username)

        assert type(result) == list
        assert len(result) < len(mrg.list_installed_packages(lb, username))
        assert type(result[0]) == dict
        assert type(result[0]['name']) == str
        assert type(result[0]['version']) == str
        assert type(result[0]['latest_version']) == str
        assert result[0]['name'] == "zlib1g"
        assert result[0]['version'] == '1:1.2.8.dfsg-2ubuntu4'
        assert result[0]['latest_version'] == '1:1.2.8.dfsg-2ubuntu4.1'

    def test_generate_docker_install_snippet_single(self):
        """Test generate_docker_install_snippet command
        """
        mrg = AptPackageManager()
        packages = [{'name': 'mypackage', 'version': '3.1.4'}]

        result = mrg.generate_docker_install_snippet(packages)
        assert result == ['RUN apt-get -y --no-install-recommends install mypackage']

        result = mrg.generate_docker_install_snippet(packages, single_line=True)
        assert result == ['RUN apt-get -y --no-install-recommends install mypackage']

    def test_generate_docker_install_snippet_multiple(self):
        """Test generate_docker_install_snippet command
        """
        mrg = AptPackageManager()

        packages = [{'name': 'mypackage', 'version': '3.1.4'},
                    {'name': 'yourpackage', 'version': '2017-54.0'}]

        result = mrg.generate_docker_install_snippet(packages)
        assert result == ['RUN apt-get -y --no-install-recommends install mypackage',
                          'RUN apt-get -y --no-install-recommends install yourpackage']

        result = mrg.generate_docker_install_snippet(packages, single_line=True)
        assert result == ['RUN apt-get -y --no-install-recommends install mypackage yourpackage']

    def test_list_versions_badpackage(self, build_lb_image_for_env):
        """Test list_versions command"""
        mrg = AptPackageManager()
        lb = build_lb_image_for_env[0]
        username = build_lb_image_for_env[1]

        with pytest.raises(ValueError):
            mrg.list_versions("asdfasdfasd", lb, username)

    def test_is_valid(self, build_lb_image_for_env):
        """Test list_versions command"""
        pkgs = [{"manager": "pip", "package": "libjpeg-dev", "version": ""},
                {"manager": "pip", "package": "afdgfdgshfdg", "version": ""}]

        mrg = AptPackageManager()
        lb = build_lb_image_for_env[0]
        username = build_lb_image_for_env[1]
        result = mrg.validate_packages(pkgs, lb, username)

        assert result[0].package == "libjpeg-dev"
        assert result[0].version != ""
        assert result[0].error is False

        assert result[1].package == "afdgfdgshfdg"
        assert result[1].version == ""
        assert result[1].error is True

