
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

from gtmcore.inventory.inventory import InventoryManager
from gtmcore.inventory.branching import BranchManager

from lmsrvcore.auth.user import get_logged_in_username
from lmsrvcore.api.interfaces import GitCommit, GitRepository



class LabbookCommit(graphene.ObjectType, interfaces=(graphene.relay.Node, GitRepository, GitCommit)):
    """An object representing a commit to a LabBook"""

    @classmethod
    def get_node(cls, info, id):
        """Method to resolve the object based on it's Node ID"""
        # Parse the key
        owner, name, hash_str = id.split("&")

        return LabbookCommit(id=f"{owner}&{name}&{hash_str}", name=name, owner=owner,
                             hash=hash_str)

    def resolve_id(self, info):
        """Resolve the unique Node id for this object"""
        if not self.id:
            if not self.owner or not self.name or not self.hash:
                raise ValueError("Resolving a LabbookCommit Node ID requires owner, name, and hash to be set")
            self.id = f"{self.owner}&{self.name}&{self.hash}"

    def resolve_short_hash(self, info):
        """Resolve the short_hash field"""
        return self.hash[:8]

    def resolve_committed_on(self, info):
        """Resolve the committed_on field"""
        return info.context.labbook_loader.load(f"{get_logged_in_username()}&{self.owner}&{self.name}").then(
            lambda labbook: labbook.git.repo.commit(self.hash).committed_datetime.isoformat())


class Branch(graphene.ObjectType, interfaces=(graphene.relay.Node, GitRepository)):
    """ Represents a branch in the repo """

    branch_name = graphene.String(required=True)

    # If true, indicates this branch is currently checked out
    is_active = graphene.Boolean()

    # Indicates whether this branch exists in the local repo
    is_local = graphene.Boolean()

    # Indicates whether this branch exists remotely
    is_remote = graphene.Boolean()

    # Indicates whether this branch can be merged into the current active branch
    is_mergeable = graphene.Boolean()

    # Count of commits behind remote - zero means up-to-date, positive is behind
    # negative indicates local repo is ahead of remote (unpushed changes)
    commits_behind = graphene.Int()

    @classmethod
    def get_node(cls, info, id):
        owner, labbook_name, branch_name = id.split('&')
        return Branch(owner=owner, name=labbook_name, branch_name=branch_name)

    def resolve_id(self, info):
        return '&'.join((self.owner, self.name, self.branch_name))

    def resolve_is_active(self, info):
        lb = InventoryManager().load_labbook(get_logged_in_username(),
                                             self.owner,
                                             self.name)
        return BranchManager(lb).active_branch == self.branch_name

    def resolve_is_local(self, info):
        lb = InventoryManager().load_labbook(get_logged_in_username(),
                                             self.owner,
                                             self.name)
        return self.branch_name in BranchManager(lb).branches_local

    def resolve_is_remote(self, info):
        lb = InventoryManager().load_labbook(get_logged_in_username(),
                                             self.owner,
                                             self.name)
        return self.branch_name in BranchManager(lb).branches_remote

    def resolve_is_mergeable(self, info):
        lb = InventoryManager().load_labbook(get_logged_in_username(),
                                             self.owner,
                                             self.name)
        mergeable = self.branch_name in BranchManager(lb).branches_local \
                    and self.branch_name != BranchManager(lb).active_branch
        return mergeable

    def resolve_commits_behind(self, info):
        lb = InventoryManager().load_labbook(get_logged_in_username(),
                                             self.owner,
                                             self.name)
        bm = BranchManager(lb)
        if bm.active_branch == self.branch_name:
            _, count = bm.get_commits_behind_remote()
            return count
        else:
            return 0
