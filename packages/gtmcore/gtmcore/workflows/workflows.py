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
import time
import os

from tempfile import TemporaryDirectory
from typing import Optional, Callable

from gtmcore.configuration.utils import call_subprocess
from gtmcore.inventory.inventory import InventoryManager
from gtmcore.labbook import LabBook
from gtmcore.logging import LMLogger
from gtmcore.workflows import core

logger = LMLogger.get_logger()


class GitWorkflow(object):

    def __init__(self, labbook: LabBook) -> None:
        self.labbook = labbook

    def garbagecollect(self):
        """ Run a `git gc` on the labbook. """
        core.git_garbage_collect(self.labbook)

    def publish(self, username: str, access_token: Optional[str] = None, remote: str = "origin",
                public: bool = False, feedback_callback: Callable = lambda _ : None) -> None:
        """ Publish this labbook to the remote GitLab instance.

        Args:
            username: Subject username
            access_token: Temp token/password to gain permissions on GitLab instance
            remote: Name of Git remote (always "origin" for now).
            public: Allow public read access
            feedback_callback: Callback to give user-facing realtime feedback

        Returns:
            None
        """

        logger.info(f"Publishing {str(self.labbook)} for user {username} to remote {remote}")
        if self.labbook.has_remote:
            raise ValueError("Cannot publish Labbook when remote already set.")

        if self.labbook.active_branch != f'gm.workspace-{username}':
            raise ValueError(f"Must be on user workspace (gm.workspace-{username}) to sync")

        try:
            self.labbook.sweep_uncommitted_changes()
            vis = "public" if public is True else "private"
            t0 = time.time()
            core.create_remote_gitlab_repo(labbook=self.labbook, username=username,
                                           access_token=access_token, visibility=vis)
            logger.info(f"Created remote repo for {str(self.labbook)} in {time.time()-t0:.1f}sec")
            t0 = time.time()
            core.publish_to_remote(labbook=self.labbook, username=username,
                                   remote=remote, feedback_callback=feedback_callback)
            logger.info(f"Published {str(self.labbook)} in {time.time()-t0:.1f}sec")
        except Exception as e:
            # Unsure what specific exception add_remote creates, so make a catchall.
            logger.error(f"Publish failed {e}: {str(self.labbook)} may be in corrupted Git state!")
            call_subprocess(['git', 'reset', '--hard'], cwd=self.labbook.root_dir)
            self.labbook.checkout_branch(f"gm.workspace-{username}")
            raise e

    def sync(self, username: str, remote: str = "origin", force: bool = False,
             feedback_callback: Callable = lambda _ : None) -> int:
        """ Sync with remote GitLab repo (i.e., pull any upstream changes and push any new changes). Following
        a sync operation both the local repo and remote should be at the same revision.

        Args:
            username: Subject user
            remote: Name of remote (usually only origin for now)
            force: In the event of conflict, force overwrite local changes
            feedback_callback: Used to give periodic feedback

        Returns:
            Integer number of commits pulled down from remote.
        """
        return core.sync_with_remote(labbook=self.labbook, username=username, remote=remote,
                                     force=force, feedback_callback=feedback_callback)

    def _add_remote(self, remote_name: str, url: str):
        self.labbook.add_remote(remote_name=remote_name, url=url)


class ZipWorkflowException(Exception):
    pass


class ZipExporter(object):

    @classmethod
    def _export_zip(cls, labbook_path: str, lb_export_directory: str,
                    config_file: Optional[str] = None,) -> str:
        if not os.path.isdir(lb_export_directory):
            os.makedirs(lb_export_directory, exist_ok=True)

        labbook = InventoryManager(config_file).load_labbook_from_directory(labbook_path)
        core.sync_locally(labbook)

        labbook_dir, _ = labbook.root_dir.rsplit(os.path.sep, 1)

        lb_zip_name = f'{labbook.name}-' \
                      f'{labbook.git.log()[0]["commit"][:6]}'
        zip_path = f'{lb_zip_name}.zip'
        exported_path = os.path.join(lb_export_directory, zip_path)

        try:
            # zip data using subprocess - NOTE! Python zipfile library does not work correctly.
            call_subprocess(['zip', '-r', exported_path, os.path.basename(labbook.root_dir)],
                            cwd=labbook_dir, check=True)
            assert os.path.exists(exported_path)
            return exported_path
        except:
            try:
                os.remove(exported_path)
            except:
                pass
            raise


    @classmethod
    def export_zip(cls, labbook_path: str, lb_export_directory: str) -> str:
        try:
            return cls._export_zip(labbook_path, lb_export_directory)
        except Exception as e:
            logger.error(e)
            raise ZipWorkflowException(e)

    @classmethod
    def _import_zip(cls, archive_path: str, username: str, owner: str,
                    config_file: Optional[str] = None,
                    update_meta: Callable = lambda _ : None) -> LabBook:

        if not os.path.isfile(archive_path):
            raise ValueError(f'Archive at {archive_path} is not a file or does not exist')

        if '.zip' not in archive_path and '.lbk' not in archive_path:
            raise ValueError(f'Archive at {archive_path} does not have .zip (or legacy .lbk) extension')

        statusmsg = f'Unzipping Project Archive...'
        update_meta(statusmsg)

        # Unzip into a temporary directory and cleanup if fails
        with TemporaryDirectory() as tdir:
            call_subprocess(['unzip', archive_path, '-d', 'project'],
                            cwd=tdir, check=True)

            pdirs = os.listdir(os.path.join(tdir, 'project'))
            if len(pdirs) != 1:
                raise ValueError("Expected only one directory unzipped")
            unzipped_path = os.path.join(tdir, 'project', pdirs[0])

            lb = InventoryManager(config_file).load_labbook_from_directory(unzipped_path)
            statusmsg = f'{statusmsg}\nCreating workspace branch...'
            update_meta(statusmsg)

            # This makes sure the working directory is set properly.
            core.sync_locally(lb, username=username)

            lb._data['owner']['username'] = owner
            lb._save_gigantum_data()
            if not lb.is_repo_clean:
                lb.git.add('.gigantum/labbook.yaml')
                lb.git.commit(message="Updated owner in labbook.yaml")

            if lb._data['owner']['username'] != owner:
                raise ValueError(f'Error importing LabBook {lb} - cannot set owner')

            # Also, remove any lingering remotes.
            # If it gets re-published, it will be to a new remote.
            if lb.has_remote:
                lb.git.remove_remote('origin')

            # Ignore execution bit changes (due to moving between windows/mac/linux)
            call_subprocess("git config core.fileMode false".split(),
                            cwd=lb.root_dir)

            im = InventoryManager(config_file)
            lb = im.put_labbook(unzipped_path, username=username, owner=owner)

            statusmsg = f'{statusmsg}\nImport Complete'
            update_meta(statusmsg)

            return lb

    @classmethod
    def import_zip(cls, archive_path: str, username: str, owner: str,
                   config_file: Optional[str] = None,
                   update_meta: Callable = lambda _ : None) -> LabBook:
        try:
            return cls._import_zip(archive_path, username, owner, config_file,
                                   update_meta)
        except Exception as e:
            logger.error(e)
            raise ZipWorkflowException(e)
        finally:
            if os.path.isfile(archive_path):
                os.remove(archive_path)
