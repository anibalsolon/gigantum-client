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
from lmsrvlabbook.tests.fixtures import fixture_working_dir

from promise import Promise

from lmsrvlabbook.dataloader.labbook import LabBookLoader
from gtmcore.labbook import LabBook, InventoryManager


class TestDataloaderLabBook(object):

    def test_load_one(self, fixture_working_dir):
        """Test loading 1 labbook"""
        im = InventoryManager(fixture_working_dir[0])
        im.create_labbook("default", "default", "labbook1", description="my first labbook1")
        im.create_labbook("default", "default", "labbook2", description="my first labbook2")
        loader = LabBookLoader()

        key = f"default&default&labbook1"
        promise1 = loader.load(key)
        assert isinstance(promise1, Promise)

        lb = promise1.get()
        assert lb.name == "labbook1"
        assert lb.description == "my first labbook1"

    def test_load_many(self, fixture_working_dir):
        """Test loading many labbooks"""
        im = InventoryManager(fixture_working_dir[0])
        im.create_labbook("default", "default", "labbook1", description="my first labbook1")
        im.create_labbook("default", "default", "labbook2", description="my first labbook2")
        im.create_labbook("default", "test3", "labbook2", description="my first labbook3")

        loader = LabBookLoader()

        keys = ["default&default&labbook1", "default&default&labbook2", "default&test3&labbook2"]
        promise1 = loader.load_many(keys)
        assert isinstance(promise1, Promise)

        lb_list = promise1.get()
        assert lb_list[0].name == "labbook1"
        assert lb_list[0].description == "my first labbook1"
        assert lb_list[1].name == "labbook2"
        assert lb_list[1].description == "my first labbook2"
        assert lb_list[2].name == "labbook2"
        assert lb_list[2].description == "my first labbook3"

