from Interfaces.ModuleInterface import ModuleInterface
from Utils.ImageHandler import ImageHandler
from Utils.Store import Store
from hashlib import sha256
import xlsxwriter
import csv


class FileModule(ModuleInterface):

    def __init__(self) -> None:
        super().__init__()
        self.imagehandler = ImageHandler()
        self._status = "Initialised"
        self._progress = 0
        self.headers = ['Partition\n', 'File\n', 'File Ext\n', 'File Type\n', 'Create Date\n', 'Modify Date\n',
                        'Change Date\n', 'Size\n', 'File Path\n']
        self.workbook = xlsxwriter.Workbook("UitvoerBestandsModule.xlsx")


    def progress(self) -> int:
        return self._progress

    def status(self) -> str:
        return self._status

    def run(self) -> None:
        data = self.imagehandler.files()
        self.bestandslijst()
        self._progress = 100

    def bestandslijst(self):
        self.bestandslijsttab = self.workbook.add_worksheet("Bestanden", None)
        for kolom, header in enumerate(self.headers):
            self.bestandslijsttab.write(0,kolom,self.headers[kolom])
        self.workbook.close()


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









