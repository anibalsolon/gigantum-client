from typing import Callable, List, Dict
import pickle
import os
from enum import Enum
import shutil
import asyncio
from collections import OrderedDict, namedtuple

from gtmcore.activity import ActivityStore, ActivityRecord, ActivityDetailType, ActivityType,\
    ActivityAction, ActivityDetailRecord
from gtmcore.dataset.dataset import Dataset
from gtmcore.dataset.manifest.hash import SmartHash


class FileChangeType(Enum):
    """Enumeration representing types of file changes"""
    NOCHANGE = 0
    CREATED = 1
    MODIFIED = 2
    DELETED = 3


StatusResult = namedtuple('StatusResult', ['created', 'modified', 'deleted'])


class Manifest(object):
    """Class to handle file file manifest"""

    def __init__(self, dataset: Dataset, file_cache_dir: str) -> None:
        self.dataset = dataset
        self.file_cache_dir = file_cache_dir

        self.ignore_file = os.path.join(dataset.root_dir, ".gigantumignore")

        self.smarthasher = SmartHash(dataset.root_dir, file_cache_dir,
                                     self.dataset.git.repo.head.commit.hexsha)

        self.manifest = self._load_manifest()
        # self.ignored = self._load_ignored()

        self._dataset_revision = None

    @property
    def dataset_revision(self) -> str:
        """Property to get the current revision hash of the dataset

        Returns:
            str
        """
        return self.dataset.git.repo.head.commit.hexsha

    def _load_manifest(self) -> OrderedDict:
        """Method to load the manifest file

        Returns:
            dict
        """
        manifest_file = os.path.join(self.dataset.root_dir, 'manifest', 'manifest0')
        if os.path.exists(manifest_file):
            with open(manifest_file, 'rb') as mf:
                return pickle.load(mf)
        else:
            return OrderedDict()

    def _save_manifest(self) -> None:
        """Method to load the manifest file

        Returns:
            dict
        """
        with open(os.path.join(self.dataset.root_dir, 'manifest', 'manifest0'), 'wb') as mf:
            pickle.dump(self.manifest, mf, pickle.HIGHEST_PROTOCOL)

    def _queue_to_push(self, obj) -> None:
        """

        Args:
            obj:

        Returns:

        """
        if not os.path.exists(obj):
            raise ValueError("Object does not exist. Failed to add to push queue.")

        with open(os.path.join(self.file_cache_dir, 'objects', '.push'), 'at') as fh:
            fh.write(obj)

    def get_change_type(self, path) -> FileChangeType:
        """

        Args:
            path:

        Returns:

        """
        if self.smarthasher.is_cached(path):
            if self.smarthasher.has_changed_fast(path):
                result = FileChangeType.MODIFIED
            else:
                result = FileChangeType.NOCHANGE
        else:
            if path in self.manifest.keys():
                # No fast hash, but exists in manifest. User just edited a file that hasn't been pulled
                result = FileChangeType.MODIFIED
            else:
                # No fast hash, not in manifest.
                result = FileChangeType.CREATED
        return result

    def status(self) -> StatusResult:
        """

        Returns:

        """
        # TODO: think about how to send batches to get_change_type
        status: Dict[str, List] = {"created": [], "modified": [], "deleted": []}
        all_files = list()
        revision_directory = os.path.join(self.file_cache_dir, self.dataset_revision)

        for root, dirs, files in os.walk(revision_directory):
            _, folder = root.split(revision_directory)
            if len(folder) > 0:
                if folder[0] == os.path.sep:
                    folder = folder[1:]

            for file in files:
                if file in ['.smarthash', '.DS_STORE']:
                    continue
                # TODO: Check for ignored

                rel_path = os.path.join(folder, file)
                all_files.append(rel_path)
                change = self.get_change_type(rel_path)
                if change == FileChangeType.NOCHANGE:
                    continue
                elif change == FileChangeType.MODIFIED:
                    status['modified'].append(rel_path)
                elif change == FileChangeType.CREATED:
                    status['created'].append(rel_path)
                else:
                    raise ValueError(f"Invalid Change type: {change}")

        return StatusResult(created=status.get('created'), modified=status.get('modified'),
                            deleted=self.smarthasher.get_deleted_files(all_files))

    async def _async_move(self, source, destination):
        shutil.move(source, destination)

    async def _move_to_object_cache(self, relative_path, hash_str):
        """

        Args:
            relative_path:
            hash_str:

        Returns:

        """
        source = os.path.join(self.file_cache_dir, self.dataset_revision, relative_path)
        level1 = hash_str[0:8]
        level2 = hash_str[8:16]

        os.makedirs(os.path.join(self.file_cache_dir, 'objects', level1), exist_ok=True)
        os.makedirs(os.path.join(self.file_cache_dir, 'objects', level1, level2), exist_ok=True)

        destination = os.path.join(self.file_cache_dir, 'objects', level1, level2, hash_str)
        if os.path.isfile(destination):
            # Object already exists, no need to store again
            os.remove(source)
        else:
            # Move file to new object
            await self._async_move(source, destination)

        # Link object back
        os.link(destination, source)

        # Queue new object for push
        self._queue_to_push(destination)

        return destination

    def update(self, storage_metadata_generator: Callable, status: StatusResult=None) -> StatusResult:
        """

        Args:
            storage_metadata_generator:
            status:

        Returns:

        """
        if not status:
            status = self.status()

        update_files = status.created
        update_files.extend(status.modified)

        if update_files:
            # Hash Files
            hash_result = self.smarthasher.hash(update_files)

            # Move files into object cache and link back to the revision directory
            tasks = [asyncio.ensure_future(self._move_to_object_cache(fd.filename, fd.hash)) for fd in hash_result]
            loop = asyncio.get_event_loop()
            loop.run_until_complete(asyncio.ensure_future(asyncio.wait(tasks)))

            # Update fast hash
            self.smarthasher.fast_hash(update_files)

            # Update manifest file
            for result in hash_result:
                _, file_bytes, mtime, ctime = result.fast_hash.split("||")
                self.manifest[result.filename] = {'h': result.hash,
                                                  'c': ctime,
                                                  'm': mtime,
                                                  'b': file_bytes,
                                                  's': storage_metadata_generator(self.dataset, result.filename)}

        if status.deleted:
            self.smarthasher.delete_hashes(status.deleted)
            for f in status.deleted:
                del self.manifest[f]

        self._save_manifest()

        return status

    def get(self, path: str) -> dict:
        pass

    def list(self, first: int=None, after: str=None) -> List[dict]:
        result = list()
        for f in self.manifest:
            item = self.manifest[f]
            result.append({'key': f,
                           'size': item.get('b'),
                           'is_favorite': False,
                           'is_dir': os.path.isdir(os.path.join(self.file_cache_dir, self.dataset_revision, f)),
                           'modified_at': item.get('m')})

        return result

    def delete(self, path_list: List[str]) -> None:
        pass

    def link_revision(self) -> None:
        revision_directory = os.path.join(self.file_cache_dir, self.dataset_revision)

        if not os.path.exists(revision_directory):
            os.makedirs(revision_directory)

        for f in self.manifest:
            level1 = self.manifest[f].get('h')[0:8]
            level2 = self.manifest[f].get('h')[8:16]

            target = os.path.join(revision_directory, f)
            source = os.path.join(self.file_cache_dir, 'objects', level1, level2, self.manifest[f].get('h'))

            target_dir = os.path.dirname(target)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

            os.link(source, target)

        # Update fast hash
        self.smarthasher.fast_hash(list(self.manifest.keys()))

    def sweep_all_changes(self, storage_metadata_generator: Callable, upload: bool=False, extra_msg: str=None) -> None:
        """

        Args:
            storage_metadata_generator:
            upload:
            extra_msg:

        Returns:

        """
        # Update manifest
        status = self.update(storage_metadata_generator)

        # commit changed manifest file
        self.dataset.git.add_all()
        self.dataset.git.commit("Commit changes to manifest file.")

        ar = ActivityRecord(ActivityType.DATASET,
                            message="--overwritten--",
                            show=True,
                            importance=255,
                            linked_commit=self.dataset.git.commit_hash,
                            tags=['save'])
        if upload:
            ar.tags.append('upload')

        for cnt, f in enumerate(status.created):
            adr = ActivityDetailRecord(ActivityDetailType.DATASET, show=False, importance=max(255 - cnt, 0),
                                       action=ActivityAction.CREATE)

            msg = f"Created new file `{f}`"
            adr.add_value('text/markdown', msg)
            ar.add_detail_object(adr)

        for cnt, f in enumerate(status.modified):
            adr = ActivityDetailRecord(ActivityDetailType.DATASET, show=False, importance=max(255 - cnt, 0),
                                       action=ActivityAction.EDIT)

            msg = f"Modified file `{f}`"
            adr.add_value('text/markdown', msg)
            ar.add_detail_object(adr)

        for cnt, f in enumerate(status.deleted):
            adr = ActivityDetailRecord(ActivityDetailType.DATASET, show=False, importance=max(255 - cnt, 0),
                                       action=ActivityAction.DELETE)

            msg = f"Deleted file `{f}`"
            adr.add_value('text/markdown', msg)
            ar.add_detail_object(adr)

        nmsg = f"{len(status.created)} new file(s). " if len(status.created) > 0 else ""
        mmsg = f"{len(status.modified)} modified file(s). " if len(status.modified) > 0 else ""
        dmsg = f"{len(status.deleted)} deleted file(s). " if len(status.deleted) > 0 else ""

        ar.message = f"{extra_msg if extra_msg else ''}" \
                     f"{'Uploaded ' if upload else ''}" \
                     f"{nmsg}{mmsg}{dmsg}"

        ars = ActivityStore(self.dataset)
        ars.create_activity_record(ar)

        # Re-link new revision
        self.smarthasher.current_revision = self.dataset_revision
        self.link_revision()

