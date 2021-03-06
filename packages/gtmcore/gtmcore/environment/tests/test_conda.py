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
import pytest

from gtmcore.fixtures.container import mock_config_with_repo, build_lb_image_for_env_conda
from gtmcore.environment.conda import Conda3PackageManager, Conda2PackageManager


skip_clause = os.environ.get('CIRCLE_BRANCH') is not None \
              and os.environ.get('SKIP_CONDA_TESTS') is not None
skip_msg = "Skip long Conda tests on circleCI when not in `test-long-running-env` job"


@pytest.mark.skipif(skip_clause, reason=skip_msg)
class TestConda3PackageManager(object):

    def test_search(self, build_lb_image_for_env_conda):
        """Test search command"""
        mrg = Conda3PackageManager()
        lb = build_lb_image_for_env_conda[0]
        username = build_lb_image_for_env_conda[1]
        result = mrg.search("reque*", lb, username)
        assert type(result) == list
        assert type(result[0]) == str
        assert len(result) > 6
        assert "requests" in result
        result = mrg.search("nump*", lb, username)
        assert type(result) == list
        assert type(result[0]) == str
        assert len(result) > 2
        assert "numpy" in result

    def test_search_no_wildcard(self, build_lb_image_for_env_conda):
        """Test search command"""
        mrg = Conda3PackageManager()
        lb = build_lb_image_for_env_conda[0]
        username = build_lb_image_for_env_conda[1]
        result = mrg.search("reque", lb, username)
        assert type(result) == list
        assert type(result[0]) == str
        assert len(result) > 6
        assert "requests" in result

    def test_search_empty(self, build_lb_image_for_env_conda):
        """Test search command with no result"""
        mrg = Conda3PackageManager()
        lb = build_lb_image_for_env_conda[0]
        username = build_lb_image_for_env_conda[1]
        result = mrg.search("asdffdghdfghdraertasdfsadfa", lb, username)
        assert type(result) == list
        assert len(result) == 0

    def test_list_versions(self, build_lb_image_for_env_conda):
        """Test list_versions command"""
        mrg = Conda3PackageManager()
        lb = build_lb_image_for_env_conda[0]
        username = build_lb_image_for_env_conda[1]
        result = mrg.list_versions("python-coveralls", lb, username)
        assert len(result) == 4
        assert result[2] == "2.7.0"
        assert result[0] == "2.9.1"

    def test_latest_version(self, build_lb_image_for_env_conda):
        """Test latest_version command"""
        mrg = Conda3PackageManager()
        lb = build_lb_image_for_env_conda[0]
        username = build_lb_image_for_env_conda[1]

        # Note, "python-coveralls" is an installed package at 2.7.0 with latest being 2.9.1
        result = mrg.latest_version("python-coveralls", lb, username)
        assert result == '2.9.1'

        # python-coveralls is a non-installed package
        result = mrg.latest_version("cdutil", lb, username)
        assert result == '8.1'

    def test_latest_versions(self, build_lb_image_for_env_conda):
        """Test latest_version command"""
        mrg = Conda3PackageManager()
        lb = build_lb_image_for_env_conda[0]
        username = build_lb_image_for_env_conda[1]
        pkgs = ["cdutil", "python-coveralls", "nltk"]
        result = mrg.latest_versions(pkgs, lb, username)

        assert result[0] == '8.1'  # cdutil
        assert result[1] == '2.9.1'  # python-coveralls
        assert result[2] == '3.2.5'  # nltk

    def test_latest_versions_bad_pkg(self, build_lb_image_for_env_conda):
        """Test latest_version command"""
        mrg = Conda3PackageManager()
        lb = build_lb_image_for_env_conda[0]
        username = build_lb_image_for_env_conda[1]
        with pytest.raises(ValueError):
            mrg.latest_versions(["asdasdfdasdff", "cdutil"], lb, username)

    def test_list_installed_packages(self, build_lb_image_for_env_conda):
        """Test list_installed_packages command

        Note, if the contents of the container change, this test will break and need to be updated. Because of this,
        only limited asserts are made to make sure things are coming back in a reasonable format
        """
        mrg = Conda3PackageManager()
        lb = build_lb_image_for_env_conda[0]
        username = build_lb_image_for_env_conda[1]
        result = mrg.list_installed_packages(lb, username)

        assert type(result) == list
        assert len(result) >= 14
        assert type(result[0]) == dict
        assert type(result[0]['name']) == str
        assert type(result[0]['version']) == str

    def test_list_available_updates(self, build_lb_image_for_env_conda):
        """Test list_available_updates command

        Note, if the contents of the container change, this test will break and need to be updated. Because of this,
        only limited asserts are made to make sure things are coming back in a reasonable format
        """
        mrg = Conda3PackageManager()
        lb = build_lb_image_for_env_conda[0]
        username = build_lb_image_for_env_conda[1]
        result = mrg.list_available_updates(lb, username)

        # TODO: Right now list_available_updates() is a noop and can possibly be removed
        assert result == []

    def test_generate_docker_install_snippet_single(self):
        """Test generate_docker_install_snippet command
        """
        mrg = Conda3PackageManager()
        packages = [{'name': 'mypackage', 'version': '3.1.4'}]

        result = mrg.generate_docker_install_snippet(packages)
        assert result == ['RUN conda install -yq mypackage=3.1.4']

        result = mrg.generate_docker_install_snippet(packages, single_line=True)
        assert result == ['RUN conda install -yq mypackage=3.1.4']

    def test_generate_docker_install_snippet_multiple(self):
        """Test generate_docker_install_snippet command
        """
        mrg = Conda3PackageManager()
        packages = [{'name': 'mypackage', 'version': '3.1.4'},
                    {'name': 'yourpackage', 'version': '2017-54.0'}]

        result = mrg.generate_docker_install_snippet(packages)
        assert result == ['RUN conda install -yq mypackage=3.1.4 yourpackage=2017-54.0']

        result = mrg.generate_docker_install_snippet(packages, single_line=True)
        assert result == ['RUN conda install -yq mypackage=3.1.4 yourpackage=2017-54.0']

    def test_list_versions_badpackage(self, build_lb_image_for_env_conda):
        """Test list_versions command"""
        mrg = Conda3PackageManager()
        lb = build_lb_image_for_env_conda[0]
        username = build_lb_image_for_env_conda[1]
        with pytest.raises(ValueError):
            mrg.list_versions("gigantumasdfasdfasdf", lb, username)

    def test_is_valid_errors(self, build_lb_image_for_env_conda):
        """Test list_versions command"""
        pkgs = [{"manager": "conda3", "package": "numpy", "version": "1.14.2"},
                {"manager": "conda3", "package": "plotly", "version": "100.00"},
                {"manager": "conda3", "package": "cdutil", "version": ""},
                {"manager": "conda3", "package": "asdfasdfasdf", "version": ""}]

        mrg = Conda3PackageManager()
        lb = build_lb_image_for_env_conda[0]
        username = build_lb_image_for_env_conda[1]
        result = mrg.validate_packages(pkgs, lb, username)

        assert result[0].package == "numpy"
        assert result[0].version == "1.14.2"
        assert result[0].error is False

        assert result[1].package == "plotly"
        assert result[1].version == "100.00"
        assert result[1].error is True

        assert result[2].package == "cdutil"
        assert result[2].version == ""
        assert result[2].error is False

        assert result[3].package == "asdfasdfasdf"
        assert result[3].version == ""
        assert result[3].error is True

    def test_is_valid_good(self, build_lb_image_for_env_conda):
        """Test valid packages command"""
        pkgs = [{"manager": "conda3", "package": "nltk", "version": "3.2.2"},
                {"manager": "conda3", "package": "cdutil", "version": ""}]

        mrg = Conda3PackageManager()
        lb = build_lb_image_for_env_conda[0]
        username = build_lb_image_for_env_conda[1]
        result = mrg.validate_packages(pkgs, lb, username)

        assert result[0].package == "nltk"
        assert result[0].version == "3.2.2"
        assert result[0].error is False

        assert result[1].package == "cdutil"
        assert result[1].version == "8.1"
        assert result[1].error is False


@pytest.mark.skipif(skip_clause, reason=skip_msg)
class TestConda2PackageManager(object):
    def test_latest_versions(self, build_lb_image_for_env_conda):
        """Test latest_version command"""
        mrg = Conda2PackageManager()
        lb = build_lb_image_for_env_conda[0]
        username = build_lb_image_for_env_conda[1]
        pkgs = ["python-coveralls", "nltk"]
        result = mrg.latest_versions(pkgs, lb, username)

        assert result[0] == '2.9.1'  # python-coveralls
        assert result[1] == '3.2.5'

    def test_is_valid_errors(self, build_lb_image_for_env_conda):
        """Test list_versions command"""
        pkgs = [{"manager": "conda2", "package": "numpy", "version": "1.14.2"},
                {"manager": "conda2", "package": "plotly", "version": "100.00"},
                {"manager": "conda2", "package": "scipy", "version": ""},
                {"manager": "conda2", "package": "asdfasdfasdf", "version": ""}]

        mrg = Conda2PackageManager()
        lb = build_lb_image_for_env_conda[0]
        username = build_lb_image_for_env_conda[1]
        result = mrg.validate_packages(pkgs, lb, username)

        assert result[0].package == "numpy"
        assert result[0].version == "1.14.2"
        assert result[0].error is False

        assert result[1].package == "plotly"
        assert result[1].version == "100.00"
        assert result[1].error is True

        assert result[2].package == "scipy"
        assert result[2].version == ""
        assert result[2].error is False

        assert result[3].package == "asdfasdfasdf"
        assert result[3].version == ""
        assert result[3].error is True

    def test_is_valid_good(self, build_lb_image_for_env_conda):
        """Test valid packages command"""
        pkgs = [{"manager": "conda2", "package": "nltk", "version": "3.2.2"},
                {"manager": "conda2", "package": "cdutil", "version": ""}]

        mrg = Conda2PackageManager()
        lb = build_lb_image_for_env_conda[0]
        username = build_lb_image_for_env_conda[1]
        result = mrg.validate_packages(pkgs, lb, username)

        assert result[0].package == "nltk"
        assert result[0].version == "3.2.2"
        assert result[0].error is False

        assert result[1].package == "cdutil"
        assert result[1].version == "8.1"
        assert result[1].error is False
