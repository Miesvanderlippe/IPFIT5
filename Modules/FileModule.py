from Interfaces.ModuleInterface import ModuleInterface
from Utils.ImageHandler import ImageHandler
from Utils.Store import Store
from Models.ArchiveModel import ArchiveModel
from Models.FileModel import FileModel
from multiprocessing.pool import ThreadPool as Pool
from multiprocessing import cpu_count
import hashlib
from Utils.XlsxWriter import XlsxWriter
import zipfile
from time import sleep
from io import BytesIO

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
        #FileModule.bestanden_lijst(self, data)
        FileModule.zip_bestanden(self, data)
        #FileModule.wegschrijven_bestandlist(self)

        self._progress = 100

    def bestanden_lijst(self, data):
        for partition in data:
            partition_lengte = len(partition)

            with Pool(processes=cpu_count()) as pool:
                bestanden = []
                [
                    pool.apply_async(self.best_lijst,(x,),callback=bestanden.append, error_callback=print)
                    for x in partition
                ]
                while partition_lengte != len(bestanden):
                    sleep(0.05)

                self.bestandslijst.extend(bestanden)
                #print(self.bestandslijst)

    @staticmethod
    def best_lijst(file_info: []) -> ArchiveModel:
        model = ArchiveModel(file_info)
        model.get_hash()
        #print(model)

    def zip_bestanden(self, data):
        for partition in data:
            for file_info in partition:
                bestanden = ArchiveModel(file_info)
                if bestanden.file_name.endswith(".zip"):
                    print(bestanden)
















    #def wegschrijven_bestandlist(self):
        # xslx_writer = XlsxWriter("BestandsModule")
        # xslx_writer.add_worksheet("BestandsLijst")
        # xslx_writer.write_headers("BestandsLijst", self.headers)
        # xslx_writer.write_items("BestandsLijst", self.bestandslijst)








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









