import pytest
import getpass
import os
import yaml
import time

from gtmcore.files import FileOperations
from gtmcore.labbook import LabBook, LabbookException
from gtmcore.labbook.inventory import InventoryManager, InventoryException
from gtmcore.gitlib.git import GitAuthor
from gtmcore.fixtures import mock_config_file, mock_labbook, remote_labbook_repo, sample_src_file


class TestInventory(object):

    def test_testabc(self):
        time.sleep(2)

    def test_uses_config(self, mock_config_file):
        i = InventoryManager(mock_config_file[0])
        assert i.inventory_root == mock_config_file[1]

    def test_list_labbooks_empty(self, mock_config_file):
        i = InventoryManager(mock_config_file[0])
        assert len(i.list_labbook_ids(username="none")) == 0

    def test_list_labbooks_wrong_base_dir(self, mock_config_file):
        i = InventoryManager(mock_config_file[0])
        assert i.list_labbook_ids(username="not-a-user") == []

    def test_list_labbooks_full_set(self, mock_config_file):
        ut_username = "ut-owner-1"
        owners = [f"ut-owner-{i}" for i in range(4)]
        lbnames = [f'unittest-labbook-{i}' for i in range(6)]
        created_lbs = []
        for ow in owners:
            for lbname in lbnames:
                l = LabBook(mock_config_file[0])
                l.new(owner={'username': ow}, name=lbname, username=ut_username)
                created_lbs.append(l)

        condensed_lbs = [(ut_username, l.owner['username'], l.name) for l in created_lbs]
        inv_manager = InventoryManager(mock_config_file[0])
        t0 = time.time()
        result_under_test = inv_manager.list_labbook_ids(username=ut_username)
        assert time.time() - t0 < 1.0, "list_labbook_ids should return in under 1 second"
        assert len(list(set(condensed_lbs))) == 6 * 4
        assert len(list(set(result_under_test))) == 6 * 4
        for r in result_under_test:
            assert r in condensed_lbs

    def test_list_labbooks_az(self, mock_config_file):
        """Test list az labbooks"""
        lb1, lb2, lb3, lb4 = LabBook(mock_config_file[0]), LabBook(mock_config_file[0]), \
                             LabBook(mock_config_file[0]), LabBook(mock_config_file[0])

        labbook_dir1 = lb1.new(username="user1", owner={"username": "user1"},
                               name="labbook0", description="my first labbook")
        labbook_dir2 = lb2.new(username="user1", owner={"username": "user1"},
                               name="labbook12", description="my second labbook")
        labbook_dir3 = lb3.new(username="user1", owner={"username": "user2"},
                               name="labbook3", description="my other labbook")
        labbook_dir4 = lb4.new(username="user2", owner={"username": "user1"},
                               name="labbook4", description="my other labbook")

        inv_manager = InventoryManager(mock_config_file[0])
        labbooks = inv_manager.list_labbooks(username="user1")
        assert len(labbooks) == 3
        assert labbooks[0].name == 'labbook0'
        assert labbooks[1].name == 'labbook3'
        assert labbooks[2].name == 'labbook12'

    def test_list_labbooks_az_reversed(self, mock_config_file):
        """Test list az labbooks, reversed"""
        lb1, lb2, lb3, lb4 = LabBook(mock_config_file[0]), LabBook(mock_config_file[0]), \
                             LabBook(mock_config_file[0]), LabBook(mock_config_file[0])

        labbook_dir1 = lb1.new(username="user1", owner={"username": "user1"},
                               name="labbook1", description="my first labbook")
        labbook_dir2 = lb2.new(username="user1", owner={"username": "user1"},
                               name="labbook2", description="my second labbook")
        labbook_dir3 = lb3.new(username="user1", owner={"username": "user2"},
                               name="labbook3", description="my other labbook")

        labbook_dir4 = lb4.new(username="user2", owner={"username": "user1"},
                               name="labbook4", description="my other labbook")

        assert labbook_dir1 == os.path.join(mock_config_file[1], "user1", "user1", "labbooks", "labbook1")
        assert labbook_dir2 == os.path.join(mock_config_file[1], "user1", "user1", "labbooks", "labbook2")
        assert labbook_dir3 == os.path.join(mock_config_file[1], "user1", "user2", "labbooks", "labbook3")
        assert labbook_dir4 == os.path.join(mock_config_file[1], "user2", "user1", "labbooks", "labbook4")

        inv_manager = InventoryManager(mock_config_file[0])
        with pytest.raises(InventoryException):
            inv_manager.list_labbooks(username="user1", sort_mode='asdf')

        labbooks = inv_manager.list_labbooks(username="user1", sort_mode='name')
        labbooks.reverse()
        assert len(labbooks) == 3
        assert labbooks[0].name == 'labbook3'
        assert labbooks[1].name == 'labbook2'
        assert labbooks[2].name == 'labbook1'

    def test_list_labbooks_create_date(self, mock_config_file):
        """Test list create dated sorted labbooks"""
        lb1, lb2, lb3 = LabBook(mock_config_file[0]), LabBook(mock_config_file[0]), LabBook(mock_config_file[0])

        lb1.new(username="user1", owner={"username": "user1"},
                name="labbook3", description="my first labbook")
        lb2.new(username="user1", owner={"username": "user1"},
                name="asdf", description="my second labbook")
        lb3.new(username="user1", owner={"username": "user2"},
                name="labbook1", description="my other labbook")

        inv_manager = InventoryManager(mock_config_file[0])
        labbooks = inv_manager.list_labbooks(username="user1", sort_mode="created_on")

        assert len(labbooks) == 3
        assert labbooks[0].name == 'labbook3'
        assert labbooks[1].name == 'asdf'
        assert labbooks[2].name == 'labbook1'

    def test_list_labbooks_create_date_no_metadata(self, mock_config_file):
        """Test list create dated sorted labbooks"""
        lb1, lb2, lb3 = LabBook(mock_config_file[0]), LabBook(mock_config_file[0]), LabBook(mock_config_file[0])

        lb1.new(username="user1", owner={"username": "user1"},
                name="labbook3", description="my first labbook")
        time.sleep(1.1)
        lb2.new(username="user1", owner={"username": "user1"},
                name="asdf", description="my second labbook")
        time.sleep(1.1)
        lb3.new(username="user1", owner={"username": "user2"},
                name="labbook1", description="my other labbook")
        time.sleep(1.1)

        inv_manager = InventoryManager(mock_config_file[0])
        labbooks = inv_manager.list_labbooks(username="user1", sort_mode="created_on")

        assert len(labbooks) == 3
        assert labbooks[0].name == 'labbook3'
        assert labbooks[1].name == 'asdf'
        assert labbooks[2].name == 'labbook1'

        os.remove(os.path.join(lb1.root_dir, '.gigantum', 'buildinfo'))
        os.remove(os.path.join(lb3.root_dir, '.gigantum', 'buildinfo'))

        labbooks = inv_manager.list_labbooks(username="user1", sort_mode="created_on")

        assert len(labbooks) == 3
        assert labbooks[0].name == 'labbook3'
        assert labbooks[1].name == 'asdf'
        assert labbooks[2].name == 'labbook1'

        os.remove(os.path.join(lb2.root_dir, '.gigantum', 'labbook.yaml'))
        labbooks = inv_manager.list_labbooks(username="user1", sort_mode='modified_on')
        assert len(labbooks) == 2

    def test_list_labbooks_create_date_reversed(self, mock_config_file):
        """Test list create dated sorted labbooks reversed"""
        lb1, lb2, lb3, lb4 = LabBook(mock_config_file[0]), LabBook(mock_config_file[0]), \
                             LabBook(mock_config_file[0]), LabBook(mock_config_file[0])

        lb1.new(username="user1", owner={"username": "user1"},
                name="labbook3", description="my first labbook")
        lb2.new(username="user1", owner={"username": "user1"},
                name="asdf", description="my second labbook")
        lb3.new(username="user1", owner={"username": "user2"},
                name="labbook1", description="my other labbook")
        lb4.new(username="user1", owner={"username": "user1"},
                name="labbook4", description="my other labbook")

        inv_manager = InventoryManager(mock_config_file[0])
        labbooks = inv_manager.list_labbooks(username="user1", sort_mode="created_on")
        labbooks.reverse()

        assert len(labbooks) == 4
        assert labbooks[0].name == 'labbook4'
        assert labbooks[1].name == 'labbook1'
        assert labbooks[2].name == 'asdf'
        assert labbooks[3].name == 'labbook3'

    def test_list_labbooks_modified_date(self, mock_config_file):
        """Test list modified dated sorted labbooks"""
        lb1, lb2, lb3, lb4 = LabBook(mock_config_file[0]), LabBook(mock_config_file[0]), \
                             LabBook(mock_config_file[0]), LabBook(mock_config_file[0])

        lb1.new(username="user1", owner={"username": "user1"},
                name="labbook3", description="my first labbook")
        time.sleep(1.2)
        lb2.new(username="user1", owner={"username": "user1"},
                name="asdf", description="my second labbook")
        time.sleep(1.2)
        lb3.new(username="user1", owner={"username": "user2"},
                name="labbook1", description="my other labbook")
        time.sleep(1.2)
        lb4.new(username="user1", owner={"username": "user1"},
                name="hhghg", description="my other labbook")

        inv_manager = InventoryManager(mock_config_file[0])
        labbooks = inv_manager.list_labbooks(username="user1", sort_mode="modified_on")

        assert len(labbooks) == 4
        assert labbooks[0].name == 'labbook3'
        assert labbooks[1].name == 'asdf'
        assert labbooks[2].name == 'labbook1'
        assert labbooks[3].name == 'hhghg'

        # modify a repo
        time.sleep(1.2)
        with open(os.path.join(lb2.root_dir, "code", "test.txt"), 'wt') as tf:
            tf.write("asdfasdf")

        lb2.git.add_all()
        lb2.git.commit("Changing the repo")

        labbooks = inv_manager.list_labbooks(username="user1", sort_mode="modified_on")

        assert len(labbooks) == 4
        assert labbooks[0].name == 'labbook3'
        assert labbooks[1].name == 'labbook1'
        assert labbooks[2].name == 'hhghg'
        assert labbooks[3].name == 'asdf'

    def test_list_labbooks_modified_date_reversed(self, mock_config_file):
        """Test list modified dated sorted labbooks"""
        lb1, lb2, lb3, lb4 = LabBook(mock_config_file[0]), LabBook(mock_config_file[0]), \
                             LabBook(mock_config_file[0]), LabBook(mock_config_file[0])

        lb1.new(username="user1", owner={"username": "user1"},
                name="labbook3", description="my first labbook")
        time.sleep(1.2)
        lb2.new(username="user1", owner={"username": "user1"},
                name="asdf", description="my second labbook")
        time.sleep(1.2)
        lb3.new(username="user1", owner={"username": "user2"},
                name="labbook1", description="my other labbook")
        time.sleep(1.2)
        lb4.new(username="user1", owner={"username": "user1"},
                name="hhghg", description="my other labbook")

        inv_manager = InventoryManager(mock_config_file[0])
        labbooks = inv_manager.list_labbooks(username="user1", sort_mode="modified_on")
        labbooks.reverse()

        assert len(labbooks) == 4
        assert labbooks[0].name == 'hhghg'
        assert labbooks[1].name == 'labbook1'
        assert labbooks[2].name == 'asdf'
        assert labbooks[3].name == 'labbook3'

        # modify a repo
        time.sleep(1.2)
        with open(os.path.join(lb2.root_dir, "code", "test.txt"), 'wt') as tf:
            tf.write("asdfasdf")

        lb2.git.add_all()
        lb2.git.commit("Changing the repo")

        labbooks = inv_manager.list_labbooks(username="user1", sort_mode="modified_on")
        labbooks.reverse()

        assert len(labbooks) == 4
        assert labbooks[0].name == 'asdf'
        assert labbooks[1].name == 'hhghg'
        assert labbooks[2].name == 'labbook1'
        assert labbooks[3].name == 'labbook3'

    def test_load_labbook_from_directory(self, mock_config_file):
        """Test loading a labbook from a directory"""
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

        # Validate labbook data file
        with open(os.path.join(labbook_dir, ".gigantum", "labbook.yaml"), "rt") as data_file:
            data = yaml.load(data_file)

        assert data["labbook"]["name"] == "labbook1"
        assert data["labbook"]["description"] == "my first labbook"
        assert "id" in data["labbook"]
        assert data["owner"]["username"] == "test"

        lb_loaded = InventoryManager(mock_config_file[0]).load_labbook_from_directory(labbook_dir)
        assert lb.active_branch == 'gm.workspace-test'

        assert lb_loaded.root_dir == os.path.join(mock_config_file[1], "test", "test", "labbooks", "labbook1")
        assert type(lb) == LabBook

        # Validate labbook data file
        assert lb_loaded.root_dir == lb.root_dir
        assert lb_loaded.id == lb.id
        assert lb_loaded.name == lb.name
        assert lb_loaded.description == lb.description

    def test_load_labbook(self, mock_config_file):
        """Test loading a labbook from a directory"""
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

        # Validate labbook data file
        with open(os.path.join(labbook_dir, ".gigantum", "labbook.yaml"), "rt") as data_file:
            data = yaml.load(data_file)

        assert data["labbook"]["name"] == "labbook1"
        assert data["labbook"]["description"] == "my first labbook"
        assert "id" in data["labbook"]
        assert data["owner"]["username"] == "test"

        im = InventoryManager(mock_config_file[0])
        lb_loaded = im.load_labbook("test", "test", "labbook1")
        assert lb_loaded.active_branch == 'gm.workspace-test'
        assert lb_loaded.root_dir == os.path.join(mock_config_file[1], "test", "test", "labbooks", "labbook1")
        assert type(lb) == LabBook

        # Validate labbook data file
        assert lb_loaded.root_dir == lb.root_dir
        assert lb_loaded.id == lb.id
        assert lb_loaded.name == lb.name
        assert lb_loaded.description == lb.description
        assert lb_loaded.key == 'test|test|labbook1'
