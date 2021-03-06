from typing import (Any, Dict, List)

from gtmcore.activity.processors.processor import ActivityProcessor, ExecutionData
from gtmcore.activity import ActivityRecord, ActivityDetailRecord, ActivityAction, ActivityDetailType
from gtmcore.labbook import LabBook


class ActivityShowBasicProcessor(ActivityProcessor):
    """Class to simply hide an activity record if it doesn't have any detail records that are set to show=True"""

    def process(self, result_obj: ActivityRecord, data: List[ExecutionData],
                status: Dict[str, Any], metadata: Dict[str, Any]) -> ActivityRecord:
        """Method to update a result object based on code and result data

        Args:
            result_obj(ActivityNote): An object containing the note
            data(list): A list of ExecutionData instances containing the data for this record
            status(dict): A dict containing the result of git status from gitlib
            metadata(str): A dictionary containing Dev Env specific or other developer defined data

        Returns:
            ActivityNote
        """
        result_obj.show = False
        with result_obj.inspect_detail_objects() as details:
            for detail in details:
                if detail.show:
                    result_obj.show = True
                    break

        return result_obj


class GenericFileChangeProcessor(ActivityProcessor):
    """Class to process file changes based on git-status into activity detail records"""

    def process(self, result_obj: ActivityRecord, data: List[ExecutionData],
                status: Dict[str, Any], metadata: Dict[str, Any]) -> ActivityRecord:
        """Method to update a result object based on code and result data

        Args:
            result_obj(ActivityNote): An object containing the note
            data(list): A list of ExecutionData instances containing the data for this record
            status(dict): A dict containing the result of git status from gitlib
            metadata(str): A dictionary containing Dev Env specific or other developer defined data

        Returns:
            ActivityRecord
        """
        for cnt, filename in enumerate(status['untracked']):
            # skip any file in .git or .gigantum dirs
            if ".git" in filename or ".gigantum" in filename:
                continue

            activity_type, activity_detail_type, section = LabBook.infer_section_from_relative_path(filename)

            adr = ActivityDetailRecord(activity_detail_type, show=False, importance=max(255-cnt, 0),
                                       action=ActivityAction.CREATE)
            # We use a "private" attribute here, but it's better than the silent breakage that happened before
            # cf. https://github.com/gigantum/gigantum-client/issues/436
            if section == LabBook._default_activity_section:
                msg = f'Created new file `{filename}` in the Project Root. Note, it is best practice to use the Code, ' \
                    'Input, and Output sections exclusively. '
            else:
                msg = f"Created new {section} file `{filename}`"
            adr.add_value('text/markdown', msg)
            result_obj.add_detail_object(adr)

        cnt = 0
        for filename, change in status['unstaged']:
            # skip any file in .git or .gigantum dirs
            if ".git" in filename or ".gigantum" in filename:
                continue

            activity_type, activity_detail_type, section = LabBook.infer_section_from_relative_path(filename)

            if change == "deleted":
                action = ActivityAction.DELETE
            elif change == "added":
                action = ActivityAction.CREATE
            elif change == "modified":
                action = ActivityAction.EDIT
            elif change == "renamed":
                action = ActivityAction.EDIT
            else:
                action = ActivityAction.NOACTION

            adr = ActivityDetailRecord(activity_detail_type, show=False, importance=max(255-cnt, 0), action=action)
            adr.add_value('text/markdown', f"{change[0].upper() + change[1:]} {section} file `{filename}`")
            result_obj.add_detail_object(adr)
            cnt += 1

        return result_obj


class ActivityDetailLimitProcessor(ActivityProcessor):
    """Class to limit the number of captured detail records to 255 records + a truncation notification

    Since the "importance" value used to order detail records is 1 byte and a max value of 255, we'll truncate to
    255 records and insert a record indicating the truncation occurred
    """

    def process(self, result_obj: ActivityRecord, data: List[ExecutionData],
                status: Dict[str, Any], metadata: Dict[str, Any]) -> ActivityRecord:
        """Method to update a result object based on code and result data

        Args:
            result_obj(ActivityNote): An object containing the note
            data(list): A list of ExecutionData instances containing the data for this record
            status(dict): A dict containing the result of git status from gitlib
            metadata(str): A dictionary containing Dev Env specific or other developer defined data

        Returns:
            ActivityNote
        """
        with result_obj.inspect_detail_objects() as detail_objs:
            orig_num = result_obj.num_detail_objects
            if result_obj.num_detail_objects > 255:
                result_obj.trim_detail_objects(255)

                adr = ActivityDetailRecord(ActivityDetailType.NOTE, show=True, importance=0,
                                           action=ActivityAction.NOACTION)
                adr.add_value('text/markdown', f"This activity produced {orig_num} detail records, "
                                               f"but was truncated to the top 255 items. Inspect your code to make "
                                               f"sure that this was not accidental. In Jupyter for example, you can"
                                               f" use a `;` at the end of a line to suppress output from functions"
                                               f" that print excessively.")
                result_obj.add_detail_object(adr)

        return result_obj
