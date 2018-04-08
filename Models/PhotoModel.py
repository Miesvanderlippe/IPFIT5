import imghdr
import exifread

from Models.FileModel import FileModel
from Utils.ImageHandler import ImageHandler
from io import BytesIO


class PhotoModel(FileModel):

    def __init__(self, file_info: [], ewf: ImageHandler):

        self.ewf = ewf
        self._ingested = False
        self._img_type = None
        self._meta_data = {}

        super().__init__(file_info)

    @property
    def img_type(self) -> str:
        if not self._ingested:
            self.ingest_file()

        return self._img_type

    @property
    def img_meta(self) -> {}:
        if not self._ingested:
            self.ingest_file()

        return self._meta_data

    def ingest_file(self) -> None:

        file = self.ewf.single_file(
            self.partition_no, self.directory,
            self.file_name, False
        )

        if file is None:
            return None

        self.get_hash()

        self._img_type = imghdr.what(None, h=file)

        if self._img_type is not None:
            exif_tags = exifread.process_file(BytesIO(file))

            self._meta_data = {
                meta_tag: meta_value
                for meta_tag, meta_value
                in exif_tags.items()
                if meta_tag not in (
                    "JPEGThumbnail", "TIFFThumbnail",
                    "Filename", "EXIF MakerNote")
            }

        # Forgive me father for I have sinned.
        self._ingested = True

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

        self.hash = self.ewf.single_file(
            self.partition_no, self.directory,
            self.file_name, True
        )

        return self.hash

    def __str__(self):
        base_str = super().__str__() + "\n"

        if self._ingested:
            if self.img_type is not None:
                base_str += "img_type: {0}\n".format(self.img_type)
                base_str += "img_meta:\n"

                for exif_key, exif_value in self.img_meta.items():
                    base_str += "    {0}: {1}\n".format(exif_key, exif_value)

        else:
            base_str += "NOT INGESTED"

        return base_str
