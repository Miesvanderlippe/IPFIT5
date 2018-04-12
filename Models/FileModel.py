from datetime import datetime


class FileModel:
    """
    Little model to make handling file information from ImageHandler easier.
    """

    def __init__(self, file_info: []):
        """
        Creates instance of FileModel using data as returned by
        ImageHandler.
        :param file_info: The file information array from FileModel
        """
        self.partition: str = file_info[0]
        self.partition_no: int = int(file_info[0][-1])
        self.file_name: str = file_info[1]
        self.extension: str = file_info[2]
        self.type: str = file_info[3]
        self.date_created: datetime = file_info[4]
        self.date_modified: datetime = file_info[5]
        self.date_changed: datetime = file_info[6]
        self.file_size: int = file_info[7]
        self.path: str = file_info[8]
        # Hash doesn't always exist
        self.hash = file_info[9] if len(file_info) >= 10 else None

    @property
    def is_file(self) -> bool:
        """
        Whether instance is representing a file
        :return: Whether instance is representing a file
        """
        return self.type == "FILE"

    @property
    def is_directory(self) -> bool:
        """
        Whether instance is representing a folder
        :return: Whether instance is representing a folder
        """
        return self.type == "DIR"

    @property
    def directory(self) -> str:
        """
        Generates the directory the file is in by stripping the filename from
        the path.
        :return: The directory the file is in.
        """
        return FileModel.rreplace(self.path, self.file_name, '')

    @staticmethod
    def rreplace(s: str, old: str, new: str) -> str:
        """
        Replace string starting from the back of the string.
        :param s: Current string
        :param old: String to replace
        :param new: Replacement string
        :return: The string with the old replaced by the new, but only at the
        end of the string.
        """
        return (s[::-1].replace(old[::-1], new[::-1], 1))[::-1]

    def __str__(self) -> str:
        return "partition: {0}\npartion_nr: {1}\nfile_name: {2}\n" \
               "extension: {3}\ntype: {4}\ndate_created: {5}\n" \
               "date_modified: {6}\ndate_changed: {7}\n" \
               "file_size: {8}\npath: {9}\ndirectory: {10}\nhash: {11}".format(
                   self.partition, self.partition_no, self.file_name,
                   self.extension, self.type, self.date_created,
                   self.date_modified, self.date_changed, self.file_size,
                   self.path, self.directory, self.hash
               )
