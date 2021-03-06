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

from gtmcore.environment.pip import PipPackageManager
from gtmcore.fixtures.container import mock_config_with_repo, build_lb_image_for_env


class TestPipPackageManager(object):
    def test_search(self, mock_config_with_repo, build_lb_image_for_env):
        """Test search command"""
        mrg = PipPackageManager()
        lb = build_lb_image_for_env[0]
        username = build_lb_image_for_env[1]
        result = mrg.search("peppercorn", lb, username)
        assert len(result) == 2

        result = mrg.search("gigantum", lb, username)
        assert len(result) == 4
        assert result[0] == "gigantum"
        assert result[3] == "gtmunit3"

    def test_list_versions(self, build_lb_image_for_env):
        """Test list_versions command"""
        mrg = PipPackageManager()
        lb = build_lb_image_for_env[0]
        username = build_lb_image_for_env[1]
        result = mrg.list_versions("gtmunit1", lb, username)

        assert len(result) == 5
        assert result[0] == '0.12.4'
        assert result[1] == '0.2.4'
        assert result[2] == '0.2.1'
        assert result[3] == '0.2.0'
        assert result[4] == '0.1.0'

    def test_latest_version(self, build_lb_image_for_env):
        """Test latest_version command"""
        mrg = PipPackageManager()
        lb = build_lb_image_for_env[0]
        username = build_lb_image_for_env[1]
        result = mrg.latest_version("gtmunit1", lb, username)

        assert result == "0.12.4"

        result = mrg.latest_version("gtmunit2", lb, username)

        assert result == "12.2"

    def test_latest_versions(self, build_lb_image_for_env):
        """Test latest_version command"""
        mrg = PipPackageManager()
        lb = build_lb_image_for_env[0]
        username = build_lb_image_for_env[1]
        gtm1, gtm2, gtm3 = mrg.latest_versions(["gtmunit1", "gtmunit2", "gtmunit3"], lb, username)

        assert gtm1 == "0.12.4"
        assert gtm2 == "12.2"
        assert gtm3 == "5.0"

    def test_list_installed_packages(self, build_lb_image_for_env):
        """Test list_installed_packages command

        Note, if the contents of the container change, this test will break and need to be updated. Because of this,
        only limited asserts are made to make sure things are coming back in a reasonable format
        """
        mrg = PipPackageManager()
        lb = build_lb_image_for_env[0]
        username = build_lb_image_for_env[1]
        result = mrg.list_installed_packages(lb, username)

        assert type(result) == list
        assert len(result) > 50
        assert type(result[0]) == dict
        assert type(result[0]['name']) == str
        assert type(result[0]['version']) == str

    def test_list_available_updates(self, build_lb_image_for_env):
        """Test list_available_updates command

        Note, if the contents of the container change, this test will break and need to be updated. Because of this,
        only limited asserts are made to make sure things are coming back in a reasonable format
        """
        mrg = PipPackageManager()
        lb = build_lb_image_for_env[0]
        username = build_lb_image_for_env[1]
        result = mrg.list_available_updates(lb, username)

        assert type(result) == list
        assert len(result) < len(mrg.list_installed_packages(lb, username))
        assert type(result[0]) == dict
        assert type(result[0]['name']) == str
        assert type(result[0]['version']) == str
        assert type(result[0]['latest_version']) == str

    def test_generate_docker_install_snippet_single(self):
        """Test generate_docker_install_snippet command
        """
        mrg = PipPackageManager()

        packages = [{'name': 'mypackage', 'version': '3.1.4'}]

        result = mrg.generate_docker_install_snippet(packages)
        assert result == ['RUN pip install mypackage==3.1.4']

        result = mrg.generate_docker_install_snippet(packages, single_line=True)
        assert result == ['RUN pip install mypackage==3.1.4']

    def test_generate_docker_install_snippet_multiple(self):
        """Test generate_docker_install_snippet command
        """
        mrg = PipPackageManager()

        packages = [{'name': 'mypackage', 'version': '3.1.4'},
                    {'name': 'yourpackage', 'version': '2017-54.0'}]

        result = mrg.generate_docker_install_snippet(packages)
        assert result == ['RUN pip install mypackage==3.1.4', 'RUN pip install yourpackage==2017-54.0']

        result = mrg.generate_docker_install_snippet(packages, single_line=True)
        assert result == ['RUN pip install mypackage==3.1.4 yourpackage==2017-54.0']

    def test_list_versions_badpackage(self, build_lb_image_for_env):
        """Test list_versions command"""
        mrg = PipPackageManager()
        lb = build_lb_image_for_env[0]
        username = build_lb_image_for_env[1]
        with pytest.raises(ValueError):
            mrg.list_versions("gigantumasdfasdfasdf", lb, username)

    def test_is_valid_errors(self, build_lb_image_for_env):
        """Test list_versions command"""
        pkgs = [{"manager": "pip", "package": "gtmunit1", "version": '0.2.4'},
                {"manager": "pip", "package": "gtmunit2", "version": "100.00"},
                {"manager": "pip", "package": "gtmunit3", "version": ""},
                {"manager": "pip", "package": "asdfasdfasdf", "version": ""}]

        mrg = PipPackageManager()
        lb = build_lb_image_for_env[0]
        username = build_lb_image_for_env[1]
        result = mrg.validate_packages(pkgs, lb, username)

        assert result[0].package == "gtmunit1"
        assert result[0].version == "0.2.4"
        assert result[0].error is False

        assert result[1].package == "gtmunit2"
        assert result[1].version == "100.00"
        assert result[1].error is True

        assert result[2].package == "gtmunit3"
        assert result[2].version == "5.0"
        assert result[2].error is False

        assert result[3].package == "asdfasdfasdf"
        assert result[3].version == ""
        assert result[3].error is True

    def test_is_valid_good(self, build_lb_image_for_env):
        """Test valid packages command"""
        pkgs = [{"manager": "pip", "package": "gtmunit3", "version": "4.15"},
                {"manager": "pip", "package": "gtmunit2", "version": ""}]

        mrg = PipPackageManager()
        lb = build_lb_image_for_env[0]
        username = build_lb_image_for_env[1]
        result = mrg.validate_packages(pkgs, lb, username)

        assert result[0].package == "gtmunit3"
        assert result[0].version == "4.15"
        assert result[0].error is False

        assert result[1].package == "gtmunit2"
        assert result[1].version == "12.2"
        assert result[1].error is False
