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
import tarfile, io
import langdetect


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
        self.inhoud_zip_bestanden = []
        self.info_zip_bestanden = []
        self.info_tar_bestanden = []
        self.inhoud_tar_bestanden = []
        self.namen_txt_bestanden = []
        self.taalkans_txt_bestanden = []

    def progress(self) -> int:
        return self._progress

    def status(self) -> str:
        return self._status

    def run(self) -> None:
        data = self.imagehandling.files()
        #FileModule.bestanden_lijst(self, data)
        #FileModule.inhoud_zip_archieven(self, data)
        #FileModule.namen_zip_archieven(self, data)
        #FileModule.namen_tar_archieven(self, data)
        #FileModule.inhoud_tar_archieven(self, data)
        FileModule.namen_txt_files(self, data)
        FileModule.taalbepalen_txt_files(self, data)

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

    def inhoud_zip_archieven(self, data):
         data = self.imagehandling.files("\\.zip$")
         for partition in data:
             for file_info in partition:
                file_model = FileModel(file_info)
                file_bytes = ImageHandler().single_file(file_model.partition_no, file_model.directory,
                                                        file_model.file_name, False)
                bestand = BytesIO(file_bytes)
                zipbestand = zipfile.ZipFile(bestand)
                self.inhoud_zip_bestanden.extend(zipbestand.filelist)
                #print(self.inhoud_zip_bestanden)

    def namen_zip_archieven(self, data):
         for partition in data:
            for file_info in partition:
                bestanden = ArchiveModel(file_info)
                if bestanden.file_name.endswith(".zip"):
                    self.info_zip_bestanden.append(bestanden.file_name)
         #print(self.info_zip_bestanden)



    def inhoud_tar_archieven(self, data):
        data = self.imagehandling.files("\\.tar.gz$")
        result = []
        for partition in data:
            for file_info in partition:
                file_model = FileModel(file_info)
                file_bytes = ImageHandler().single_file(file_model.partition_no, file_model.directory,
                                                        file_model.file_name, False)
                bestand = BytesIO(file_bytes)
                tarbestand = tarfile.open(None,"r:gz",fileobj=bestand)
                self.inhoud_tar_bestanden.append(tarbestand.list(verbose=False))
                #print(self.inhoud_tar_bestanden)
                # self.inhoud_tar_bestanden.extend(tarbestand.getnames())
                # print(self.inhoud_tar_bestanden)


    def namen_tar_archieven(self, data):
        for partition in data:
            for file_info in partition:
                files = ArchiveModel(file_info)
                if files.file_name.endswith(".tar.gz"):
                    self.info_tar_bestanden.append(files.file_name)
        #print(self.info_tar_bestanden)

    def namen_txt_files(self, data):
        data = self.imagehandling.files("\\.txt$")
        for partition in data:
            for file_info in partition:
                bestandje = ArchiveModel(file_info)
                if bestandje.file_name.endswith(".txt"):
                    self.namen_txt_bestanden.append(bestandje.file_name)
        #print(self.namen_txt_bestanden)

    def taalbepalen_txt_files(self, data):
        data = self.imagehandling.files("\\.txt$")
        for partition in data:
            for file_info in partition:
                file_model = FileModel(file_info)
                file_bytes = ImageHandler().single_file(file_model.partition_no, file_model.directory,
                                                        file_model.file_name, False)
                fake_file = BytesIO(file_bytes)

                textual_content = "".join(str(line) for line in fake_file.readlines())

                if len(textual_content) > len(self.namen_txt_bestanden):
                    try:
                        languages = langdetect.detect_langs(textual_content)
                        self.taalkans_txt_bestanden.append(languages)
                    except Exception as e:
                        pass
            #print(self.taalkans_txt_bestanden)

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









