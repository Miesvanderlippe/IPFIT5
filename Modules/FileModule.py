from Interfaces.ModuleInterface import ModuleInterface
import zipfile
import tarfile
import csv
import os

class FileModule(ModuleInterface):

    def __init__(self) -> None:
        super().__init__()

# aanmaken lijst waar bestandsnamen die zich in de containers bevinden naar worden weggeschreven
archievenlijst = []

# uitlezen van de zip archieven, deze vervolgens appenden aan de archievenlijst
def zips_uitlezen():
    zips = zipfile.ZipFile("ziparchief.zip",'r')
   # print(zips.namelist)
    for item in zips.namelist():
        archievenlijst.append(item)
    # print(archievenlijst)

# uitlezen van de tar archieven, deze vervolgens appenden aan de archievenlijst
def tars_uitlezen():
    tars = tarfile.open("tararchief.tar.gz", "r:gz")
    for tarinfo in tars:
        archievenlijst.append(tarinfo.name)
    # print(archievenlijst)

# Alle bestandsnamen wegschrijven naar een .csv op een nieuwe regel.
def archieflijst_wegschrijven():
    with open("archiefbestanden.csv", "w") as f:
        writer = csv.writer(f, delimiter="\n")
        writer.writerow(archievenlijst)




if __name__ == '__main__':
    zips_uitlezen()
    tars_uitlezen()
    archieflijst_wegschrijven()

