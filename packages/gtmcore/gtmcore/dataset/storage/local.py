import asyncio
import aiohttp
import aiofiles
import copy
import shutil
import zlib
import snappy
import tempfile
import requests

from gtmcore.dataset import Dataset
from gtmcore.dataset.storage.backend import StorageBackend
from typing import Optional, List, Dict, Callable, Tuple
import os

from gtmcore.dataset.io import PushResult, PushObject, PullResult, PullObject
from gtmcore.logging import LMLogger
from gtmcore.dataset.manifest.eventloop import get_event_loop

logger = LMLogger.get_logger()


class LocalFilesystem(StorageBackend):

    def _backend_metadata(self) -> dict:
        """Method to specify Storage Backend metadata for each implementation. This is used to render the UI

        Simply implement this method in a child class. Note, 'icon' should be the name of the icon file saved in the
        thumbnails directory. It should be a 128x128 px PNG image.

        Returns:
            dict
        """
        return {"storage_type": "local_filesystem",
                "name": "Local Filesystem",
                "description": "Dataset type to use locally stored data. No files will sync with this dataset type.",
                "tags": ["local"],
                "icon": "gigantum_object_storage.png",
                "url": "https://docs.gigantum.com",
                "readme": """Local Filesystem datasets simply mount a local directory for use. For security reasons,
only folders located the 'local_data' directory inside your Gigantum working directory can be specified as the dataset
root folder. This means you either need to place data there
"""}

    def _required_configuration(self) -> Dict[str, str]:
        """A private method to return a list of keys that must be set for a backend to be fully configured

        The format is a dict of keys and descriptions. E.g.

        {
          "server": "The host name for the remote server",
          "username": "The current logged in username"

        }

        There are 3 keys that are always automatically populated:
           - username: the gigantum username for the logged in user
           - gigantum_bearer_token: the gigantum bearer token for the current session
           - gigantum_id_token: the gigantum id token for the current session

        Returns:

        """
        return {"Bucket": "The bucket name",
                "Prefix": "The prefix"
                }

    @staticmethod
    def _object_service_endpoint(dataset: Dataset) -> str:
        """

        Args:
            dataset:

        Returns:

        """
        default_remote = dataset.client_config.config['git']['default_remote']
        obj_service = None
        for remote in dataset.client_config.config['git']['remotes']:
            if default_remote == remote:
                obj_service = dataset.client_config.config['git']['remotes'][remote]['object_service']
                break

        if not obj_service:
            raise ValueError('Object Service endpoint not configured.')

        return f"https://{obj_service}"

    def _object_service_headers(self) -> dict:
        """Method to generate the request headers, including authorization information

        Returns:

        """
        return {'Authorization': f"Bearer {self.configuration.get('gigantum_bearer_token')}",
                'Identity': self.configuration.get("gigantum_id_token"),
                'Content-Type': 'application/json',
                'Accept': 'application/json'}

    def prepare_push(self, dataset, objects: List[PushObject], status_update_fn: Callable) -> None:
        """Gigantum Object Service only requires that the user's tokens have been set

        Args:
            dataset: The current dataset instance
            objects: A list of PushObjects to be pushed
            status_update_fn: A function to update status during pushing

        Returns:
            None
        """
        if 'username' not in self.configuration.keys():
            raise ValueError("Username must be set to push objects to Gigantum Cloud")

        if 'gigantum_bearer_token' not in self.configuration.keys():
            raise ValueError("User must have valid session to push objects to Gigantum Cloud")

        if 'gigantum_id_token' not in self.configuration.keys():
            raise ValueError("User must have valid session to push objects to Gigantum Cloud")

        status_update_fn(f"Ready to push objects to {dataset.namespace}/{dataset.name}")

    def finalize_push(self, dataset, status_update_fn: Callable) -> None:
        status_update_fn(f"Done pushing objects to {dataset.namespace}/{dataset.name}")

    def prepare_pull(self, dataset, objects: List[PullObject], status_update_fn: Callable) -> None:
        """Gigantum Object Service only requires that the user's tokens have been set

        Args:
            dataset: The current dataset instance
            objects: A list of PushObjects to be pulled
            status_update_fn: A function to update status during pushing

        Returns:
            None
        """
        if 'username' not in self.configuration.keys():
            raise ValueError("Username must be set to push objects to Gigantum Cloud")

        if 'gigantum_bearer_token' not in self.configuration.keys():
            raise ValueError("User must have valid session to push objects to Gigantum Cloud")

        if 'gigantum_id_token' not in self.configuration.keys():
            raise ValueError("User must have valid session to push objects to Gigantum Cloud")

        status_update_fn(f"Ready to pull objects from {dataset.namespace}/{dataset.name}")

    def finalize_pull(self, dataset, status_update_fn: Callable) -> None:
        status_update_fn(f"Done pulling objects from {dataset.namespace}/{dataset.name}")

    async def _push_object_consumer(self, queue: asyncio.LifoQueue, session: aiohttp.ClientSession,
                                    status_update_fn: Callable) -> None:
        """Async Queue consumer worker for pushing objects to the object service/s3

        Args:
            queue: The current work queue
            session: The current aiohttp session
            status_update_fn: the update function for providing feedback

        Returns:
            None
        """
        while True:
            presigned_request: PresignedS3Upload = await queue.get()

            try:
                if presigned_request.skip_object is False:
                    if not presigned_request.is_presigned:
                        # Fetch the signed URL
                        status_update_fn(f'Preparing upload for {presigned_request.object_details.dataset_path}')
                        await presigned_request.get_presigned_s3_url(session)
                        queue.put_nowait(presigned_request)
                    else:
                        # Process S3 Upload
                        status_update_fn(f'Uploading {presigned_request.object_details.dataset_path}')
                        await presigned_request.put_object(session)
                        self.successful_requests.append(presigned_request)
                else:
                    # Object skipped because it already exists in the backend (de-duplicating)
                    status_update_fn(f'{presigned_request.object_details.dataset_path} already exists.'
                                     f' Skipping upload to avoid duplicated storage.')
                    self.successful_requests.append(presigned_request)

            except Exception as err:
                logger.exception(err)
                self.failed_requests.append(presigned_request)

            # Notify the queue that the item has been processed
            queue.task_done()

    @staticmethod
    async def _push_object_producer(queue: asyncio.LifoQueue, object_service_root: str, object_service_headers: dict,
                                    upload_chunk_size: int, objects: List[PushObject]) -> None:
        """Async method to populate the queue with upload requests

        Args:
            queue: The current work queue
            object_service_root: The root URL to use for all objects, including the namespace and dataset name
            object_service_headers: The headers to use when requesting signed urls, including auth info
            upload_chunk_size: Size in bytes for streaming IO chunks
            objects: A list of PushObjects to push

        Returns:
            None
        """
        for obj in objects:
            presigned_request = PresignedS3Upload(object_service_root,
                                                  object_service_headers,
                                                  upload_chunk_size,
                                                  obj)
            await queue.put(presigned_request)

    async def _run_push_pipeline(self, object_service_root: str, object_service_headers: dict,
                                 objects: List[PushObject], status_update_fn: Callable,
                                 upload_chunk_size: int = 4194304, num_workers: int = 4):
        """Method to run the async upload pipeline

        Args:
            object_service_root: The root URL to use for all objects, including the namespace and dataset name
            object_service_headers: The headers to use when requesting signed urls, including auth info
            objects: A list of PushObjects to push
            status_update_fn: the update function for providing feedback
            upload_chunk_size: Size in bytes for streaming IO chunks
            num_workers: the number of consumer workers to start

        Returns:

        """
        # We use a LifoQueue to ensure S3 uploads start as soon as they are ready to help ensure pre-signed urls do
        # not timeout before they can be used if there are a lot of files.
        queue: asyncio.LifoQueue = asyncio.LifoQueue()

        async with aiohttp.ClientSession() as session:
            # Start workers
            workers = []
            for i in range(num_workers):
                task = asyncio.ensure_future(self._push_object_consumer(queue, session, status_update_fn))
                workers.append(task)

            # Populate the work queue
            await self._push_object_producer(queue,
                                             object_service_root,
                                             object_service_headers,
                                             upload_chunk_size,
                                             objects)

            # wait until the consumer has processed all items
            await queue.join()

            # the workers are still awaiting for work so close them
            for worker in workers:
                worker.cancel()

    def push_objects(self, dataset: Dataset, objects: List[PushObject], status_update_fn: Callable) -> PushResult:
        """High-level method to push objects to the object service/s3

        Args:
            dataset: The current dataset
            objects: A list of PushObjects the enumerate objects to push
            status_update_fn: A callback to update status and provide feedback to the user

        Returns:
            PushResult
        """
        # Clear lists
        self.successful_requests = list()
        self.failed_requests = list()
        message = "Successfully synced all objects"
        status_update_fn(f"Uploading {len(objects)} objects to Gigantum Cloud")

        backend_config = dataset.client_config.config['datasets']['backends']['gigantum_object_v1']
        upload_chunk_size = backend_config['upload_chunk_size']
        num_workers = backend_config['num_workers']

        object_service_root = f"{self._object_service_endpoint(dataset)}/{dataset.namespace}/{dataset.name}"

        loop = get_event_loop()
        loop.run_until_complete(self._run_push_pipeline(object_service_root, self._object_service_headers(), objects,
                                                        status_update_fn=status_update_fn,
                                                        upload_chunk_size=upload_chunk_size,
                                                        num_workers=num_workers))

        successes = [x.object_details for x in self.successful_requests]

        failures = list()
        for f in self.failed_requests:
            # An exception was raised during task processing
            logger.error(f"Failed to push {f.object_details.dataset_path}:{f.object_details.object_path}")
            status_update_fn(f"Failed to upload object {f.object_details.dataset_path}.")
            message = "Some objects failed to upload and will be retried on the next sync operation. Check results."
            failures.append(f.object_details)

        return PushResult(success=successes, failure=failures, message=message)

    async def _pull_object_consumer(self, queue: asyncio.LifoQueue, session: aiohttp.ClientSession,
                                    status_update_fn: Callable) -> None:
        """Async Queue consumer worker for downloading objects from the object service/s3

        Args:
            queue: The current work queue
            session: The current aiohttp session
            status_update_fn: the update function for providing feedback

        Returns:
            None
        """
        while True:
            presigned_request: PresignedS3Download = await queue.get()

            try:
                if not presigned_request.is_presigned:
                    # Fetch the signed URL
                    status_update_fn(f'Preparing download for {presigned_request.object_details.dataset_path}')
                    await presigned_request.get_presigned_s3_url(session)
                    queue.put_nowait(presigned_request)
                else:
                    # Process S3 Download
                    status_update_fn(f'Downloading {presigned_request.object_details.dataset_path}')
                    await presigned_request.get_object(session)
                    self.successful_requests.append(presigned_request)

            except Exception as err:
                logger.exception(err)
                self.failed_requests.append(presigned_request)

            # Notify the queue that the item has been processed
            queue.task_done()

    @staticmethod
    async def _pull_object_producer(queue: asyncio.LifoQueue, object_service_root: str, object_service_headers: dict,
                                    download_chunk_size: int, objects: List[PullObject]) -> None:
        """Async method to populate the queue with download requests

        Args:
            queue: The current work queue
            object_service_root: The root URL to use for all objects, including the namespace and dataset name
            object_service_headers: The headers to use when requesting signed urls, including auth info
            download_chunk_size: Size in bytes for streaming IO chunks
            objects: A list of PullObjects to push

        Returns:
            None
        """
        for obj in objects:
            # Create object destination dir if needed
            obj_dir, _ = obj.object_path.rsplit('/', 1)
            os.makedirs(obj_dir, exist_ok=True)  # type: ignore

            # Populate queue with item for object
            presigned_request = PresignedS3Download(object_service_root,
                                                    object_service_headers,
                                                    download_chunk_size,
                                                    obj)
            await queue.put(presigned_request)

    async def _run_pull_pipeline(self, object_service_root: str, object_service_headers: dict,
                                 objects: List[PullObject], status_update_fn: Callable,
                                 download_chunk_size: int = 4194304, num_workers: int = 4):
        """Method to run the async download pipeline

        Args:
            object_service_root: The root URL to use for all objects, including the namespace and dataset name
            object_service_headers: The headers to use when requesting signed urls, including auth info
            objects: A list of PushObjects to push
            status_update_fn: the update function for providing feedback
            download_chunk_size: Size in bytes for streaming IO chunks
            num_workers: the number of consumer workers to start

        Returns:

        """
        # We use a LifoQueue to ensure S3 uploads start as soon as they are ready to help ensure pre-signed urls do
        # not timeout before they can be used if there are a lot of files.
        queue: asyncio.LifoQueue = asyncio.LifoQueue()

        async with aiohttp.ClientSession() as session:
            workers = []
            for i in range(num_workers):
                task = asyncio.ensure_future(self._pull_object_consumer(queue, session, status_update_fn))
                workers.append(task)

            # Populate the work queue
            await self._pull_object_producer(queue,
                                             object_service_root,
                                             object_service_headers,
                                             download_chunk_size,
                                             objects)

            # wait until the consumer has processed all items
            await queue.join()

            # the workers are still awaiting for work so close them
            for worker in workers:
                worker.cancel()

    def pull_objects(self, dataset: Dataset, objects: List[PullObject], status_update_fn: Callable) -> PullResult:
        """High-level method to pull objects from the object service/s3

        Args:
            dataset: The current dataset
            objects: A list of PullObjects the enumerate objects to push
            status_update_fn: A callback to update status and provide feedback to the user

        Returns:
            PushResult
        """
        # Clear lists
        self.successful_requests = list()
        self.failed_requests = list()
        message = "Successfully synced all objects"
        status_update_fn(f"Downloading {len(objects)} objects from Gigantum Cloud")

        backend_config = dataset.client_config.config['datasets']['backends']['gigantum_object_v1']
        download_chunk_size = backend_config['download_chunk_size']
        num_workers = backend_config['num_workers']

        object_service_root = f"{self._object_service_endpoint(dataset)}/{dataset.namespace}/{dataset.name}"

        loop = get_event_loop()
        loop.run_until_complete(self._run_pull_pipeline(object_service_root, self._object_service_headers(), objects,
                                                        status_update_fn=status_update_fn,
                                                        download_chunk_size=download_chunk_size,
                                                        num_workers=num_workers))

        successes = [x.object_details for x in self.successful_requests]

        failures = list()
        for f in self.failed_requests:
            # An exception was raised during task processing
            logger.error(f"Failed to pull {f.object_details.dataset_path}:{f.object_details.object_path}")
            status_update_fn(f"Failed to download object {f.object_details.dataset_path}.")
            message = "Some objects failed to download and will be retried on the next sync operation. Check results."
            failures.append(f.object_details)

        return PullResult(success=successes, failure=failures, message=message)

    def delete_contents(self, dataset) -> None:
        """Method to remove the contents of a dataset from the storage backend, should only work if managed

        Args:
            dataset: Dataset object

        Returns:
            None
        """
        url = f"{self._object_service_endpoint(dataset)}/{dataset.namespace}/{dataset.name}"
        response = requests.delete(url, headers=self._object_service_headers(), timeout=10)

        if response.status_code != 200:
            logger.error(f"Failed to remove {dataset.namespace}/{dataset.name} from cloud index. "
                         f"Status Code: {response.status_code}")
            logger.error(response.json())
            raise IOError("Failed to invoke dataset delete in the dataset backend service.")
        else:
            logger.info(f"Deleted remote repository {dataset.namespace}/{dataset.name} from cloud index")
