from os import name
from Interfaces.ModuleInterface import ModuleInterface
from Utils.Store import Store
from Utils.ImageHandler import ImageHandler
from Models.LogEntryModel import LogEntryModel
from Models.PhotoModel import PhotoModel
from multiprocessing.pool import ThreadPool as Pool
from multiprocessing import cpu_count
from Utils.XlsxWriter import XlsxWriter
from time import sleep


class PhotoModule(ModuleInterface):
    def __init__(self) -> None:
        self.ewf = ImageHandler()
        self.cameras = set()
        self.images_by_camera = {}
        self.files = []

        self._xlsx_writer = None

        super().__init__()

        self.logger.write_log(LogEntryModel.create_logentry(
            LogEntryModel.ResultType.informative, "Initiated photo module",
            "no motivation", "PhotoModule()", "using PhotoModule", "Initiated"))


    @property
    def xlsx_writer(self) -> XlsxWriter:
        """
        Returns an instance of XLSX writer and creates one if none exist.
        :return: xlsxwriter
        """
        if self._xlsx_writer is None:
            self._xlsx_writer = XlsxWriter("PhotosModule")

        return self._xlsx_writer

    def run(self) -> None:
        """
        Runs the module.
        """
        # Get partitions & files
        data = self.ewf.files()

        # nr of results we expect (used later on)
        total_results = 0

        for partition in data:
            # expand results to be expected, we'll wait on the results to get
            # to this number
            partition_length = len(partition)
            total_results += partition_length

            with Pool(processes=cpu_count()) as pool:
                [
                    pool.apply_async(self.ingest_file, (x,),
                                     callback=self.after_ingest,
                                     error_callback=print)  # TODO: Logger
                    for x in partition
                ]

                while total_results != len(self.files):
                    sleep(0.05)

        self.create_export()
        self._progress = 100

    def status(self) -> str:
        """
        Should return what the moduel is doing.
        :return: str, current job
        """
        return ""

    def progress(self) -> int:
        """
        Current progression (0-100)
        :return: int, percentage to done
        """
        return 100

    def create_export(self) -> None:
        """
        Generate the expected outputs
        """
        prefix = 0

        for camera in self.cameras:

            prefix += 1

            camera_key = "{0:03d} {1}".format(prefix, camera[0:25])

            self.xlsx_writer.add_worksheet(camera_key)

            self.xlsx_writer.write_headers(camera_key,
                                           PhotoModel.worksheet_headers)

            self.xlsx_writer.write_items(camera_key, [
                x.worksheet_columns for x in self.images_by_camera[camera]
            ])

        self.xlsx_writer.close()

        self.logger.write_log(LogEntryModel.create_logentry(
            LogEntryModel.ResultType.positive, "Generated camera exports",
            "Make info readable", "PhotoModule.create_export()",
            "using PhotoModule and XlsxWriter", "Exports created"))

    def after_ingest(self, file_model: PhotoModel) -> None:
        """
        Keeps the camera models & pictures by camera lists up to date.
        :param file_model: The file after ingestion
        """
        self.files.append(file_model)

        if file_model.is_image:
            camera_model = file_model.camera_model

            self.cameras.add(camera_model)

            if camera_model not in self.images_by_camera.keys():
                self.images_by_camera[camera_model] = []

            self.images_by_camera[camera_model].append(file_model)
        self.logger.write_log(LogEntryModel.create_logentry(
            LogEntryModel.ResultType.informative,
            "Ingested file {0}".format(file_model.path),
            "Digest some data", "PhotoModule.after_ingest()",
            "using PhotoModule and PhotoModel", "File ingested"))

    @staticmethod
    def ingest_file(file_info: []) -> PhotoModel:
        model = PhotoModel(file_info)

        try:
            model.ingest_file()
            # TODO: Logger
            # print("Ingested {0}".format(model.file_name))
        except Exception as e:
            # TODO: Logger
            print("Couldn't ingest {0}".format(model.file_name))
            print(e)

        return model


if __name__ == '__main__':
    store = Store()
    store.image_store.dispatch(
        {
            'type': 'set_image',
            'image': '/Users/Mies/Documents/lubuntu.dd'
        }
    )

    photo_module = PhotoModule()
    photo_module.run()
