from Interfaces.ModuleInterface import ModuleInterface
from Models.ArchiveModel import ArchiveModel
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool as Pool
from time import sleep
from Utils.ImageHandler import ImageHandler
from Utils.Store import Store
from Utils.XlsxWriter import XlsxWriter


class FileModule(ModuleInterface):

    headers = [
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

    def __init__(self) -> None:
        super().__init__()
        self.image_handler = ImageHandler()
        self.files = []
        self.archives = []
        self.text_files = []
        self._status = "Initialised"
        self._progress = 0

    def progress(self) -> int:
        return self._progress

    def status(self) -> str:
        return self._status

    def run(self) -> None:
        data = self.image_handler.files()
        total_length = 0

        for partition in data:
            total_length += len(partition)

            with Pool(processes=cpu_count()) as pool:
                [
                    pool.apply_async(FileModule.ingest_file, (x,),
                                     callback=self.after_ingest,
                                     error_callback=print)
                    for x in partition
                ]

                while total_length != len(self.files):
                    # print("{0}; {1}".format(partition_lengte, len(bestanden)))
                    sleep(0.05)

        self.gen_exports()
        self._progress = 100

    def after_ingest(self, model: ArchiveModel) -> None:
        if model.is_archive:
            self.archives.append(model)

        elif model.is_text:
            self.text_files.append(model)

        self.files.append(model)

    @staticmethod
    def ingest_file(file_info: []) -> ArchiveModel:
        model = ArchiveModel(file_info)
        # model.get_hash()

        return model

    def gen_exports(self) -> None:
        xslx_writer = XlsxWriter("FileModule")

        xslx_writer.add_worksheet("Archives")
        xslx_writer.write_headers("Archives",
                                  ArchiveModel.worksheet_headers_archive)
        xslx_writer.write_items("Archives",
                                [x.xlsx_rows for x in self.archives])

        xslx_writer.add_worksheet("Text files")
        xslx_writer.write_headers("Text files",
                                  ArchiveModel.worksheet_headers_lang)
        xslx_writer.write_items("Text files",
                                [x.xlsx_rows for x in self.text_files])

        xslx_writer.close()


if __name__ == '__main__':

    store = Store()
    store.image_store.dispatch(
        {
            'type': 'set_image',
            'image': '/Users/Mies/Documents/lubuntu.dd'
        }
    )
    module = FileModule()
    module.run()
