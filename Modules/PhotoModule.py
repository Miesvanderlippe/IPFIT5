from Interfaces.ModuleInterface import ModuleInterface
from Utils.Store import Store
from Utils.ImageHandler import ImageHandler
from Models.PhotoModel import PhotoModel
from multiprocessing import Pool, cpu_count
from time import sleep


class PhotoModule(ModuleInterface):
    def __init__(self) -> None:
        self.ewf = ImageHandler()
        self._status = "Initialised"
        self._progress = 0

        super().__init__()

    def run(self) -> None:
        data = self.ewf.files()
        files = []

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

            files.extend(results)

        cameras = PhotoModule.get_cameras(files)

        print("\n".join(cameras))

        with open("test.txt", "w") as test_file:
            for photo_model in files:
                try:
                    test_file.write(str(photo_model))
                except Exception as e:
                    print(e)

        self._progress = 100

    def status(self) -> str:
        return self._status

    def progress(self) -> int:
        return self._progress

    @staticmethod
    def get_cameras(files: []) -> ():
        return set([
            x.camera_model
            for x in files
            if x.is_image
        ])

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
