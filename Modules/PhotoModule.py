from Interfaces.ModuleInterface import ModuleInterface
from Utils.Store import Store
from Utils.ImageHandler import ImageHandler
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
        self._status = "Initialised"
        self._progress = 0

        self._xlsx_writer = None

        super().__init__()

    @property
    def xlsx_writer(self) -> XlsxWriter:
        if self._xlsx_writer is None:
            self._xlsx_writer = XlsxWriter("PhotosModule")

        return self._xlsx_writer

    def run(self) -> None:
        data = self.ewf.files()
        total_results = 0

        for partition in data:
            partition_length = len(partition)
            total_results += partition_length

            with Pool(processes=cpu_count()) as pool:
                [
                    pool.apply_async(self.ingest_file, (x,),
                                     callback=self.after_ingest,
                                     error_callback=print)
                    for x in partition
                ]

                while total_results != len(self.files):
                    sleep(0.05)

        self.create_export()
        self._progress = 100

    def status(self) -> str:
        return self._status

    def progress(self) -> int:
        return self._progress

    def create_export(self) -> None:

        for camera in self.cameras:
            self.xlsx_writer.add_worksheet(camera)

            self.xlsx_writer.write_headers(camera, PhotoModel.worksheet_headers)

            self.xlsx_writer.write_items(camera, [
                x.worksheet_columns for x in self.images_by_camera[camera]
            ])

        self.xlsx_writer.close()

    def after_ingest(self, file_model: PhotoModel) -> None:

        self.files.append(file_model)

        if file_model.is_image:
            camera_model = file_model.camera_model

            self.cameras.add(camera_model)

            if camera_model not in self.images_by_camera.keys():
                self.images_by_camera[camera_model] = []

            self.images_by_camera[camera_model].append(file_model)


    @staticmethod
    def get_cameras(files: []) -> ():
        return set([
            x.camera_model
            for x in files
            if x.is_image
        ])

    @staticmethod
    def get_files_by_cam(files: [], camera_model: str) -> []:
        return [
            x
            for x in files
            if x.is_image and
            x.camera_model == camera_model
        ]

    @staticmethod
    def ingest_file(file_info: []) -> PhotoModel:
        model = PhotoModel(file_info)

        try:
            model.ingest_file()
            # print("Ingested {0}".format(model.file_name))
        except Exception as e:
            print("Couldn't ingest {0}".format(model.file_name))
            print(e)

        return model


if __name__ == '__main__':
    store = Store()
    store.image_store.dispatch(
        {
            'type': 'set_image',
            'image': '/Users/Mies/Documents/usb_with_images.dd'
        }
    )

    photo_module = PhotoModule()
    photo_module.run()
