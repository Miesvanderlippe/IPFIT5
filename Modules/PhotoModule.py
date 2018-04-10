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
        self.cameras = []
        self.files = []
        self._status = "Initialised"
        self._progress = 0

        super().__init__()

    def run(self) -> None:
        data = self.ewf.files()

        for partition in data:
            partition_length = len(partition)

            with Pool(processes=cpu_count()) as pool:
                results = []
                [
                    pool.apply_async(self.ingest_file, (x,),
                                     callback=results.append,
                                     error_callback=print)
                    for x in partition
                ]

                while partition_length != len(results):
                    sleep(0.05)

                self.files.extend(results)

        self.cameras = PhotoModule.get_cameras(self.files)
        self.create_export()
        self._progress = 100

    def status(self) -> str:
        return self._status

    def progress(self) -> int:
        return self._progress

    def create_export(self) -> None:
        # xslx_writer = XlsxWriter("Photos")

        for camera in self.cameras:
            print("\nCamera: {0}\n".format(camera))
            print("\n".join(
                [
                    str(x) for x in
                    PhotoModule.get_files_by_cam(self.files, camera)
                ]
            ))

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
            'image': '/Users/Mies/Documents/lubuntu.dd'
        }
    )

    photo_module = PhotoModule()
    photo_module.run()
