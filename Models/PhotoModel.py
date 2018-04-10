import imghdr
import exifread

from Models.FileModel import FileModel
from Utils.ImageHandler import ImageHandler
from io import BytesIO


class PhotoModel(FileModel):

    worksheet_headers = [
        "Full path",
        "File name",
        "Camera used",
        "True image type",
        "image_headers",
        "Hash"
    ]

    def __init__(self, file_info: []):

        self._ingested = False
        self._img_type = None
        self._meta_data = {}

        super().__init__(file_info)

    @property
    def is_image(self) -> bool:
        return self.img_type is not None

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

    @property
    def camera_model(self) -> str:
        meta = self.img_meta

        if len(meta) == 0:
            return "UNKNOWN CAMERA UNKNOWN MODEL"

        camera_make = str(
            meta["Image Make"] if "Image Make" in meta
            and len(str(meta["Image Make"]).strip()) > 0 else "UNKNOWN CAMERA"
        ).strip()

        camera_model = str(
            meta["Image Model"] if "Image Model" in meta
            and len(str(meta["Image Model"]).strip()) > 0 else "UNKNOWN MODEL"
        ).replace(camera_make, "").replace("-", "").strip()

        return "{0} {1}".format(
            camera_make,
            camera_model
        )

    def ingest_file(self) -> None:

        file = ImageHandler().single_file(
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
                and not meta_tag.startswith("Thumbnail")
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

        self.hash = ImageHandler().single_file(
            self.partition_no, self.directory,
            self.file_name, True
        )

        return self.hash

    @property
    def worksheet_columns(self) -> []:
        return [
            self.path,
            self.file_name,
            self.camera_model,
            str(self.img_type),
            " - ".join(
                ["{0}: {1}".format(x, y) for x, y in self.img_meta.items()]
            ),
            self.hash
        ]

    def __str__(self):
        base_str = super().__str__() + "\n"

        if self._ingested:
            if self.img_type is not None:
                base_str += "img_type: {0}\n".format(self.img_type)
                base_str += "camera_model: {0}\n".format(self.camera_model)
                base_str += "img_meta:\n"

                for exif_key, exif_value in self.img_meta.items():
                    base_str += "    {0}: {1}\n".format(exif_key, exif_value)

        else:
            base_str += "NOT INGESTED"

        return base_str
