from Models.FileModel import FileModel
from Utils.ImageHandler import ImageHandler


class ArchiveModel(FileModel):

    def __init__(self, file_info: []):
        super().__init__(file_info)

    def get_hash(self) -> str:
        """
        Generates and returns a hash if the hash doesn't exist yet. Returns
        "" if failed or if directory.
        :return: A sha256 file hash
        """

        if not self.is_file:
            return ""

        if self.hash is not None and len(self.hash) > 0:
            return self.hash

        self.hash = ImageHandler().single_file(
            self.partition_no, self.directory,
            self.file_name, True
        )

        return self.hash

    def __str__(self):
        base_str = super().__str__() + "\n"

        # Add extra info to to str here

        return base_str
