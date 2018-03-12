from Interfaces.ModuleInterface import ModuleInterface
from Utils.Store import Store
from Utils.Ewf import Ewf
import csv


class PhotoModule(ModuleInterface):

    def __init__(self) -> None:
        super().__init__()

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
    module = PhotoModule()
    # print(module.logger.name)  # PhotoModule

    store = Store()
    store.image_store.dispatch(
        {
            'type': 'set_image',
            'image': '/Users/Mies/Downloads/HFS.dd'
        }
    )

    ewf = Ewf()
    data = ewf.files()
    PhotoModule.write_csv(data, "files.csv")
