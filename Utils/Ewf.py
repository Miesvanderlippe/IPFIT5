import pyewf
import pytsk3

from os import sep
from sys import setrecursionlimit
from pathlib import Path as PathlibPath

from Utils.Logging.Logging import Logging


class Ewf(pytsk3.Img_Info):
    def __init__(self, store):
        self.logger = Logging(self.__class__.__name__).logger
        self.store = store

        setrecursionlimit(100000)

        self.image_handle = None

        self.ext = PathlibPath(store.get_state()).suffix.lower()[1:]
        self.block_size = 0
        self.logger.debug('Extension: ' + self.ext)

        if self.ext == 'e01' or self.ext == 's01' or self.ext == 'ex01' or self.ext == 'l01' or self.ext == 'lx01':
            self.ewf_handle = pyewf.handle()
            self.ewf_handle.open(pyewf.glob(store.get_state()))
            self.logger.debug('EWF handle opened')
            self.logger.info('{} loaded with EWF'.format(
                store.get_state().split(sep)[-1]))
            super(Ewf, self).__init__(url='', type=pytsk3.TSK_IMG_TYPE_EXTERNAL)

    def close(self):
        self.logger.debug('EWF handle closed')
        self.ewf_handle.close()

    def read(self, offset, size):
        self.ewf_handle.seek(offset)
        return self.ewf_handle.read(size)

    def get_size(self):
        return self.ewf_handle.get_media_size()

    def info(self):
        if self.ext == 'e01' or self.ext == 's01' or self.ext == 'ex01' or self.ext == 'l01' or self.ext == 'lx01':
            volume = pytsk3.Volume_Info(self)
            self.close()
        else:
            self.image_handle = pytsk3.Img_Info(url=self.store.get_state())
            volume = pytsk3.Volume_Info(self.image_handle)

        self.block_size = volume.info.block_size
        return volume


class EwfInfoMenu(object):
    def __init__(self):
        self.logger = Logging(self.__class__.__name__).logger

    @staticmethod
    def menu(store):
        ewf = Ewf(store)
        volume = ewf.info()

        menu_items = [('Amount of partitions: {}'.format(volume.info.part_count), ''), ('', '')]

        for part in volume:
            menu_items.append(('Partition address: {}'.format(part.addr), ''))
            menu_items.append(('Partition start: {}'.format(part.start), ''))
            menu_items.append(('Partition length (relative): {}'.format(
                part.start + part.len - 1), ''))
            menu_items.append(('Partition length: {}'.format(part.len), ''))
            menu_items.append(('Partition description: {}'.format(
                part.desc.decode('UTF-8')), ''))

            menu_items.append(('', ''))

        return menu_items
