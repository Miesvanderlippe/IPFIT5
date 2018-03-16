from Interfaces.ModuleInterface import ModuleInterface
import zipfile
import tarfile
import csv
import os
from langdetect import detect

class FileModule(ModuleInterface):

    def __init__(self) -> None:
        super().__init__()

# aanmaken lijst waar bestandsnamen die zich in de containers bevinden naar worden weggeschreven
archievenlijst = []

# uitlezen van de zip archieven, deze vervolgens appenden aan de archievenlijst
def archieven_uitlezen():
    zips = zipfile.ZipFile("ziparchief.zip",'r')
   # print(zips.namelist)
    for item in zips.namelist():
        archievenlijst.append(item)
    # print(archievenlijst)
        tars = tarfile.open("tararchief.tar.gz", "r:gz")
        for tarinfo in tars:
            archievenlijst.append(tarinfo.name)

# Alle bestandsnamen wegschrijven naar een .csv op een nieuwe regel.
def archieflijst_wegschrijven():
    with open("archiefbestanden.csv", "w") as f:
        writer = csv.writer(f, delimiter="\n")
        writer.writerow(archievenlijst)

# taalbepalen met langcheck, file openen -> lezen en testen
def langcheck():
    file = open('taaltekstbestand.txt', 'r')
    text = file.read()
    file.close()
    test = detect(text)
    print(test)

# bestandsextensies uit paden halen en wegschrijven
def extensies_uit_paden():
    extensiepadlijst = []
extensiepadlijst  = [os.path.join(r,file) for r,d,f in os.walk("C:\\Users\\Y50\\Desktop\\IPFIT5") for file in f]
with open("bestandsextensies.csv", "w") as f:
    writer = csv.writer(f, delimiter="\n")
    writer.writerow(extensiepadlijst)


if __name__ == '__main__':
    archieven_uitlezen()
    archieflijst_wegschrijven()
    extensies_uit_paden()
    langcheck()
