from io import BytesIO
from Models.FileModel import FileModel
from Utils.ImageHandler import ImageHandler

import tarfile
import zipfile
import langdetect


class ArchiveModel(FileModel):

    worksheet_base_headers = [
        "Full path",
        "File name",
        "Hash"
    ]

    worksheet_headers_lang = [
        *worksheet_base_headers,
        "Language"
    ]

    worksheet_headers_archive = [
        *worksheet_base_headers,
        "Archive type",
        "Contents"
    ]

    def __init__(self, file_info: []):
        super().__init__(file_info)
        self._archive_type = None

    @property
    def archive_type(self) -> str:

        if self._archive_type is not None:
            return self._archive_type

        self._archive_type = ""

        if self.file_name.endswith(".zip"):
            self._archive_type = "zip"

        if self.file_name.endswith(".tar.gz"):
            self._archive_type = "tar.gz"

        return self._archive_type

    @property
    def is_archive(self) -> bool:
        return self.archive_type != ""

    @property
    def is_text(self) -> bool:
        return self.file_name.endswith(".txt")

    @property
    def languages(self) -> str:
        if not self.is_text:
            return ""

        fake_file = BytesIO(self.get_bytes())
        textual_content = "".join(str(line) for line in fake_file.readlines())

        if len(textual_content) > 0:
            languages = langdetect.detect_langs(textual_content)
            return ", ".join(["{0} ({1}%)".format(x.lang, x.prob) for x in languages])

        return ""

    def archive_contens(self) -> []:
        if not self.is_archive:
            return []

        if self.archive_type == "zip":
            return self.extract_zip()

        if self.archive_type == "tar.gz":
            return self.extract_gz()

        return []

    def extract_gz(self) -> []:
        bestand = BytesIO(self.get_bytes())
        tarbestand = tarfile.open(None, "r:gz", fileobj=bestand)

        contents = tarbestand.getmembers()

        if contents is None:
            return []

        return [x.name for x in contents]

    def extract_zip(self) -> []:
        bestand = BytesIO(self.get_bytes())
        zipbestand = zipfile.ZipFile(bestand)

        contents = zipbestand.filelist

        if contents is None:
            return []

        return [x.filename for x in contents]

    def get_bytes(self) -> bytes:
        return ImageHandler().single_file(
            self.partition_no, self.directory,
            self.file_name, False
        )

    @property
    def xlsx_rows(self) -> []:
        base_rows = [
            self.path,
            self.file_name,
            self.hash
        ]

        if self.is_text:
            base_rows.append(self.languages)

        if self.is_archive:
            base_rows.append(self.archive_type)
            base_rows.append("; ".join(self.archive_contens()))

        return base_rows

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
