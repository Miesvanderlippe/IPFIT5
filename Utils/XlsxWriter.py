from pathlib import Path
from typing import List

from xlsxwriter import Workbook
from Utils.Store import Store


class XlsxWriter:
    def __init__(self, name: str) -> None:
        self.workbook = Workbook(self.get_save_path(name))
        self.worksheets = {}
        self.headers = None

    @staticmethod
    def get_save_path(name: str) -> str:
        """
        Get the filepath to where the XLSX workbook should be saved

        :param name: Name of the XLSX workbook

        :return: Absolute filepath
        """
        # Make output folder
        config_path = Path(__file__).parent.parent.joinpath('Output')
        Path.mkdir(Path(config_path), exist_ok=True)

        credentials = Store().credential_store.get_state()
        case = credentials["case"]

        # Make case folder
        case_path = Path(config_path.joinpath(case))
        Path.mkdir(Path(case_path), exist_ok=True)

        return str(
            case_path.joinpath('{}.xlsx'.format(
                name.replace(' ', '-')
            ))
        )

    def add_worksheet(self, name: str) -> None:
        """
        Add an worksheet to the workbook

        :param name: Name of the new worksheet

        :return: None
        """
        self.worksheets[name] = self.workbook.add_worksheet(name)

    def write_headers(self, worksheet: str, headers: List[str]) -> None:
        """
        Write headers to a worksheet

        :param worksheet: Worksheet to write the headers to
        :param headers: A list with all the headers

        :return: None
        """
        self.headers = headers

        bold = self.workbook.add_format({'bold': True})
        bold.set_center_across()

        for i, header in enumerate(headers):
            self.worksheets[worksheet].write(0, i, header, bold)

    def write_items(self, worksheet: str, items: List[List[str]]) -> None:
        """
        Write items to a worksheet

        :param worksheet: Worksheet to write the headers to
        :param items: A list with all the items

        :return: None
        """
        for i, item_list in enumerate(items):
            for j, item in enumerate(item_list):
                self.worksheets[worksheet].write(i + 2, j, item)

        self.set_width(worksheet, self.get_width(self.headers, items))

    @staticmethod
    def get_width(headers: List[str], items: List[List[str]]) -> List[int]:
        """
        Get the width of each column in a worksheet based on the content

        :param headers: Headers of the worksheet
        :param items: All the items in the worksheet

        :return: The best width for each column in the worksheet
        """
        if headers is None:
            width = [0 for _ in items[0]]
        else:
            width = [len(i) for i in headers]

        for item_list in items:
            for j, item in enumerate(item_list):
                if width[j] < len(str(item)):
                    width[j] = len(str(item))

        return width

    def set_width(self, worksheet: str, width: List[int]) -> None:
        """
        Set the width of each column in a worksheet

        :param worksheet: Worksheet to set the width of the columns
        :param width: All the widths to use

        :return: None
        """
        for i, w in enumerate(width):
            self.worksheets[worksheet].set_column(i, i, w + 1)

    def close(self) -> None:
        """
        Close the XLSX workbook object

        :return: None
        """
        self.workbook.close()
