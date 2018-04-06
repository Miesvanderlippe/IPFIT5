from Interfaces.ModuleInterface import ModuleInterface
from Utils.ImageHandler import ImageHandler
from Utils.Store import Store
from hashlib import sha256
from Utils.XlsxWriter import XlsxWriter

class FileModule(ModuleInterface):

    def __init__(self) -> None:
        super().__init__()
        self.imagehandling = ImageHandler()
        self._status = "Initialised"
        self._progress = 0
        self.headers = [
                        'Partition',
                        'File',
                        'File Ext',
                        'File Type',
                        'Create Date',
                        'Modify Date',
                        'Change Date',
                        'Size',
                        'File Path'
                        ]

    def progress(self) -> int:
        return self._progress

    def status(self) -> str:
        return self._status

    def run(self) -> None:
        data = self.imagehandling.files()
        FileModule.bestanden_lijst(self, data)
        #   FileModule.write_csv(data, "test.csv")
        self._progress = 100

    # @staticmethod
    # def write_csv(data, output):
    #     if not data:
    #         return
    #
    #     with open(output, 'w', encoding="utf-8") as csvfile:
    #         csv_writer = csv.writer(csvfile)
    #         headers = ['Partition', 'File', 'File Ext', 'File Type',
    #                    'Create Date', 'Modify Date', 'Change Date', 'Size',
    #                    'File Path', 'Hash']
    #         csv_writer.writerow(headers)
    #         for result_list in data:
    #             csv_writer.writerows(result_list)


    def bestanden_lijst(self, data):
        lijst = []
        teller = 0
        for item in data[0]:
            item[0:0] = [teller]
            teller += 1
            lijst.append(item)
        print(lijst)

    def bestanden_hashen(self):


if __name__ == '__main__':

    store = Store()
    store.image_store.dispatch(
        {
            'type': 'set_image',
            'image': 'C:\\Studie\\ipfit5\\lubuntu.dd'
        }
    )
    module = FileModule()
    module.run()









