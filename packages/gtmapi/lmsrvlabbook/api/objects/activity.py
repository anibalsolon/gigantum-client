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
from graphene.types import datetime

from gtmcore.logging import LMLogger
from gtmcore.activity import ActivityStore, ActivityDetailRecord, ActivityDetailType, ActivityType, ActivityAction

from lmsrvcore.api.interfaces import GitRepository
from lmsrvcore.auth.user import get_logged_in_username


logger = LMLogger.get_logger()

# Bring ActivityType enumeration into Graphene
ActivityRecordTypeEnum = graphene.Enum.from_enum(ActivityType)

# Bring ActivityDeatilType enumeration into Graphene
ActivityDetailTypeEnum = graphene.Enum.from_enum(ActivityDetailType)

# Bring ActivityActionType enumeration into Graphene
ActivityActionTypeEnum = graphene.Enum.from_enum(ActivityAction)


class ActivityDetailObject(graphene.ObjectType, interfaces=(graphene.relay.Node, GitRepository)):
    """Container for Activity Detail Records"""
    # The loaded detail record data
    _detail_record = None

    # Unique key for this activity detail record in the detail db
    key = graphene.String(required=True)

    # A list of data elements, encoded for the web, with the format [[MIME_TYPE, DATA],]
    data = graphene.List(graphene.List(graphene.String))

    # Type indicating the type of activity detail object
    type = graphene.Field(ActivityDetailTypeEnum)

    # Type indicating the action modifier of activity
    action = graphene.Field(ActivityActionTypeEnum)

    # Boolean indicating if this item should be "shown" or "hidden"
    show = graphene.Boolean()

    # A score indicating the importance, currently expected to range from 0-255
    importance = graphene.Int()

    # A list of tags for the entire record
    tags = graphene.List(graphene.String)

    def _load_detail_record(self, dataloader):
        """Private method to load a detail record if it has not been previously loaded and set"""
        if not self._detail_record:
            # Load record from database
            if not self.key:
                raise ValueError("Must set `key` on object creation to resolve detail record")

            # Load store instance
            lb = dataloader.load(f"{get_logged_in_username()}&{self.owner}&{self.name}").get()
            store = ActivityStore(lb)

            # Retrieve record
            self._detail_record: ActivityDetailRecord = store.get_detail_record(self.key)

        # Set class properties
        self.type = ActivityDetailTypeEnum.get(self._detail_record.type.value).value
        self.show = self._detail_record.show
        self.tags = self._detail_record.tags
        self.importance = self._detail_record.importance
        self.action = ActivityActionTypeEnum.get(self._detail_record.action.value).value

    @classmethod
    def get_node(cls, info, id):
        """Method to resolve the object based on it's Node ID"""
        # Parse the key
        owner, name, key = id.split("&")

        return ActivityDetailObject(id=f"{owner}&{name}&{key}", name=name, owner=owner, key=key)

    def resolve_id(self, info):
        """Resolve the unique Node id for this object"""
        if not self.id:
            if not self.owner or not self.name or not self.key:
                raise ValueError("Resolving a ActivityDetailObject Node ID requires owner, name, and key to be set")
            self.id = f"{self.owner}&{self.name}&{self.key}"

        return self.id

    def resolve_type(self, info):
        """Resolve the type field"""
        if self.type is None:
            self._load_detail_record(info.context.labbook_loader)
        return self.type

    def resolve_action(self, info):
        """Resolve the action field"""
        if self.action is None:
            self._load_detail_record(info.context.labbook_loader)
        return self.action

    def resolve_show(self, info):
        """Resolve the show field"""
        if self.show is None:
            self._load_detail_record(info.context.labbook_loader)
        return self.show

    def resolve_importance(self, info):
        """Resolve the importance field"""
        if self.importance is None:
            self._load_detail_record(info.context.labbook_loader)
        return self.importance

    def resolve_tags(self, info):
        """Resolve the tags field"""
        if self.tags is None:
            self._load_detail_record(info.context.labbook_loader)
        return self.tags

    def resolve_data(self, info):
        """Resolve the data field"""
        if self.data is None:
            self._load_detail_record(info.context.labbook_loader)

        # JSONify for transport via web
        data_dict = self._detail_record.jsonify_data()

        return [(x, data_dict[x]) for x in data_dict]


class ActivityRecordObject(graphene.ObjectType, interfaces=(graphene.relay.Node, GitRepository)):
    """Container for Activity Records"""
    # An instance of the loaded activity record data
    _activity_record = None

    # Commit hash for this activity record
    commit = graphene.String(required=True)

    # Commit hash of the commit this references
    linked_commit = graphene.String()

    # Message summarizing the Activity
    message = graphene.String()

    # Storage for detail objects
    detail_objects = graphene.List(ActivityDetailObject)

    # Type indicating the type of activity
    type = graphene.Field(ActivityRecordTypeEnum)

    # Boolean indicating if this item should be "shown" or "hidden"
    show = graphene.Boolean()

    # A score indicating the importance, currently expected to range from 0-255
    importance = graphene.Int()

    # A list of tags for the entire record
    tags = graphene.List(graphene.String)

    # Datetime of the record creation
    timestamp = datetime.DateTime()

    # Username of the user who created the activity record
    username = graphene.String()

    # Email of the user who created the activity record
    email = graphene.String()

    def _load_activity_record(self, dataloader):
        """Private method to load an activity record if it has not been previously loaded and set"""
        if not self._activity_record:
            # Load record from database
            if not self.commit:
                raise ValueError("Must set `commit` on object creation to resolve detail record")

            # Load store instance
            lb = dataloader.load(f"{get_logged_in_username()}&{self.owner}&{self.name}").get()
            store = ActivityStore(lb)

            # Retrieve record
            self._activity_record = store.get_activity_record(self.commit)

        # Set class properties
        self.linked_commit = self._activity_record.linked_commit
        self.message = self._activity_record.message
        self.type = ActivityRecordTypeEnum.get(self._activity_record.type.value).value
        self.show = self._activity_record.show
        self.tags = self._activity_record.tags
        self.timestamp = self._activity_record.timestamp
        self.importance = self._activity_record.importance
        self.username = self._activity_record.username
        self.email = self._activity_record.email

    @classmethod
    def get_node(cls, info, id):
        """Method to resolve the object based on it's Node ID"""
        # Parse the key
        owner, name, commit = id.split("&")

        return ActivityRecordObject(id=f"{owner}&{name}&{commit}", name=name, owner=owner, commit=commit)

    def resolve_id(self, info):
        """Resolve the unique Node id for this object"""
        if not self.id:
            if not self.owner or not self.name or not self.commit:
                raise ValueError("Resolving a ActivityRecordObject Node ID requires owner, name, and commit to be set")
            self.id = f"{self.owner}&{self.name}&{self.commit}"

        return self.id

    def resolve_linked_commit(self, info):
        """Resolve the linked_commit field"""
        if self.linked_commit is None:
            self._load_activity_record(info.context.labbook_loader)
        return self.linked_commit

    def resolve_message(self, info):
        """Resolve the message field"""
        if self.message is None:
            self._load_activity_record(info.context.labbook_loader)
        return self.message

    def resolve_type(self, info):
        """Resolve the type field"""
        if self.type is None:
            self._load_activity_record(info.context.labbook_loader)
        return self.type

    def resolve_show(self, info):
        """Resolve the show field"""
        if self.show is None:
            self._load_activity_record(info.context.labbook_loader)
        return self.show

    def resolve_tags(self, info):
        """Resolve the tags field"""
        if self.tags is None:
            self._load_activity_record(info.context.labbook_loader)
        return self.tags

    def resolve_timestamp(self, info):
        """Resolve the timestamp field"""
        if self.timestamp is None:
            self._load_activity_record(info.context.labbook_loader)
        return self.timestamp

    def resolve_importance(self, info):
        """Resolve the importance field"""
        if self.importance is None:
            self._load_activity_record(info.context.labbook_loader)
        return self.importance

    def resolve_username(self, info):
        """Resolve the username field"""
        if self.username is None:
            self._load_activity_record(info.context.labbook_loader)
        return self.username

    def resolve_email(self, info):
        """Resolve the email field"""
        if self.email is None:
            self._load_activity_record(info.context.labbook_loader)
        return self.email

    def resolve_detail_objects(self, info):
        """Resolve the detail_objects field"""
        if self.detail_objects is None:
            if self._activity_record is None:
                # Load the activity record first if it is missing
                self._load_activity_record(info.context.labbook_loader)

            # Load detail objects from database
            with self._activity_record.inspect_detail_objects() as details:
                self.detail_objects = [ActivityDetailObject(id=f"{self.owner}&{self.name}&{d.key}",
                                                            owner=self.owner,
                                                            name=self.name,
                                                            key=d.key,
                                                            show=d.show,
                                                            tags=d.tags,
                                                            importance=d.importance,
                                                            action=ActivityActionTypeEnum.get(d.action.value).value,
                                                            type=ActivityDetailTypeEnum.get(d.type.value).value) for d in details]

        return self.detail_objects
