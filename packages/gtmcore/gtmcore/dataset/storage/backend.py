import abc
import os
from pkg_resources import resource_filename
import base64


class StorageBackend(metaclass=abc.ABCMeta):
    """"""

    def __init__(self):
        pass

    def _backend_metadata(self) -> dict:
        """Method to specify Storage Backend metadata for each implementation. This is used to render the UI

        Simply implement this method in a child class. Note, 'icon' should be the name of the icon file saved in the
        thumbnails directory. It should be a 128x128 px PNG image.

        return {"storage_type": "a_unique_identifier",
                "name": "My Dataset Type",
                "description": "Short string",
                "readme": "Long string",
                "tags": ["tag1", 'tag2'],
                "icon": "my_icon.png"
                "url": "http://moreinfo.com"
                }

        Returns:
            dict
        """
        raise NotImplemented

    @property
    def metadata(self):
        """

        Returns:

        """
        metadata = self._backend_metadata()

        dataset_pkg = resource_filename('gtmcore', 'dataset')
        icon_file = os.path.join(dataset_pkg, 'storage', 'thumbnails', metadata['icon'])

        with open(icon_file, 'rb') as icf:
            metadata['icon'] = base64.b64encode(icf.read()).decode("utf-8")

        return metadata
