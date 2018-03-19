import os, os.path
import sys
import argparse
import logging
from Utils.Store import Store
from Utils.Ewf import Ewf
import pypff
import csv
from collections import Counter
import pathlib
import glob

"""
De code werkt, helaas worden niet alle mappen uit het .pst bestand gehaald. De mappen die tot nu toe worden geëxporteerd:
Postvak IN, Verwijderde items & ongewenste Email.
"""

pst_file = "C:\\shit\\bramchoufoer@hotmail.com.pst"
output_directory = "C:\\shit"

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
    print(root)
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
    message_list_sender = []
    for message in folder.sub_messages:
        message_dict = processMessage(message)
        message_dict_sender = processSender(message)
        message_list.append(message_dict)
        message_list_sender.append(message_dict_sender)
    folderReport(message_list, folder.name)
    folderReport_sender(message_list_sender, folder.name)

    """

    message_listb = []
    for x in folder.sub_messages:
        message_dictb = processSender(message)
        message_listb.append(message_dictb)
    folderReportb(message_listb, folder.name)
    """


def processMessage(message):
    """
    The processMessage function processes multi-field messages to simplify collection of information
    :param message: pypff.Message object
    :return: A dictionary with message fields (values) and their data (keys)
    """

    # print(message.plain_text_body)

    return {
        "subject": message.subject,
        "sender": message.sender_name,
        "header": message.transport_headers,
        "body": message.plain_text_body.decode,
        "attachment_count": message.number_of_attachments,
    }
def processSender(message):
    return {
        "sender": message.sender_name,
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
    fout_path = makePath("alle_emails" + folder_name + ".csv")
    #fout = open(fout_path, 'w')
    with open (fout_path, 'w', newline='') as fout:
        header= ['sender','subject','body','attachment_count', 'header']

        try:
            csv_fout = csv.DictWriter(fout, fieldnames=header)
            csv_fout.writeheader()
            for x in message_list:
                csv_fout.writerow(x)

        except Exception as e:
            print(e)
            pass

def folderReport_sender(message_list_sender, folder_name):
    """
    The folderReport function generates a report per PST folder
    :param message_list: A list of messages discovered during scans
    :folder_name: The name of an Outlook folder within a PST
    :return: None
    """
    if not len(message_list_sender):

        return

    # CSV Report
    fout_path = makePath("lijst_emailadressen" + folder_name + ".csv")
    #fout = open(fout_path, 'w')
    with open (fout_path, 'w', newline='') as fout:
        header = ['sender']

        try:
            csv_fout = csv.DictWriter(fout, fieldnames=header)
            csv_fout.writeheader()
            for x in message_list_sender:
                csv_fout.writerow(x)

        except Exception as e:
            pass


def merge_csv():
    files = [x for x in os.listdir('C:\\shit') if x.startswith('lijst_')]

    with open('C:\\shit\\Alle_Email_Adressen.csv', 'wb') as out:
        for x in files:
            f_path = os.path.join('C:\\shit', x)
            with open(f_path, 'rb') as f:
                out.write(f.read())



if __name__ == "__main__":

    output_directory = os.path.abspath(output_directory)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    main(pst_file)
    merge_csv()

