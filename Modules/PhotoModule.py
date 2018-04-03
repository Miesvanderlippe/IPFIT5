from Interfaces.ModuleInterface import ModuleInterface
from Utils.Store import Store
from Utils.ImageHandler import ImageHandler
import csv


class PhotoModule(ModuleInterface):
    def __init__(self) -> None:
        self.ewf = ImageHandler()
        self._status = "Initialised"
        self._progress = 0

        super().__init__()

    def run(self) -> None:
        data = self.ewf.files()
        PhotoModule.write_csv(data, "files.csv")
        self._progress = 100

    def status(self) -> str:
        return self._status

    def progress(self) -> int:
        return self._progress

    @staticmethod
    def write_csv(data, output):
        if not data:
            return

        with open(output, 'w') as csvfile:
            csv_writer = csv.writer(csvfile)
            headers = ['Partition', 'File', 'File Ext', 'File Type',
                       'Create Date', 'Modify Date', 'Change Date', 'Size',
                       'File Path', 'Hash']
            csv_writer.writerow(headers)
            for result_list in data:
                csv_writer.writerows(result_list)


if __name__ == '__main__':
    store = Store()
    store.image_store.dispatch(
        {
            'type': 'set_image',
            'image': '/Users/Mies/Documents/swag.dd'
        }
    )

    photo_module = PhotoModule()
    photo_module.run()
