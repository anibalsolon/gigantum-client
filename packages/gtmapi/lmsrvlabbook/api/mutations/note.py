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

from gtmcore.labbook import InventoryManager
from gtmcore.logging import LMLogger

from gtmcore.activity import ActivityStore, ActivityDetailRecord, ActivityDetailType, ActivityRecord, ActivityType
from lmsrvcore.auth.user import get_logged_in_username, get_logged_in_author

from lmsrvlabbook.api.objects.activity import ActivityRecordObject
from lmsrvlabbook.api.connections.activity import ActivityConnection

logger = LMLogger.get_logger()


class CreateUserNote(graphene.relay.ClientIDMutation):
    """Mutation to create a new user note entry in the activity feed of lab book

    The `linked_commit` is an empty string since there is no linked commit

    """

    class Input:
        owner = graphene.String(required=True)
        labbook_name = graphene.String(required=True)
        title = graphene.String(required=True)
        body = graphene.String(required=False)
        tags = graphene.List(graphene.String, required=False)

    # Return the new Activity Record
    new_activity_record_edge = graphene.Field(lambda: ActivityConnection.Edge)

    @classmethod
    def _create_user_note(cls, lb, title, body, tags):
        store = ActivityStore(lb)
        adr = ActivityDetailRecord(ActivityDetailType.NOTE,
                                   show=True,
                                   importance=255)
        if body:
            adr.add_value('text/markdown', body)

        ar = ActivityRecord(ActivityType.NOTE,
                            message=title,
                            linked_commit="no-linked-commit",
                            importance=255,
                            tags=tags)
        ar.add_detail_object(adr)
        ar = store.create_activity_record(ar)
        return ar

    @classmethod
    def mutate_and_get_payload(cls, root, info, owner, labbook_name, title, body=None, tags=None,
                               client_mutation_id=None):
        username = get_logged_in_username()
        lb = InventoryManager().load_labbook(username, owner, labbook_name,
                                             author=get_logged_in_author())

        with lb.lock_labbook():
            ar = cls._create_user_note(lb, title, body, tags)

        return CreateUserNote(new_activity_record_edge=ActivityConnection.Edge(
            node=ActivityRecordObject(owner=owner,
                                      name=labbook_name,
                                      commit=ar.commit),
            cursor=ar.commit))
