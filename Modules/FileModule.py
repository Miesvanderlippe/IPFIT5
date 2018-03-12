from Interfaces.ModuleInterface import ModuleInterface
import zipfile
import tarfile


class FileModule(ModuleInterface):

    def __init__(self) -> None:
        super().__init__()

archievenlijst = []

def zips_uitlezen():
    zips = zipfile.ZipFile("ziparchief.zip",'r')
   # print(zips.namelist)
    for item in zips.namelist():
        archievenlijst.append(item)
    # print(archievenlijst)

def tars_uitlezen():
    tars = tarfile.open("tararchief.tar.gz", "r:gz")
    for tarinfo in tars:
        archievenlijst.append(tarinfo.name)
    print(archievenlijst)






if __name__ == '__main__':
    zips_uitlezen()
    tars_uitlezen()


