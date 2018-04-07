
class ImageFileModel:

    def __init__(self, file_info: []):
        self.partition = file_info[0]
        self.partition_no = int(file_info[0][-1])
        self.file_name = file_info[1]
        self.extension = file_info[2]
        self.type = file_info[3]
        self.date_created = file_info[4]
        self.date_modified = file_info[5]
        self.date_changed = file_info[6]
        self.file_size = file_info[7]
        self.path = file_info[8]
        # Hash doesn't always exist
        self.hash = file_info[9] if len(file_info) >= 10 else None

    @property
    def is_file(self) -> bool:
        return self.type == "FILE"

    @property
    def is_directory(self) -> bool:
        return self.type == "DIR"

    @property
    def directory(self) -> str:
        return ImageFileModel.rreplace(self.path, self.file_name, '')

    @staticmethod
    def rreplace(s: str, old: str, new: str) -> str:
        return (s[::-1].replace(old[::-1], new[::-1], 1))[::-1]

    def __str__(self):
        return "partition: {0}\npartion_nr: {1}\nfile_name: {2}\n" \
               "extension: {3}\ntype: {4}\ndate_created: {5}\n" \
               "date_modified: {6}\ndate_changed: {7}\n" \
               "file_size: {8}\npath: {9}\ndirectory: {10}\nhash: {11}".format(
                    self.partition, self.partition_no, self.file_name,
                    self.extension, self.type, self.date_created,
                    self.date_modified, self.date_changed, self.file_size,
                    self.path, self.directory, self.hash
                )
