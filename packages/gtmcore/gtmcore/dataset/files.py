import shutil
import os
from typing import Any, Dict, List, Optional

from gtmcore.dataset import Dataset
from gtmcore.dataset.manifest import Manifest
from gtmcore.dataset.cache import get_cache_manager_class
from gtmcore.logging import LMLogger
from gtmcore.activity import (ActivityDetailRecord, ActivityRecord,
                               ActivityStore, ActivityAction)


logger = LMLogger.get_logger()


def _make_path_relative(path_str: str) -> str:
    while len(path_str or '') >= 1 and path_str[0] == os.path.sep:
        path_str = path_str[1:]
    return path_str


class DatasetFileOperations(object):

    @classmethod
    def put_file(cls, dataset: Dataset, src_file: str, dst_path: str, username: str,
                 txid: Optional[str] = None) -> Dict[str, Any]:
        """Move the file at `src_file` to `dst_dir`. Filename removes
        upload ID if present. This operation does NOT commit or create an
        activity record.

        Args:
            dataset: Subject Dataset
            src_file: Full path of file to insert into
            dst_path: Path within section to insert `src_file`
            username: username for currently logged in user
            txid: Optional transaction id

        Returns:
           Full path to inserted file.
        """
        if not os.path.abspath(src_file):
            raise ValueError(f"Source file `{src_file}` not an absolute path")

        if not os.path.isfile(src_file):
            raise ValueError(f"Source file does not exist at `{src_file}`")

        fsc_class = get_cache_manager_class(dataset.client_config)
        fsc = fsc_class(dataset, username)

        mdst_dir = _make_path_relative(dst_path)
        full_dst = os.path.join(fsc.current_revision_dir, mdst_dir)

        # Force overwrite if file already exists
        if os.path.isfile(os.path.join(full_dst, os.path.basename(src_file))):
            os.remove(os.path.join(full_dst, os.path.basename(src_file)))

        if not os.path.isdir(os.path.dirname(full_dst)):
            os.makedirs(os.path.dirname(full_dst), exist_ok=True)

        fdst = shutil.move(src_file, full_dst)
        relpath = fdst.replace(fsc.current_revision_dir, '')
        return cls.get_file_info(dataset, relpath, username)

    @classmethod
    def complete_batch(cls, dataset: Dataset, username: str, txid: str,
                       cancel: bool = False, rollback: bool = False) -> None:
        """
        Indicate a batch upload is finished and sweep all new files.

        Args:
            dataset: Subject dataset
            username: username of the currently logged in user
            txid: Transaction id (correlator)
            username: username for currently logged in user
            cancel: Indicate transaction finished but due to cancellation
            rollback: Undo all local changes if cancelled (default False)

        Returns:
            None
        """

        if cancel and rollback:
            logger.warning(f"Cancelled tx {txid}, doing git reset")
            # TODO: Add ability to reset
        else:
            logger.info(f"Done batch upload {txid}, cancelled={cancel}")
            if cancel:
                logger.warning("Sweeping aborted batch upload.")

            m = "Cancelled upload `{txid}`. " if cancel else ''

            fsc_class = get_cache_manager_class(dataset.client_config)
            fsc = fsc_class(dataset, username)

            manifest = Manifest(dataset, fsc.cache_root)
            manifest.sweep_all_changes(storage_metadata_generator=lambda x, y: "", upload=True, extra_msg=m)

    #@classmethod
    #def delete_file(cls, labbook: LabBook, section: str, relative_path: str) -> bool:
    #    """Delete file (or directory) from inside lb section.
#
#
    #    Part of the intention is to mirror the unix "rm" command. Thus, there
    #    needs to be some extra arguments in order to delete a directory, especially
    #    one with contents inside of it. In this case, `directory` must be true in order
    #    to delete a directory at the given path.
#
    #    Args:
    #        labbook: Subject LabBook
    #        section: Section name (code, input, output)
    #        relative_path: Relative path from labbook root to target
#
    #    Returns:
    #        None
    #    """
    #    labbook.validate_section(section)
    #    relative_path = LabBook.make_path_relative(relative_path)
    #    target_path = os.path.join(labbook.root_dir, section, relative_path)
    #    if not os.path.exists(target_path):
    #        raise ValueError(f"Attempted to delete non-existent path at `{target_path}`")
    #    else:
    #        target_type = 'file' if os.path.isfile(target_path) else 'directory'
    #        logger.info(f"Removing {target_type} at `{target_path}`")
#
    #        if shims.in_untracked(labbook.root_dir, section=section):
    #            logger.info(f"Removing untracked target {target_path}")
    #            if os.path.isdir(target_path):
    #                shutil.rmtree(target_path)
    #            else:
    #                os.remove(target_path)
    #            return True
#
    #        commit_msg = f"Removed {target_type} {relative_path}."
    #        labbook.git.remove(target_path, force=True, keep_file=False)
    #        assert not os.path.exists(target_path)
    #        commit = labbook.git.commit(commit_msg)
#
    #        if os.path.isfile(target_path):
    #            _, ext = os.path.splitext(target_path)
    #        else:
    #            ext = 'directory'
#
    #        # Get LabBook section
    #        activity_type, activity_detail_type, section_str = labbook.get_activity_type_from_section(section)
#
    #        # Create detail record
    #        adr = ActivityDetailRecord(activity_detail_type, show=False, importance=0,
    #                                   action=ActivityAction.DELETE)
    #        adr.add_value('text/plain', commit_msg)
#
    #        # Create activity record
    #        ar = ActivityRecord(activity_type,
    #                            message=commit_msg,
    #                            linked_commit=commit.hexsha,
    #                            show=True,
    #                            importance=255,
    #                            tags=[ext])
    #        ar.add_detail_object(adr)
#
    #        # Store
    #        ars = ActivityStore(labbook)
    #        ars.create_activity_record(ar)
#
    #        if not os.path.exists(target_path):
    #            return True
    #        else:
    #            logger.error(f"{target_path} should have been deleted, but remains.")
    #            return False

    #@classmethod
    #def move_file(cls, labbook: LabBook, section: str, src_rel_path: str, dst_rel_path: str) -> Dict[str, Any]:
#
    #    """Move a file or directory within a labbook, but not outside of it. Wraps
    #    underlying "mv" call.
#
    #    Args:
    #        labbook: Subject LabBook
    #        section(str): Section name (code, input, output)
    #        src_rel_path(str): Source file or directory
    #        dst_rel_path(str): Target file name and/or directory
    #    """
#
    #    # Start with Validations
    #    labbook.validate_section(section)
    #    if not src_rel_path:
    #        raise ValueError("src_rel_path cannot be None or empty")
#
    #    if not dst_rel_path:
    #        raise ValueError("dst_rel_path cannot be None or empty")
#
    #    is_untracked = shims.in_untracked(labbook.root_dir, section)
    #    src_rel_path = LabBook.make_path_relative(src_rel_path)
    #    dst_rel_path = LabBook.make_path_relative(dst_rel_path)
#
    #    src_abs_path = os.path.join(labbook.root_dir, section, src_rel_path.replace('..', ''))
    #    dst_abs_path = os.path.join(labbook.root_dir, section, dst_rel_path.replace('..', ''))
#
    #    if not os.path.exists(src_abs_path):
    #        raise ValueError(f"No src file exists at `{src_abs_path}`")
#
    #    try:
    #        src_type = 'directory' if os.path.isdir(src_abs_path) else 'file'
    #        logger.info(f"Moving {src_type} `{src_abs_path}` to `{dst_abs_path}`")
#
    #        if not is_untracked:
    #            labbook.git.remove(src_abs_path, keep_file=True)
#
    #        shutil.move(src_abs_path, dst_abs_path)
#
    #        if not is_untracked:
    #            commit_msg = f"Moved {src_type} `{src_rel_path}` to `{dst_rel_path}`"
#
    #            if os.path.isdir(dst_abs_path):
    #                labbook.git.add_all(dst_abs_path)
    #            else:
    #                labbook.git.add(dst_abs_path)
#
    #            commit = labbook.git.commit(commit_msg)
#
    #            # Get LabBook section
    #            activity_type, activity_detail_type, section_str = labbook.get_activity_type_from_section(section)
#
    #            # Create detail record
    #            adr = ActivityDetailRecord(activity_detail_type, show=False, importance=0,
    #                                       action=ActivityAction.EDIT)
    #            adr.add_value('text/markdown', commit_msg)
#
    #            # Create activity record
    #            ar = ActivityRecord(activity_type,
    #                                message=commit_msg,
    #                                linked_commit=commit.hexsha,
    #                                show=True,
    #                                importance=255,
    #                                tags=['file-move'])
    #            ar.add_detail_object(adr)
#
    #            # Store
    #            ars = ActivityStore(labbook)
    #            ars.create_activity_record(ar)
#
    #        return cls.get_file_info(labbook, section, dst_rel_path)
    #    except Exception as e:
    #        logger.critical("Failed moving file in labbook. Repository may be in corrupted state.")
    #        logger.exception(e)
    #        raise

    #@classmethod
    #def makedir(cls, labbook: LabBook, relative_path: str, make_parents: bool = True,
    #            create_activity_record: bool = False) -> None:
    #    """Make a new directory inside the labbook directory.
#
    #    Args:
    #        labbook: Subject LabBook
    #        relative_path(str): Path within the labbook to make directory
    #        make_parents(bool): If true, create intermediary directories
    #        create_activity_record(bool): If true, create commit and activity record
#
    #    Returns:
    #        str: Absolute path of new directory
    #    """
    #    if not relative_path:
    #        raise ValueError("relative_path argument cannot be None or empty")
#
    #    relative_path = LabBook.make_path_relative(relative_path)
    #    new_directory_path = os.path.join(labbook.root_dir, relative_path)
    #    section = relative_path.split(os.sep)[0]
    #    git_untracked = shims.in_untracked(labbook.root_dir, section)
    #    if os.path.exists(new_directory_path):
    #        return
    #    else:
    #        logger.info(f"Making new directory in `{new_directory_path}`")
    #        os.makedirs(new_directory_path, exist_ok=make_parents)
    #        if git_untracked:
    #            logger.warning(f'New {str(labbook)} untracked directory `{new_directory_path}`')
    #            return
    #        new_dir = ''
    #        for d in relative_path.split(os.sep):
    #            new_dir = os.path.join(new_dir, d)
    #            full_new_dir = os.path.join(labbook.root_dir, new_dir)
#
    #            gitkeep_path = os.path.join(full_new_dir, '.gitkeep')
    #            if not os.path.exists(gitkeep_path):
    #                with open(gitkeep_path, 'w') as gitkeep:
    #                    gitkeep.write("This file is necessary to keep this directory tracked by Git"
    #                                  " and archivable by compression tools. Do not delete or modify!")
    #                labbook.git.add(gitkeep_path)
#
    #        if create_activity_record:
    #            # Create detail record
    #            activity_type, activity_detail_type, section_str = labbook.infer_section_from_relative_path(
    #                relative_path)
    #            adr = ActivityDetailRecord(activity_detail_type, show=False, importance=0,
    #                                       action=ActivityAction.CREATE)
#
    #            msg = f"Created new {section_str} directory `{relative_path}`"
    #            commit = labbook.git.commit(msg)
    #            adr.add_value('text/markdown', msg)
#
    #            # Create activity record
    #            ar = ActivityRecord(activity_type,
    #                                message=msg,
    #                                linked_commit=commit.hexsha,
    #                                show=True,
    #                                importance=255,
    #                                tags=['directory-create'])
    #            ar.add_detail_object(adr)
#
    #            # Store
    #            ars = ActivityStore(labbook)
    #            ars.create_activity_record(ar)

    @classmethod
    def get_file_info(cls, dataset: Dataset, rel_file_path: str, username: str) -> Dict[str, Any]:
        """Method to get a file's detail information

        Args:
            dataset: Subject dataset
            rel_file_path(str): The relative file path to generate info from
            username: username for currently logged in user

        Returns:
            dict
        """
        # TODO Load from manifest
        # remove leading separators if one exists.
        rel_file_path = _make_path_relative(rel_file_path)

        fsc_class = get_cache_manager_class(dataset.client_config)
        fsc = fsc_class(dataset, username)

        full_path = os.path.join(fsc.current_revision_dir, rel_file_path)

        file_info = os.stat(full_path)
        is_dir = os.path.isdir(full_path)

        # If it's a directory, add a trailing slash so UI renders properly
        if is_dir:
            if rel_file_path[-1] != os.path.sep:
                rel_file_path = f"{rel_file_path}{os.path.sep}"

        return {
                  'key': rel_file_path,
                  'is_dir': is_dir,
                  'size': file_info.st_size if not is_dir else 0,
                  'modified_at': file_info.st_mtime,
                  'is_favorite': False  # TODO: rel_file_path in labbook.favorite_keys[section]
               }
