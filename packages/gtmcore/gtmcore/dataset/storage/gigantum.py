from gtmcore.dataset.storage.backend import StorageBackend


class GigantumObjectStore(StorageBackend):

    def _backend_metadata(self) -> dict:
        """Method to specify Storage Backend metadata for each implementation. This is used to render the UI

        Simply implement this method in a child class. Note, 'icon' should be the name of the icon file saved in the
        thumbnails directory. It should be a 128x128 px PNG image.

        Returns:
            dict
        """
        return {"storage_type": "gigantum_object_v1",
                "name": "Gigantum Cloud",
                "description": "Scalable Dataset storage provided by your Gigantum account",
                "tags": ["gigantum"],
                "icon": "gigantum_object_storage.png",
                "url": "https://docs.gigantum.com",
                "is_managed": True,
                "readme": """Gigantum Cloud Datasets are backed by a scalable object storage service that is linked to
your Gigantum account and credentials. It provides efficient storage at the file level and works seamlessly with the 
Client.

This dataset type is fully managed. That means as you modify data, each version will be tracked independently. Syncing
to Gigantum Cloud will count towards your storage quota and include all versions of files.
"""}
