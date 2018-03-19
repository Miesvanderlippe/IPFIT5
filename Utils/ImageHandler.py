from re import search, I
from hashlib import sha256
from sys import setrecursionlimit
from pathlib import Path as PathlibPath
from datetime import datetime
from Utils.Store import Store
from typing import List, Union, Tuple
from Utils.Singleton import Singleton
from pytsk3 import Img_Info, Volume_Info, FS_Info, Directory, File, \
    TSK_VS_PART_INFO, TSK_IMG_TYPE_EXTERNAL, TSK_FS_META_TYPE_DIR


class ImageHandler(Img_Info, metaclass=Singleton):
    def __init__(self, ) -> None:
        self.store = Store().image_store

        setrecursionlimit(100000)

        self.image_handle = None

        self.ext = PathlibPath(self.store.get_state()).suffix.lower()[1:]
        self.search_result = None

    def close(self) -> None:
        self.ewf_handle.close()
        self.logger.debug('Extension: ' + self.ext)

        if self.store.get_state() != 'initial':
            self.image_handle = Img_Info(self.store.get_state())

    def check_file_path(self) -> bool:
        image_path = PathlibPath(self.store.get_state())
        return image_path.is_file()

    def check_file(self) -> bool:
        try:
            self.info()
        except OSError:
            return False
        return True

    def info(self) -> Volume_Info:
        try:
            return Volume_Info(self.image_handle)
        except RuntimeError:
            return None

    def volume_info(self) -> List[Union[str, str]]:
        volume = self.info()

        volume_info = [
            'Volume information',
            '',
            '- Amount of partitions: {}'.format(volume.info.part_count)
        ]

        for part in volume:
            volume_info.append('')
            volume_info.append('- Partition address: {}'.format(part.addr))
            volume_info.append('- Partition start: {}'.format(part.start))
            volume_info.append(
                '- Partition length (relative): {}'.format(
                    part.start + part.len - 1))
            volume_info.append('- Partition length: {}'.format(part.len))
            volume_info.append(
                '- Partition description: {}'.format(
                    part.desc.decode('UTF-8')))

        return volume_info

    @staticmethod
    def rreplace(s: str, old: str, new: str) -> str:
        return (s[::-1].replace(old[::-1], new[::-1], 1))[::-1]

    @staticmethod
    def partition_check(part: TSK_VS_PART_INFO) -> bool:
        tables_to_ignore = ['Unallocated', 'Extended', 'Primary Table']
        decoded = part.desc.decode('UTF-8')

        return part.len > 2048 and not any(
            table for
            table in tables_to_ignore
            if table in decoded
        )

    def get_handle(self) -> Tuple[Volume_Info, Img_Info]:
        vol = self.info()
        img = self.image_handle

        return vol, img

    @staticmethod
    def open_fs_single_vol(img: Img_Info, path: str) -> Union[
        Tuple[FS_Info, Directory], Tuple[None, None]
    ]:
        try:
            fs = FS_Info(img)
            # noinspection PyArgumentList
            root = fs.open_dir(path=path)

            return fs, root
        except IOError:
            pass
            return None, None

        except RuntimeError:
            pass
            return None, None

    @staticmethod
    def open_fs(img: Img_Info, vol: Volume_Info, path: str,
                part: Volume_Info) -> \
            Union[Tuple[FS_Info, Directory], Tuple[None, None]]:
        try:
            fs = FS_Info(
                img, offset=part.start * vol.info.block_size)
            # noinspection PyArgumentList
            root = fs.open_dir(path=path)

            return fs, root
        except IOError:
            pass
            return None, None

        except RuntimeError:
            return None, None

    @staticmethod
    def nameless_dir(fs_object: File) -> bool:
        return not hasattr(fs_object, 'info') \
            or not hasattr(fs_object.info, 'name') or not hasattr(
                fs_object.info.name, 'name') or \
            fs_object.info.name.name.decode('UTF-8') in ['.', '..']

    def single_file(self, partition: int, path: str, filename: str,
                    hashing: bool = False) -> Union[str, File, None]:
        vol, img = self.get_handle()
        fs, root = None, None

        if vol is not None:
            all_partitions = [x for x in vol]
            part = all_partitions[partition]
            if self.partition_check(part):
                fs, root = self.open_fs(img, vol, path, part)
        else:
            fs, root = self.open_fs_single_vol(img, path)

        if fs is not None and root is not None:
            try:
                for fs_object in root:
                    if self.nameless_dir(fs_object):
                        continue
                    try:
                        file_name = fs_object.info.name.name.decode('UTF-8')
                        if file_name.lower() == filename.lower():
                            return self.hash_file(fs_object) if hashing else \
                                fs_object
                    except IOError:
                        pass
            except RuntimeError:
                pass

        return '' if hashing else None

    def files(self, search_str: str = None) -> \
            List[List[Union[str, datetime]]]:

        vol, img = self.get_handle()
        recursed_data = []

        # Open FS and Recurse
        if vol is not None:
            for part in vol:
                if self.partition_check(part):
                    fs, root = self.open_fs(img, vol, '/', part)
                    if fs is not None and root is not None:
                        data = self.recurse_files(part.addr, fs, root, [],
                                                  [], [''], search_str)
                        recursed_data.append(data)
        else:
            fs, root = self.open_fs_single_vol(img, '/')
            if fs is not None and root is not None:
                data = self.recurse_files(1, fs, root, [], [], [''],
                                          search_str)
                recursed_data.append(data)

        return recursed_data

    def recurse_files(self, part: int, fs: FS_Info,
                      root_dir: Directory,
                      dirs: List[Directory],
                      data: List[List[Union[str, datetime]]],
                      parent: List[str], search_str: str = None) -> \
            List[List[Union[str, datetime]]]:

        # print('Recurse')
        dirs.append(root_dir.info.fs_file.meta.addr)
        for fs_object in root_dir:
            # Skip '.', '..' or directory entries without a name.
            if self.nameless_dir(fs_object):
                continue
            try:
                file_name = fs_object.info.name.name.decode('UTF-8')
                file_path = '{}/{}'.format(
                    '/'.join(parent),
                    fs_object.info.name.name.decode('UTF-8'))
                try:
                    if fs_object.info.meta.type == \
                            TSK_FS_META_TYPE_DIR:
                        f_type = 'DIR'
                        file_ext = ''
                    else:
                        f_type = 'FILE'
                        file_ext = file_name.rsplit('.')[-1].lower() \
                            if '.' in file_name else ''
                except AttributeError:
                    continue

                if search_str is None or search(search_str,
                                                file_name,
                                                I) is not None:
                    size = fs_object.info.meta.size
                    create = self.convert_time(fs_object.info.meta.crtime)
                    change = self.convert_time(fs_object.info.meta.ctime)
                    modify = self.convert_time(fs_object.info.meta.mtime)

                    data.append(
                        ['PARTITION {}'.format(part), file_name, file_ext,
                         f_type, create, change, modify, size, file_path])

                if f_type == 'DIR':
                    parent.append(fs_object.info.name.name.decode('UTF-8'))
                    sub_directory = fs_object.as_directory()
                    inode = fs_object.info.meta.addr

                    # This ensures that we don't recurse into a directory
                    # above the current level and thus avoid circular loops.
                    if inode not in dirs:
                        self.recurse_files(part, fs, sub_directory,
                                           dirs, data, parent, search_str)
                    parent.pop(-1)

            except IOError:
                pass
        dirs.pop(-1)
        return data

    @staticmethod
    def hash_file(fs_object: File) -> str:
        offset = 0
        buff_size = 1024 * 1024
        size = getattr(fs_object.info.meta, "size", 0)

        sha256_sum = sha256()
        while offset < size:
            available_to_read = min(buff_size, size - offset)
            data = fs_object.read_random(offset, available_to_read)
            if not data:
                break

            offset += len(data)
            sha256_sum.update(data)
        return sha256_sum.hexdigest()

    @staticmethod
    def convert_time(ts: float) -> Union[str, datetime]:
        return '' if str(ts) == '0' else datetime.utcfromtimestamp(ts)


if __name__ == '__main__':
    store = Store()
    store.image_store.dispatch(
        {
            'type': 'set_image',
            'image': '/Users/Mies/Downloads/FAT.dd'
        }
    )

    ewf = ImageHandler()

    volume = ewf.info()

    menu_items = [
        ('Amount of partitions: {}'.format(volume.info.part_count), ''),
        ('', '')]

    print(ewf.files())
    print(ewf.volume_info())
    print("\n".join([x[0] + x[1] for x in menu_items]))