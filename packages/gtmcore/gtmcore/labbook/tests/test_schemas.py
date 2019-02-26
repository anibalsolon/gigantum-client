
import os
from pkg_resources import resource_filename
import tempfile

from gtmcore.labbook.schemas import validate_labbook_schema, migrate_schema_to_current, translate_schema, CURRENT_SCHEMA
from gtmcore.configuration.utils import call_subprocess
from gtmcore.inventory.inventory import InventoryManager
from gtmcore.fixtures import mock_config_file


class TestLabBook(object):
    def test_migrate(self, mock_config_file):
        p = resource_filename('gtmcore', 'labbook')
        p2 = os.path.join(p, 'tests', 'test.zip')

        with tempfile.TemporaryDirectory() as td:
            call_subprocess(f"unzip {p2} -d {td}".split(), cwd=td)
            temp_lb_path = os.path.join(td, 'test')

            # Tests backwards compatibility (test.zip is a very old schema 1 LabBook)
            lb = InventoryManager(mock_config_file[0]).load_labbook_from_directory(temp_lb_path)
            assert lb.schema < CURRENT_SCHEMA

            # Test schema migration -- migrate and then refresh.
            migrate_schema_to_current(lb.root_dir)
            lb = InventoryManager(mock_config_file[0]).load_labbook_from_directory(lb.root_dir)
            assert validate_labbook_schema(CURRENT_SCHEMA, lb_data=lb.data)
            assert lb.schema == CURRENT_SCHEMA
