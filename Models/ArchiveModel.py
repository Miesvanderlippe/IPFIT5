from datetime import datetime
from io import BytesIO
from Models.FileModel import FileModel
from Utils.ImageHandler import ImageHandler
from Models.LogEntryModel import LogEntryModel
from Utils.Logger import ExtendedLogger

import tarfile
import zipfile
import langdetect


class ArchiveModel(FileModel):

    worksheet_base_headers = [
        "Full path",
        "File name",
        "Hash"
    ]

    worksheet_headers_timeline = [
        *worksheet_base_headers,
        "Date created",
        "Date modified",
        "Date changed"
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
        # Cache archive type
        self._archive_type = None
        # Cache contents
        self._archive_contents = None
        # Cache languages
        self._languages = None
        self.logger = ExtendedLogger.get_instance(__class__.__name__)

    @property
    def archive_type(self) -> str:
        """
        Returns the type of archive this file represents or "" if it isn't an
        archive. This is achieved by checking the extension but it may be
        updated to check for headers later on.
        :return: archive type (zip, tar.gz)
        """

        if self._archive_type is not None:
            return self._archive_type

        # Set archive type to empty str so if file isn't archive we don't
        # run the function time and time again but instead return empty str.
        self._archive_type = ""

        # Should be a different check but hey, extensions are quick
        if self.file_name.endswith(".zip"):
            self._archive_type = "zip"

        if self.file_name.endswith(".tar.gz"):
            self._archive_type = "tar.gz"

        return self._archive_type

    @property
    def is_archive(self) -> bool:
        """
        Returns whether the file is an archive. Does it by checking if archive
        type isn't default.
        :return: bool is archive
        """
        return self.archive_type != ""

    @property
    def is_text(self) -> bool:
        """
        Returns whether the file is a text file.
        :return: bool is text
        """
        return self.file_name.endswith(".txt")

    @property
    def languages(self) -> str:
        """
        String representing the languages found in the file if there's any.
        Language is represented by 2 letter ISO country code + probability the
        detected language is right.
        :return: lang (probability %)
        """
        # Return cached contents
        if self._languages is not None:
            return self._languages

        # Make sure we don't re-run the function
        self._languages = ""

        # Return if not text
        if not self.is_text:
            return self._languages

        # Create fake file from filebytes
        fake_file = BytesIO(self.get_bytes())
        # Read contents
        textual_content = "".join(str(line) for line in fake_file.readlines())

        # Check if there's any contents
        if len(textual_content) > 0:
            # Detect the languages
            languages = langdetect.detect_langs(textual_content)
            self._languages = ", ".join(
                ["{0} ({1}%)".format(x.lang, x.prob) for x in languages])

        self.logger.write_log(LogEntryModel.create_logentry(
            LogEntryModel.ResultType.positive,
            "Indexed languages in {0}".format(self.path),
            "Index textual files", "ArchiveModel.languages",
            "using langdetect", ";".join(self._languages)))

        return self._languages

    def archive_contens(self) -> []:
        """
        Returns the contents of the archive. Returns a list of files, or an
        empty list if this isn't an archive.
        :return: list of files in archive
        """
        if self._archive_contents is not None:
            return self._archive_contents

        self._archive_contents = []

        if not self.is_archive:
            return self._archive_contents

        if self.archive_type == "zip":
            self._archive_contents = self.extract_zip()

        elif self.archive_type == "tar.gz":
            self._archive_contents = self.extract_gz()

        self.logger.write_log(LogEntryModel.create_logentry(
            LogEntryModel.ResultType.positive,
            "Extracted data from {0}".format(self.path),
            "Index archive contents", "ArchiveModel.archive_contens",
            "using python archive handles", ";".join(self._archive_contents)))

        return self._archive_contents

    def extract_gz(self) -> []:
        """
        Extracts filenames from tar.gz archive.
        :return: list of filenames
        """
        bestand = BytesIO(self.get_bytes())
        tarbestand = tarfile.open(None, "r:gz", fileobj=bestand)

        contents = tarbestand.getmembers()

        if contents is None:
            return []

        return [x.name for x in contents]

    def extract_zip(self) -> []:
        """
        Extracts filenames from zip archive.
        :return: list of filenames
        """
        bestand = BytesIO(self.get_bytes())
        zipbestand = zipfile.ZipFile(bestand)

        contents = zipbestand.filelist

        if contents is None:
            return []

        return [x.filename for x in contents]

    def get_bytes(self) -> bytes:
        """
        Returns the bytes of the file. Returns None if failed.
        :return: bytes of file
        """
        return ImageHandler().single_file(
            self.partition_no, self.directory,
            self.file_name, False
        )

    def xlsx_rows(self, timeline_headers: bool = False) -> []:
        """
        Rows ready to be written to xlsx export. May contain different rows
        like archive contents if the file is an archive or languages if the
        file is a text file.
        :return: string[] with values of file
        """
        base_rows = [
            self.path,
            self.file_name,
            self.hash
        ]

        if timeline_headers:
            base_rows.append(
                self.date_created.strftime('%d-%m-%Y %H:%M:%S')
                if isinstance(self.date_created, datetime)
                else str(self.date_created))
            base_rows.append(
                self.date_modified.strftime('%d-%m-%Y %H:%M:%S')
                if isinstance(self.date_modified, datetime)
                else str(self.date_modified))
            base_rows.append(
                self.date_changed.strftime('%d-%m-%Y %H:%M:%S')
                if isinstance(self.date_changed, datetime)
                else str(self.date_changed))

        elif self.is_text:
            base_rows.append(self.languages)

        elif self.is_archive:
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

        self.logger.write_log(LogEntryModel.create_logentry(
            LogEntryModel.ResultType.positive,
            "Generating hash for {0}".format(self.path),
            "no motivation", "ImageHandler.single_file",
            "using ImageHandler and sha256", self.hash))

        return self.hash

    def __str__(self):
        base_str = super().__str__() + "\n"

        base_str += "is_archive: {0}\n".format(str(self.is_archive))
        base_str += "is_text: {0}\n".format(str(self.is_text))

        if self.is_text:
            base_str += "found languages: {0}\n".format(self.languages)

        if self.is_archive:
            base_str += "Archive content: \n"
            for file_name in self.archive_contens():
                base_str += "    {0}\n".format(file_name)

        return base_str
