from copy import copy
from datetime import datetime
from Interfaces.ModuleInterface import ModuleInterface
from Models.ArchiveModel import ArchiveModel
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool as Pool
from time import sleep
from Utils.ImageHandler import ImageHandler
from Utils.Store import Store
from Utils.XlsxWriter import XlsxWriter
from Models.LogEntryModel import LogEntryModel

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

        self.logger.write_log(LogEntryModel.create_logentry(
            LogEntryModel.ResultType.informative,
            "Ingested file {0}".format(model.path),
            "Digest some data", "ArchiveModel.after_ingest()",
            "using ArchiveModel and FileModule", "File ingested"))

        self.files.append(model)

    @staticmethod
    def ingest_file(file_info: []) -> ArchiveModel:
        model = ArchiveModel(file_info)
        # model.get_hash()

        return model

    def generate_timeline(self) -> []:
        timeline = []

        for file_model in self.files:
            # created date is formated to string, or none if it isn't a date
            create = file_model.date_created.strftime('%d-%m-%Y %H:%M:%S') if \
                isinstance(file_model.date_created, datetime) else None
            # same for the rest of the values
            modify = file_model.date_modified.strftime('%d-%m-%Y %H:%M:%S') if \
                isinstance(file_model.date_modified, datetime) else None
            change = file_model.date_changed.strftime('%d-%m-%Y %H:%M:%S') if \
                isinstance(file_model.date_changed, datetime) else None

            timeline.append(file_model)

            # If all timestamp fields are filled
            if all(x is not None for x in [create, modify, change]):
                # We check if the date created is different from the modified
                # date and append a copy if that is the case.
                if create != modify:
                    timeline.append(copy(file_model))

                # If there's another unique value between changed, modified &
                # created we append another copy ( so there'd be 3 copies
                # in the timeline for 3 events)
                if (create != change and change != modify) or \
                        (modify != change and change != create):
                    timeline.append(copy(file_model))

            # Else, if there's only two dates in the three timestamps
            elif sum(x is not None for x in [create, modify, change]) == 2:
                # We get the two values that do hold a date
                values = [x for x in [create, modify, change] if x is not None]

                # and append a copy if they're different (there'd be 2 copies
                # in the timeline).
                # The two values could be any combination of the three
                # possible timestamps but we only care if they're different
                if values[0] != values[1]:
                    timeline.append(copy(file_model))

        # First, sort timeline on creation date. If there isn't any the value
        # will be the minimum date so the item will be at the bottom of the
        # timeline.
        timeline.sort(key=lambda x: x.date_created
                      if isinstance(x.date_created, datetime)
                      else datetime.min)
        # Next, we sort on modified with the same min-date rule
        timeline.sort(key=lambda x: x.date_modified
                      if isinstance(x.date_modified, datetime)
                      else datetime.min)
        # Last, it's changed date.
        # Because irrelevant items won't be moved you now have a sorted
        # timeline.
        timeline.sort(key=lambda x: x.date_changed
                      if isinstance(x.date_changed, datetime)
                      else datetime.min)

        return timeline

    def gen_exports(self) -> None:
        xslx_writer = XlsxWriter("FileModule")

        xslx_writer.add_worksheet("Timeline")
        xslx_writer.write_headers("Timeline",
                                  ArchiveModel.worksheet_headers_timeline)
        xslx_writer.write_items("Timeline",
                                [x.xlsx_rows(True) for x in self.files])

        xslx_writer.add_worksheet("Archives")
        xslx_writer.write_headers("Archives",
                                  ArchiveModel.worksheet_headers_archive)
        xslx_writer.write_items("Archives",
                                [x.xlsx_rows() for x in self.archives])

        xslx_writer.add_worksheet("Text files")
        xslx_writer.write_headers("Text files",
                                  ArchiveModel.worksheet_headers_lang)
        xslx_writer.write_items("Text files",
                                [x.xlsx_rows() for x in self.text_files])

        xslx_writer.close()

        self.logger.write_log(LogEntryModel.create_logentry(
            LogEntryModel.ResultType.informative,
            "Generated timeline",
            "Make data readable", "ArchiveModel.gen_exports()",
            "using ArchiveModel and FileModule", "Timeline generated"))


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
