import os
import sys
import argparse
import logging


import pypff

import csv
from collections import Counter


pst_file = "C:\\shit\\testende59@gmail.com.pst"
output_directory = "C:\\shit"
 # ik kom niet uit de volgende bug:
"""
"C:\Program Files\Python36\python.exe" C:/Users/Bram/Documents/IPFIT5/Modules/EmailModuletest.py
Traceback (most recent call last):
  File "C:/Users/Bram/Documents/IPFIT5/Modules/EmailModuletest.py", line 133, in <module>
    main(pst_file)
  File "C:/Users/Bram/Documents/IPFIT5/Modules/EmailModuletest.py", line 32, in main
    folderTraverse(root)
  File "C:/Users/Bram/Documents/IPFIT5/Modules/EmailModuletest.py", line 51, in folderTraverse
    folderTraverse(folder) # Call new folder to traverse:
  File "C:/Users/Bram/Documents/IPFIT5/Modules/EmailModuletest.py", line 52, in folderTraverse
    checkForMessages(folder)
  File "C:/Users/Bram/Documents/IPFIT5/Modules/EmailModuletest.py", line 66, in checkForMessages
    folderReport(message_list, folder.name)
  File "C:/Users/Bram/Documents/IPFIT5/Modules/EmailModuletest.py", line 104, in folderReport
    csv_fout.writerows(message_list)
  File "C:\Program Files\Python36\lib\csv.py", line 158, in writerows
    return self.writer.writerows(map(self._dict_to_list, rowdicts))
  File "C:\Program Files\Python36\lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
UnicodeEncodeError: 'charmap' codec can't encode characters in position 69-70: character maps to <undefined>

zie functie folderReport
"""


def main(pst_file):
    """
    The main function opens a PST and calls functions to parse and report data from the PST
    :param pst_file: A string representing the path to the PST file to analyze
    :param report_name: Name of the report title (if supplied by the user)
    :return: None
    """

    pst_name = os.path.split(pst_file)[1]
    file = pypff.file()
    file.open(pst_file)
    root = file.get_root_folder()


    folderTraverse(root)

def makePath(file_name):
    """
    The makePath function provides an absolute path between the output_directory and a file
    :param file_name: A string representing a file name
    :return: A string representing the path to a specified file
    """
    return os.path.abspath(os.path.join(output_directory, file_name))


def folderTraverse(base):
    """
    The folderTraverse function walks through the base of the folder and scans for sub-folders and messages
    :param base: Base folder to scan for new items within the folder.
    :return: None
    """
    for folder in base.sub_folders:
        if folder.number_of_sub_folders:
            folderTraverse(folder) # Call new folder to traverse:
        checkForMessages(folder)


def checkForMessages(folder):
    """
    The checkForMessages function reads folder messages if present and passes them to the report function
    :param folder: pypff.Folder object
    :return: None
    """

    message_list = []
    for message in folder.sub_messages:
        message_dict = processMessage(message)
        message_list.append(message_dict)
    folderReport(message_list, folder.name)


def processMessage(message):
    """
    The processMessage function processes multi-field messages to simplify collection of information
    :param message: pypff.Message object
    :return: A dictionary with message fields (values) and their data (keys)
    """
    return {
        "subject": message.subject,
        "sender": message.sender_name,
        "header": message.transport_headers,
        "body": message.plain_text_body,
        #"creation_time": message.creation_time,
        #"submit_time": message.client_submit_time,
        #"delivery_time": message.delivery_time,
        "attachment_count": message.number_of_attachments,
    }


def folderReport(message_list, folder_name):
    """
    The folderReport function generates a report per PST folder
    :param message_list: A list of messages discovered during scans
    :folder_name: The name of an Outlook folder within a PST
    :return: None
    """
    if not len(message_list):

        return

    # CSV Report
    fout_path = makePath("folder_report_" + folder_name + ".csv")
    fout = open(fout_path, 'w')
    header = ['subject', 'sender','header','body', 'attachment_count']
    csv_fout = csv.DictWriter(fout, fieldnames=header, extrasaction='ignore')
    csv_fout.writeheader()
    csv_fout.writerows(message_list)
    fout.close()

if __name__ == "__main__":

    output_directory = os.path.abspath(output_directory)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    main(pst_file)

