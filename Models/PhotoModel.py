import imghdr
import exifread

from Models.FileModel import FileModel
from Models.LogEntryModel import LogEntryModel
from Utils.ImageHandler import ImageHandler
from Utils.Logger import ExtendedLogger
from io import BytesIO


class PhotoModel(FileModel):
    """
    Model that holds file values for PhotoModule. Does some data manipulation
    and extracts values from files in image.
    """

    # Headers for Excel worksheet
    worksheet_headers = [
        "Full path",
        "File name",
        "Camera used",
        "True image type",
        "image_headers",
        "Hash"
    ]

    def __init__(self, file_info: []):
        """
        Initiates PhotoModel using file_info & parent constructor
        :param file_info: file_info array from ImageHandler
        """
        self._ingested = False
        self._img_type = None
        self._meta_data = {}

        self.logger = ExtendedLogger.get_instance(__class__.__name__)

        super().__init__(file_info)

    @property
    def is_image(self) -> bool:
        """
        Whether the file is an image.
        Ingests file when it's not ingested yet.
        :return: Whether the file is an image.
        """
        return self.img_type is not None

    @property
    def img_type(self) -> str:
        """
        Returns the true type of an image using imghdr.
        Ingests image when it's not ingested yet.
        :return: the image type
        """
        if not self._ingested:
            self.ingest_file()

        return self._img_type

    @property
    def img_meta(self) -> {}:
        """
        Returns the meta data of an image. Returns empty dict when file is not
        an image
        Ingests image when it's not ingested yet.
        :return: dict with meta data (key: value). Type of value is variable.
        """
        if not self._ingested:
            self.ingest_file()

        return self._meta_data

    @property
    def camera_model(self) -> str:
        """
        Builds the camera model from meta data.
        Ingests image when it's not ingested yet.
        :return: Camera make and model
        """
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
        """
        Gets image meta, true image type & hash from image. This can be very
        slow.
        """
        file = ImageHandler().single_file(
            self.partition_no, self.directory,
            self.file_name, False
        )

        if file is None:
            return None

        # may remove this in the future.
        self.get_hash()

        self._img_type = imghdr.what(None, h=file)

        if self._img_type is not None:
            exif_tags = exifread.process_file(BytesIO(file))

            self._meta_data = {
                meta_tag: meta_value
                for meta_tag, meta_value
                in exif_tags.items()
                # These tags just contain binary data or non-interesting data.
                if meta_tag not in (
                    "JPEGThumbnail", "TIFFThumbnail",
                    "Filename", "EXIF MakerNote")
                # Filter other thumbnail data
                and not meta_tag.startswith("Thumbnail")
            }

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

        self.logger.write_log(LogEntryModel.create_logentry(
            LogEntryModel.ResultType.positive,
            "Generating hash for {0}".format(self.path),
            "no motivation", "ImageHandler.single_file",
            "using ImageHandler and sha256", self.hash))

        return self.hash

    @property
    def worksheet_columns(self) -> []:
        """
        Returns some of the data in model according to columns in
        PhotoModel.worksheet_columns.
        :return: The data in a list.
        """
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
