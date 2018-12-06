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
import os
import base64

from gtmcore.inventory.inventory import InventoryManager
from gtmcore.logging import LMLogger
from gtmcore.dataset.files import DatasetFileOperations

from lmsrvcore.auth.user import get_logged_in_username, get_logged_in_author
from lmsrvcore.api.mutations import ChunkUploadMutation, ChunkUploadInput

from lmsrvlabbook.api.objects.dataset import Dataset
from lmsrvlabbook.api.connections.datasetfile import DatasetFile, DatasetFileConnection

logger = LMLogger.get_logger()


class CreateDataset(graphene.relay.ClientIDMutation):
    """Mutation for creation of a new Dataset on disk"""

    class Input:
        name = graphene.String(required=True)
        description = graphene.String(required=True)
        storage_type = graphene.String(required=True)

    # Return the dataset instance
    dataset = graphene.Field(Dataset)

    @classmethod
    def mutate_and_get_payload(cls, root, info, name, description, storage_type, client_mutation_id=None):
        username = get_logged_in_username()
        inv_manager = InventoryManager()

        inv_manager.create_dataset(username=username,
                                   owner=username,
                                   dataset_name=name,
                                   description=description,
                                   storage_type=storage_type,
                                   author=get_logged_in_author())

        return CreateDataset(dataset=Dataset(id="{}&{}".format(username, name),
                                             name=name, owner=username))


class AddDatasetFile(graphene.relay.ClientIDMutation, ChunkUploadMutation):
    """Mutation to add a file to a labbook. File should be sent in the
    `uploadFile` key as a multi-part/form upload.
    file_path is the relative path from the labbook section specified."""
    class Input:
        owner = graphene.String(required=True)
        dataset_name = graphene.String(required=True)
        file_path = graphene.String(required=True)
        chunk_upload_params = ChunkUploadInput(required=True)
        transaction_id = graphene.String(required=True)

    new_dataset_file_edge = graphene.Field(DatasetFileConnection.Edge)

    @classmethod
    def mutate_and_wait_for_chunks(cls, info, **kwargs):
        return AddDatasetFile(new_dataset_file_edge=DatasetFileConnection.Edge(node=None, cursor="null"))

    @classmethod
    def mutate_and_process_upload(cls, info, owner, dataset_name,
                                  file_path, chunk_upload_params,
                                  transaction_id, client_mutation_id=None):
        if not cls.upload_file_path:
            logger.error('No file uploaded')
            raise ValueError('No file uploaded')

        try:
            username = get_logged_in_username()
            ds = InventoryManager().load_dataset(username, owner, dataset_name,
                                                 author=get_logged_in_author())
            dstpath = os.path.join(os.path.dirname(file_path), cls.filename)
            with ds.lock():
                fops = DatasetFileOperations.put_file(dataset=ds,
                                                      src_file=cls.upload_file_path,
                                                      dst_path=dstpath,
                                                      username=username,
                                                      txid=transaction_id)
        finally:
            try:
                logger.debug(f"Removing temp file {cls.upload_file_path}")
                os.remove(cls.upload_file_path)
            except FileNotFoundError:
                pass

        # Create data to populate edge
        create_data = {'owner': owner,
                       'name': dataset_name,
                       'key': fops['key'],
                       '_file_info': fops}

        # TODO: Fix cursor implementation..
        # this currently doesn't make sense when adding edges
        cursor = base64.b64encode(f"{0}".encode('utf-8'))
        return AddDatasetFile(new_dataset_file_edge=DatasetFileConnection.Edge(node=DatasetFile(**create_data),
                                                                               cursor=cursor))


class CompleteDatasetUploadTransaction(graphene.relay.ClientIDMutation):

    class Input:
        owner = graphene.String(required=True)
        dataset_name = graphene.String(required=True)
        transaction_id = graphene.String(required=True)
        cancel = graphene.Boolean()
        rollback = graphene.Boolean()

    success = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(cls, root, info, owner, dataset_name,
                               transaction_id, cancel=False, rollback=False,
                               client_mutation_id=None):
        username = get_logged_in_username()
        ds = InventoryManager().load_dataset(username, owner, dataset_name,
                                             author=get_logged_in_author())
        with ds.lock():
            DatasetFileOperations.complete_batch(ds, username, transaction_id, cancel=cancel,
                                                 rollback=rollback)

        return CompleteDatasetUploadTransaction(success=True)
