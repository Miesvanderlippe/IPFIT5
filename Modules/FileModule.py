from Interfaces.ModuleInterface import ModuleInterface
from Utils.ImageHandler import ImageHandler
from Utils.Store import Store
from Models.ArchiveModel import ArchiveModel
from Models.FileModel import FileModel
from multiprocessing import Pool, cpu_count
import hashlib
from Utils.XlsxWriter import XlsxWriter
import zipfile
from time import sleep

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
        self.bestandslijst = []


    def progress(self) -> int:
        return self._progress

    def status(self) -> str:
        return self._status

    def run(self) -> None:
        data = self.imagehandling.files()
        FileModule.bestanden_lijst(self, data)

        self._progress = 100

    def bestanden_lijst(self, data):
        for partition in data:
             for file_info in partition:
                model = ArchiveModel(file_info)
                model.get_hash()
                print(model)

    @staticmethod
    def best_lijst(file_info: []) -> ArchiveModel:
        model = ArchiveModel(file_info)
        model.get_hash()
        print(model)

    def archieven_uitlezen(self, data):
        pass


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









