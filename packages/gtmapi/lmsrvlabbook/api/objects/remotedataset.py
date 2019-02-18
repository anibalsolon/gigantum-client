# Copyright (c) 2018 FlashX, LLC
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
import graphene

from gtmcore.configuration import Configuration
from gtmcore.workflows.gitlab import GitLabManager
from gtmcore.inventory.inventory import InventoryManager, InventoryException

from lmsrvcore.api.interfaces import GitRepository
from lmsrvcore.auth.user import get_logged_in_username
from lmsrvcore.auth.identity import parse_token


class RemoteDataset(graphene.ObjectType, interfaces=(graphene.relay.Node, GitRepository)):
    """A type representing a Dataset stored on a remote server

    RemoteDatasets are uniquely identified by both the "owner" and the "name" of the Dataset

    NOTE: RemoteDatasets require all fields to be explicitly set as there is no current way to asynchronously retrieve
          the data

    """
    # A short description of the Dataset limited to 140 UTF-8 characters
    description = graphene.String()

    # Whether it is public or private (or local only)
    visibility = graphene.String()

    # Creation date/timestamp in UTC in ISO format
    creation_date_utc = graphene.String()

    # Modification date/timestamp in UTC in ISO format
    modified_date_utc = graphene.String()

    # Flag indicating if the Dataset also exists locally
    is_local = graphene.Boolean()

    @classmethod
    def get_node(cls, info, id):
        """Method to resolve the object based on it's Node ID"""
        # Parse the key
        owner, name = id.split("&")

        return RemoteDataset(id="{}&{}".format(owner, name), name=name, owner=owner)

    def resolve_id(self, info):
        """Resolve the unique Node id for this object"""
        if not self.id:
            if not self.owner or not self.name:
                raise ValueError("Resolving a Remote Dataset Node ID requires owner and name to be set")
            self.id = f"{self.owner}&{self.name}"
        return self.id

    def resolve_visibility(self, info):
        app_config = Configuration().config
        default_remote = app_config['git']['default_remote']
        admin_service = None
        for remote in Configuration().config['git']['remotes']:
            if default_remote == remote:
                admin_service = app_config['git']['remotes'][remote]['admin_service']
                break

        # Extract valid Bearer token
        if "HTTP_AUTHORIZATION" in info.context.headers.environ:
            token = parse_token(info.context.headers.environ["HTTP_AUTHORIZATION"])
        else:
            raise ValueError("Authorization header not provided. Must have a valid session to query for collaborators")

        # Get collaborators from remote service
        mgr = GitLabManager(default_remote, admin_service, token)
        try:
            d = mgr.repo_details(namespace=self.owner, repository_name=self.name)
            return d.get('visibility')
        except ValueError:
            return "unknown"

    def resolve_description(self, info):
        """Return the description of the dataset"""
        if self.description is None:
            raise ValueError("RemoteDataset requires all fields to be explicitly set")
        return self.description

    def resolve_creation_date_utc(self, info):
        """Return the creation timestamp

        Args:
            info:

        Returns:

        """
        if self.creation_date_utc is None:
            raise ValueError("RemoteDataset requires all fields to be explicitly set")
        return self.creation_date_utc

    def resolve_modified_date_utc(self, info):
        """Return the modified timestamp

        Args:
            info:

        Returns:

        """
        if self.modified_date_utc is None:
            raise ValueError("RemoteDataset requires all fields to be explicitly set")
        return self.modified_date_utc

    def resolve_is_local(self, info):
        """Return the modified timestamp

        Args:
            info:

        Returns:

        """
        try:
            username = get_logged_in_username()
            ds = InventoryManager().load_dataset(username, self.owner, self.name)
            return True
        except InventoryException:
            return False
