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
import re
import yaml
import datetime
import json

from typing import (Dict, Optional)

from gtmcore.gitlib import GitAuthor
from gtmcore.dataset.schemas import validate_dataset_schema
from gtmcore.activity import ActivityType, ActivityDetailType

from gtmcore.inventory.repository import Repository


class Dataset(Repository):
    """Class representing a single LabBook"""
    _default_activity_type = ActivityType.DATASET
    _default_activity_detail_type = ActivityDetailType.DATASET
    _default_activity_section = "Dataset Root"

    def __init__(self, config_file: Optional[str] = None, namespace: Optional[str] = None,
                 author: Optional[GitAuthor] = None) -> None:
        super().__init__(config_file, author)

        self.namespace = namespace

    def __str__(self):
        if self._root_dir:
            return f'<Dataset at `{self._root_dir}`>'
        else:
            return f'<Dataset UNINITIALIZED>'

    def __eq__(self, other):
        return isinstance(other, Dataset) and other.root_dir == self.root_dir

    @property
    def id(self) -> str:
        if self._data:
            return self._data["id"]
        else:
            raise ValueError("No ID assigned to the Dataset.")

    @property
    def name(self) -> str:
        if self._data:
            return self._data["name"]
        else:
            raise ValueError("No name assigned to the Dataset.")

    @name.setter
    def name(self, value: str) -> None:
        if not value:
            raise ValueError("value cannot be None or empty")

        if not self._data:
            self._data = {'name': value}
        else:
            self._data["name"] = value
        self._validate_gigantum_data()

        # Update data file
        self._save_gigantum_data()

        # Rename directory
        if self._root_dir:
            base_dir, _ = self._root_dir.rsplit(os.path.sep, 1)
            os.rename(self._root_dir, os.path.join(base_dir, value))
        else:
            raise ValueError("Dataset root dir not specified. Failed to configure git.")

        # Update the root directory to the new directory name
        self._set_root_dir(os.path.join(base_dir, value))

    @property
    def creation_date(self) -> Optional[datetime.datetime]:
        """Get creation date from the gigantum.yaml file"""
        if self._data:
            created_at = self._data["created_on"]
            d = datetime.datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%S.%f')
            return d
        else:
            raise ValueError("No creation date set.")

    @property
    def build_details(self) -> Optional[Dict[str, str]]:
        if self._data:
            return self._data.get("build_info")
        else:
            return None

    @property
    def description(self) -> str:
        if self._data:
            return self._data["description"]
        else:
            raise ValueError("No description assigned to this Dataset.")

    @description.setter
    def description(self, value) -> None:
        if not self._data:
            self._data = {'description': value}
        else:
            self._data["description"] = value

        self._save_gigantum_data()

    @property
    def storage_type(self) -> str:
        if self._data:
            return self._data["storage_type"]
        else:
            raise ValueError("No storage type assigned to this Dataset.")

    @storage_type.setter
    def storage_type(self, value) -> None:
        if not self._data:
            self._data = {'storage_type': value}
        else:
            self._data["storage_type"] = value

        self._save_gigantum_data()

    @property
    def storage_config(self) -> dict:
        """Property to load the storage.json file"""
        with open(os.path.join(self.root_dir, ".gigantum", "storage.json"), 'rt') as sf:
            data = json.load(sf)

        return data

    @storage_config.setter
    def storage_config(self, data: dict) -> None:
        """Save storage config data"""
        with open(os.path.join(self.root_dir, ".gigantum", "storage.json"), 'wt') as sf:
            json.dump(data, sf, indent=2)

    def _save_gigantum_data(self) -> None:
        """Method to save changes to the LabBook

        Returns:
            None
        """
        if not self.root_dir:
            raise ValueError("No root directory assigned to Dataset. Failed to get root directory.")

        with open(os.path.join(self.root_dir, ".gigantum", "gigantum.yaml"), 'wt') as df:
            df.write(yaml.dump(self._data, default_flow_style=False))
            df.flush()

    def _load_gigantum_data(self) -> None:
        """Method to load the labbook YAML file to a dictionary

        Returns:
            None
        """
        if not self.root_dir:
            raise ValueError("No root directory assigned to Dataset. Failed to get root directory.")

        with open(os.path.join(self.root_dir, ".gigantum", "gigantum.yaml"), 'rt') as df:
            self._data = yaml.load(df)

    def _validate_gigantum_data(self) -> None:
        """Method to validate the LabBook data file contents

        Returns:
            None
        """
        if not re.match("^(?!-)(?!.*--)[a-z0-9-]+(?<!-)$", self.name):
            raise ValueError("Invalid `name`. Only a-z 0-9 and hyphens allowed. No leading or trailing hyphens.")

        if len(self.name) > 100:
            raise ValueError("Invalid `name`. Max length is 100 characters")

        # Validate schema is supported by running version of the software and valid
        if not validate_dataset_schema(self.schema, self.data):
            errmsg = f"Schema in Dataset {str(self)} does not match indicated version {self.schema}"
            raise ValueError(errmsg)
