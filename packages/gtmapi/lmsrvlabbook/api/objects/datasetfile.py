import graphene
import base64

from gtmcore.dataset.files import DatasetFileOperations
from lmsrvcore.api.interfaces import GitRepository
from lmsrvcore.auth.user import get_logged_in_username


class DatasetFile(graphene.ObjectType, interfaces=(graphene.relay.Node, GitRepository)):
    """A type representing a file or directory inside the dataset file system."""
    # Loaded file info
    _file_info = None

    # Relative path from labbook section.
    key = graphene.String(required=True)

    # True indicates that path points to a directory
    is_dir = graphene.Boolean()

    # True indicates that path points to a favorite
    is_favorite = graphene.Boolean()

    # Modified at contains timestamp of last modified - NOT creation - in epoch time.
    modified_at = graphene.Int()

    # Size in bytes encoded as a string.
    size = graphene.String()

    def _load_file_info(self, dataloader):
        """Private method to retrieve file info for a given key"""
        if not self._file_info:
            # Load file info from LabBook
            if not self.section or not self.key:
                raise ValueError("Must set `section` and `key` on object creation to resolve file info")

            # Load dataset instance
            username = get_logged_in_username()
            ds = dataloader.load(f"{username}&{self.owner}&{self.name}").get()

            # Retrieve file info
            self._file_info = DatasetFileOperations.get_file_info(ds, self.key, username)

        # Set class properties
        self.is_dir = self._file_info['is_dir']
        self.modified_at = self._file_info['modified_at']
        self.size = f"{self._file_info['size']}"
        self.is_favorite = self._file_info['is_favorite']

    @classmethod
    def get_node(cls, info, id):
        """Method to resolve the object based on it's Node ID"""
        # Parse the key
        owner, name, section, key = id.split("&")

        return DatasetFile(id=f"{owner}&{name}&{key}", name=name, owner=owner, section=section, key=key)

    def resolve_id(self, info):
        """Resolve the unique Node id for this object"""
        if not self.id:
            if not self.owner or not self.name or not self.key:
                raise ValueError("Resolving a DatasetFile Node ID requires owner, name, and key to be set")
            self.id = f"{self.owner}&{self.name}&{self.key}"

        return self.id

    def resolve_is_dir(self, info):
        """Resolve the is_dir field"""
        if self.is_dir is None:
            self._load_file_info(info.context.dataset_loader)
        return self.is_dir

    def resolve_modified_at(self, info):
        """Resolve the modified_at field"""
        if self.modified_at is None:
            self._load_file_info(info.context.dataset_loader)
        return self.modified_at

    def resolve_size(self, info):
        """Resolve the size field"""
        if self.size is None:
            self._load_file_info(info.context.dataset_loader)
        return self.size

    def resolve_is_favorite(self, info):
        """Resolve the is_favorite field"""
        if self.is_favorite is None:
            self._load_file_info(info.context.dataset_loader)
        return self.is_favorite
