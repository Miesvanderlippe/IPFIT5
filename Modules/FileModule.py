from Interfaces.ModuleInterface import ModuleInterface
from langdetect import detect
from Utils.Ewf import Ewf
from Utils.Store import Store
import zipfile
import tarfile
import csv
import os
import sys

class FileModule(ModuleInterface):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def write_csv(data, output):
        if not data:
            return

        with open(output, 'w',encoding="utf-8") as csvfile:
            csv_writer = csv.writer(csvfile)
            headers = ['Partition', 'File', 'File Ext', 'File Type',
                       'Create Date', 'Modify Date', 'Change Date', 'Size',
                       'File Path', 'Hash']
            csv_writer.writerow(headers)
            for result_list in data:
                csv_writer.writerows(result_list)



# aanmaken lijst waar bestandsnamen die zich in de containers bevinden naar worden weggeschreven
archievenlijst = []


# # uitlezen van de zip archieven, deze vervolgens appenden aan de archievenlijst
# def archieven_uitlezen():
#     zips = zipfile.ZipFile("ziparchief.zip",'r')
#    # print(zips.namelist)
#     for item in zips.namelist():
#         archievenlijst.append(item)
#     # print(archievenlijst)
#         tars = tarfile.open("tararchief.tar.gz", "r:gz")
#         for tarinfo in tars:
#             archievenlijst.append(tarinfo.name)
#
# # Alle bestandsnamen wegschrijven naar een .csv op een nieuwe regel.
# def archieflijst_wegschrijven():
#     with open("archiefbestanden.csv", "w") as f:
#         writer = csv.writer(f, delimiter="\n")
#         writer.writerow(archievenlijst)
#
# # taalbepalen met langcheck, file openen -> lezen en testen
# def langcheck():
#     file = open('taaltekstbestand.txt', 'r')
#     text = file.read()
#     file.close()
#     test = detect(text)
#     print(test)
#
# # bestandsextensies uit paden halen en wegschrijven
# def extensies_uit_paden():
#     extensiepadlijst = []
# extensiepadlijst  = [os.path.join(r,file) for r,d,f in os.walk() for file in f]
# with open("bestandsextensies.csv", "w") as f:
#     writer = csv.writer(f, delimiter="\n")
#     writer.writerow(extensiepadlijst)


if __name__ == '__main__':
    module = FileModule()

    store = Store()
    store.image_store.dispatch(
        {
            'type': 'set_image',
            'image': 'C:\\Studie\\ipfit5\\lubuntu.dd'
        }
    )

    ewf = Ewf()
data = ewf.files()
#FileModule.write_csv(data, "b.csv")



#archieven_uitlezen()
#archieflijst_wegschrijven()
#extensies_uit_paden()
#langcheck()
