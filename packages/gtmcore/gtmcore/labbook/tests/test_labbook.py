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
import getpass
import os
import yaml
import time

from gtmcore.files import FileOperations
from gtmcore.labbook import LabBook, LabbookException, InventoryManager
from gtmcore.gitlib.git import GitAuthor
from gtmcore.fixtures import mock_config_file, mock_labbook, remote_labbook_repo, sample_src_file


class TestLabBook(object):


    def test_create_labbook(self, mock_config_file):
        """Test creating an empty labbook"""
        lb = LabBook(mock_config_file[0])

        labbook_dir = lb.new(username="test", name="labbook1", description="my first labbook",
                             owner={"username": "test"})

        assert labbook_dir == os.path.join(mock_config_file[1], "test", "test", "labbooks", "labbook1")
        assert type(lb) == LabBook

        # Validate directory structure
        assert os.path.isdir(os.path.join(labbook_dir, "code")) is True
        assert os.path.isdir(os.path.join(labbook_dir, "input")) is True
        assert os.path.isdir(os.path.join(labbook_dir, "output")) is True
        assert os.path.isdir(os.path.join(labbook_dir, ".gigantum")) is True
        assert os.path.isdir(os.path.join(labbook_dir, ".gigantum", "env")) is True
        assert os.path.isdir(os.path.join(labbook_dir, ".gigantum", "activity")) is True
        assert os.path.isdir(os.path.join(labbook_dir, ".gigantum", "activity", "log")) is True
        assert os.path.isdir(os.path.join(labbook_dir, ".gigantum", "activity", "index")) is True
        assert os.path.isfile(os.path.join(labbook_dir, ".gigantum", "buildinfo")) is True

        # Validate labbook data file
        with open(os.path.join(labbook_dir, ".gigantum", "labbook.yaml"), "rt") as data_file:
            data = yaml.load(data_file)

        assert data["labbook"]["name"] == "labbook1"
        assert data["labbook"]["description"] == "my first labbook"
        assert "id" in data["labbook"]
        assert data["owner"]["username"] == "test"

        if getpass.getuser() == 'circleci':
            assert lb.build_details is None
        else:
            assert lb.build_details is not None
        assert lb.creation_date is not None

    def test_create_labbook_no_username(self, mock_config_file):
        """Test creating an empty labbook"""
        lb = LabBook(mock_config_file[0])

        labbook_dir = lb.new(name="labbook1", description="my first labbook",
                             owner={"username": "test"})

        assert labbook_dir == os.path.join(mock_config_file[1], "test", "test", "labbooks", "labbook1")
        assert type(lb) == LabBook

        # Validate directory structure
        assert os.path.isdir(os.path.join(labbook_dir, "code")) is True
        assert os.path.isdir(os.path.join(labbook_dir, "input")) is True
        assert os.path.isdir(os.path.join(labbook_dir, "output")) is True
        assert os.path.isdir(os.path.join(labbook_dir, ".gigantum")) is True
        assert os.path.isdir(os.path.join(labbook_dir, ".gigantum", "env")) is True
        assert os.path.isdir(os.path.join(labbook_dir, ".gigantum", "activity")) is True
        assert os.path.isdir(os.path.join(labbook_dir, ".gigantum", "activity", "log")) is True
        assert os.path.isdir(os.path.join(labbook_dir, ".gigantum", "activity", "index")) is True

        # Validate labbook data file
        with open(os.path.join(labbook_dir, ".gigantum", "labbook.yaml"), "rt") as data_file:
            data = yaml.load(data_file)

        assert data["labbook"]["name"] == "labbook1"
        assert data["labbook"]["description"] == "my first labbook"
        assert "id" in data["labbook"]
        assert data["owner"]["username"] == "test"

    def test_create_labbook_that_exists(self, mock_config_file):
        """Test trying to create a labbook with a name that already exists locally"""
        lb = LabBook(mock_config_file[0])
        lb.new(owner={"username": "test"}, name="labbook1", description="my first labbook")
        with pytest.raises(ValueError):
            lb.new(owner={"username": "test"}, name="labbook1", description="my first labbook")

    def test_checkout_id_property(self, mock_config_file):
        """Test trying to create a labbook with a name that already exists locally"""
        lb = LabBook(mock_config_file[0])
        lb.new(owner={"username": "test"}, name="labbook1", description="my first labbook")
        checkout_file = os.path.join(lb.root_dir, '.gigantum', '.checkout')
        assert os.path.exists(checkout_file) is False
        checkout_id = lb.checkout_id
        assert os.path.exists(checkout_file) is True

        parts = checkout_id.split("-")
        assert len(parts) == 6
        assert parts[0] == "test"
        assert parts[1] == "test"
        assert parts[2] == "labbook1"
        assert parts[3] == "gm.workspace"
        assert len(parts[5]) == 10

        # Check repo is clean
        status = lb.git.status()
        for key in status:
            assert len(status[key]) == 0

        # Remove checkout file
        os.remove(checkout_file)

        # Repo should STILL be clean as it is not tracked
        status = lb.git.status()
        for key in status:
            assert len(status[key]) == 0

    def test_checkout_id_property_multiple_access(self, mock_config_file):
        """Test getting a checkout id multiple times"""
        lb = LabBook(mock_config_file[0])
        lb.new(owner={"username": "test"}, name="labbook1", description="my first labbook")

        checkout_file = os.path.join(lb.root_dir, '.gigantum', '.checkout')
        assert os.path.exists(checkout_file) is False
        checkout_id_1 = lb.checkout_id
        assert os.path.exists(checkout_file) is True
        assert checkout_id_1 == lb.checkout_id

        # Remove checkout id
        os.remove(checkout_file)
        lb._checkout_id = None

        # New ID should be created
        assert checkout_id_1 != lb.checkout_id

    def test_change_properties(self, mock_config_file):
        """Test loading a labbook from a directory"""
        lb = LabBook(mock_config_file[0])
        lb.new(owner={"username": "test"}, name="labbook1", description="my first labbook")

        lb.name = "new-labbook-1"
        lb.description = "an updated description"

        # Reload and see changes

        im = InventoryManager(mock_config_file[0])
        lb_loaded = im.load_labbook("test", "test", "new-labbook-1")
        assert lb_loaded.active_branch == 'gm.workspace-test'

        assert lb_loaded.root_dir == os.path.join(mock_config_file[1], "test", "test", "labbooks", "new-labbook-1")
        assert type(lb) == LabBook

        # Validate labbook data file
        assert lb_loaded.id == lb.id
        assert lb_loaded.name == "new-labbook-1"
        assert lb_loaded.description == "an updated description"

    def test_validate_new_labbook_name(self, mock_config_file):
        lb = LabBook(mock_config_file[0])
        lb.new(owner={"username": "test"}, name="name-validate-test", description="validate tests.")

        bad_labbook_names = [
            None, "", "-", "--", "--a", '_', "-a", "a-", "$#Q", "Catbook4me", "--MeowMe", "-meow-4-me-",
            "r--jacob-vogelstein", "Bad!", "----a----", "4---a--5---a", "cats-" * 200, "Catbook_",
            "4underscores_not_allowed", "my--labbook1",
            "-DNf84329DSJfdj3820jg"
        ]

        allowed_labbook_names = [
            "r-jacob-vogelstein", "chewy-dog", "chewy-dog-99", "9-sdfysc-2-42-aadsda-a43", 'a' * 99, '2-22-222-3333',
            '9' * 50
        ]

        for bad in bad_labbook_names:
            with pytest.raises(ValueError):
                lb.name = bad

        for good in allowed_labbook_names:
            lb.name = good

    def test_make_path_relative(self):
        vectors = [
            # In format of input: expected output
            (None, None),
            ('', ''),
            ('/', ''),
            ('//', ''),
            ('/////cats', 'cats'),
            ('//cats///', 'cats///'),
            ('cats', 'cats'),
            ('/cats/', 'cats/'),
            ('complex/.path/.like/this', 'complex/.path/.like/this'),
            ('//complex/.path/.like/this', 'complex/.path/.like/this')
        ]
        for sample_input, expected_output in vectors:
            assert LabBook.make_path_relative(sample_input) == expected_output

    def test_labbook_key(self, mock_config_file):
        lb = LabBook(mock_config_file[0])
        lb.new(owner={"username": "test"}, name="test-lb-key", description="validate tests.")
        assert lb.key == 'test|test|test-lb-key'

    def test_sweep_uncommitted_changes(self, mock_config_file):
        """ Test sweep covers Added, Removed, and """
        lb = LabBook(mock_config_file[0])
        lb.new(owner={"username": "test"}, name="test-insert-files-1", description="validate tests.")

        with open(os.path.join(lb.root_dir, 'input', 'sillyfile'), 'wb') as newf:
            newf.write(os.urandom(2 ** 24))

        assert 'input/sillyfile' in lb.git.status()['untracked']
        lb.sweep_uncommitted_changes()
        s = lb.git.status()
        assert all([len(s[key]) == 0 for key in s.keys()])

        with open(os.path.join(lb.root_dir, 'input', 'sillyfile'), 'wb') as newf:
            newf.write(os.urandom(2 ** 16))
        assert 'input/sillyfile' in [n[0] for n in lb.git.status()['unstaged']]
        lb.sweep_uncommitted_changes()
        s = lb.git.status()
        assert all([len(s[key]) == 0 for key in s.keys()])
        os.remove(os.path.join(lb.root_dir, 'input', 'sillyfile'))
        assert 'input/sillyfile' in [n[0] for n in lb.git.status()['unstaged']]

        lb.sweep_uncommitted_changes()
        s = lb.git.status()
        assert all([len(s[key]) == 0 for key in s.keys()])

        assert any(['1 new file(s)' in l['message'] for l in lb.git.log()])

    def test_create_labbook_with_author(self, mock_config_file):
        """Test creating an empty labbook with the author set"""
        lb = LabBook(mock_config_file[0], author=GitAuthor(name="username", email="user1@test.com"))

        labbook_dir = lb.new(username="test", name="labbook1", description="my first labbook",
                             owner={"username": "test"})

        assert labbook_dir == os.path.join(mock_config_file[1], "test", "test", "labbooks", "labbook1")
        assert type(lb) == LabBook

        # Validate directory structure
        assert os.path.isdir(os.path.join(labbook_dir, "code")) is True
        assert os.path.isdir(os.path.join(labbook_dir, "input")) is True
        assert os.path.isdir(os.path.join(labbook_dir, "output")) is True
        assert os.path.isdir(os.path.join(labbook_dir, ".gigantum")) is True
        assert os.path.isdir(os.path.join(labbook_dir, ".gigantum", "env")) is True
        assert os.path.isdir(os.path.join(labbook_dir, ".gigantum", "activity")) is True
        assert os.path.isdir(os.path.join(labbook_dir, ".gigantum", "activity", "log")) is True
        assert os.path.isdir(os.path.join(labbook_dir, ".gigantum", "activity", "index")) is True

        # Validate labbook data file
        with open(os.path.join(labbook_dir, ".gigantum", "labbook.yaml"), "rt") as data_file:
            data = yaml.load(data_file)

        assert data["labbook"]["name"] == "labbook1"
        assert data["labbook"]["description"] == "my first labbook"
        assert "id" in data["labbook"]
        assert data["owner"]["username"] == "test"

        log_data = lb.git.log()
        assert log_data[0]['author']['name'] == "username"
        assert log_data[0]['author']['email'] == "user1@test.com"
        assert log_data[0]['committer']['name'] == "Gigantum AutoCommit"
        assert log_data[0]['committer']['email'] == "noreply@gigantum.io"

    def test_read_write_readme(self, mock_config_file):
        """Test creating a reading and writing a readme file to the labbook"""
        lb = LabBook(mock_config_file[0], author=GitAuthor(name="test", email="test@test.com"))

        labbook_dir = lb.new(username="test", name="labbook1", description="my first labbook",
                             owner={"username": "test"})

        assert lb.get_readme() is None
        assert os.path.exists(os.path.join(lb.root_dir, 'README.md')) is False

        lb.write_readme("## Summary\nThis is my readme")

        assert os.path.exists(os.path.join(lb.root_dir, 'README.md')) is True

        assert lb.get_readme() == "## Summary\nThis is my readme"

    def test_readme_size_limit(self, mock_config_file):
        """Test creating a reading and writing a readme file to the labbook"""
        lb = LabBook(mock_config_file[0], author=GitAuthor(name="test", email="test@test.com"))

        labbook_dir = lb.new(username="test", name="labbook1", description="my first labbook",
                             owner={"username": "test"})

        assert lb.get_readme() is None
        assert os.path.exists(os.path.join(lb.root_dir, 'README.md')) is False

        with pytest.raises(ValueError):
            lb.write_readme("A" * (6 * 1000000))

        assert lb.get_readme() is None
        assert os.path.exists(os.path.join(lb.root_dir, 'README.md')) is False

    def test_readme_wierd_strings(self, mock_config_file):
        """Test creating a reading and writing a readme file to the labbook with complex strings"""
        lb = LabBook(mock_config_file[0], author=GitAuthor(name="test", email="test@test.com"))

        labbook_dir = lb.new(username="test", name="labbook1", description="my first labbook",
                             owner={"username": "test"})

        assert lb.get_readme() is None
        assert os.path.exists(os.path.join(lb.root_dir, 'README.md')) is False

        rand_str = os.urandom(1000000)
        with pytest.raises(TypeError):
            lb.write_readme(rand_str)

        assert lb.get_readme() is None
        assert os.path.exists(os.path.join(lb.root_dir, 'README.md')) is False

        with pytest.raises(TypeError):
            lb.write_readme(None)

        assert lb.get_readme() is None
        assert os.path.exists(os.path.join(lb.root_dir, 'README.md')) is False

        lb.write_readme("")

        assert lb.get_readme() == ""
        assert os.path.exists(os.path.join(lb.root_dir, 'README.md')) is True
