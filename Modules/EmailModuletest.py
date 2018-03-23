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


pst_file = "C:\\shit\\bramchoufoer@hotmail.com.pst"
output_directory = "C:\\shit"

def main(pst_file):


    pst_name = os.path.split(pst_file)[1]
    file = pypff.file()
    file.open(pst_file)
    root = file.get_root_folder()
    print(root)
    folderTraverse(root)

def makePath(file_name):

    return os.path.abspath(os.path.join(output_directory, file_name))


def folderTraverse(base):


    for folder in base.sub_folders:

        if folder.number_of_sub_folders:
            folderTraverse(folder) # Call new folder to traverse:
        checkForMessages(folder)


def checkForMessages(folder):


    message_list = []
    message_list_notes = []

    for message in folder.sub_messages:
        message_dict = processMessage(message)
        message_dict_notes = processMessage(message)
        message_list.append(message_dict)
        message_list_notes.append(message_dict_notes)
    folderReport(message_list, folder.name)
    folderReport_sender(message_list, folder.name)
    folderReport_from_to(message_list_notes, folder.name)

    """

    message_listb = []
    for x in folder.sub_messages:
        message_dictb = processSender(message)
        message_listb.append(message_dictb)
    folderReportb(message_listb, folder.name)
    """


def processMessage(message):
    return {
        "subject": message.subject,
        "sender": message.sender_name,
        "header": message.transport_headers,
        "body": message.plain_text_body.decode(),
        "attachment_count": message.number_of_attachments,
    }
def processSender(message):
    return {
        "sender": message.sender_name,
    }


def folderReport(message_list, folder_name):
    # CSV Report
    fout_path = makePath("map_" + folder_name + ".csv")
    #fout = open(fout_path, 'w')
    with open (fout_path, 'w',  encoding="utf-8" ,newline='') as fout:
        header = ['from','date','delivered', 'to','sender', 'subject', 'body', 'attachment_count','header']

        for message in message_list:
            for head in header:
                if head not in message.keys():
                    message[head] = ""
            try:
                headers = message['header'].split('\n')
                for line in headers:
                    if 'Delivered-To: ' in line:
                        message['delivered'] = line
                    if 'Date: ' in line:
                        message['date'] = line
                    if 'From: ' in line:
                        message['from'] = line
                    if 'To: ' in line:
                        message['to'] = line
                    if 'Subject: ' in line:
                        message['subject'] = line

                del message['header']


            except Exception as e:

                continue

        try:
            csv_fout = csv.DictWriter(fout, fieldnames=header)
            csv_fout.writeheader()
            for x in message_list:
                csv_fout.writerow(x)

        except Exception as e:
            print(e)
            pass


def folderReport_sender(message_list, folder_name):
    # CSV Report
    fout_path = makePath("verzameling_emailadressen"+folder_name+".csv")
    # fout = open(fout_path, 'w')
    with open(fout_path, 'w', encoding="utf-8", newline='') as fout:
        header = ['from', 'date', 'delivered', 'to', 'sender', 'subject', 'body', 'attachment_count', 'header']

        for message in message_list:
            for head in header:
                if head not in message.keys():
                    message[head] = ""
            try:
                headers = message['header'].split('\n')
                for line in headers:
                    if 'Delivered-To: ' in line:
                        message['delivered'] = line
                    if 'Date: ' in line:
                        message['date'] = line
                    if 'From: ' in line:
                        message['from'] = line
                    if 'To: ' in line:
                        message['to'] = line
                    if 'Subject: ' in line:
                        message['subject'] = line
                del message['header']
                del message['attachment_count']
                del message['body']
                del message['subject']
                del message['delivered']
                del message['date']


            except Exception as e:
                print("Error in folderreport: {}".format(e))
                continue


        try:
            csv_fout = csv.DictWriter(fout, fieldnames=header)
            csv_fout.writeheader()
            for x in message_list:
                csv_fout.writerow(x)

        except Exception as e:
            print(e)
            pass
def folderReport_from_to(message_list_notes, folder_name):
    # CSV Report

    fout_path = makePath("notes_from_to"+folder_name+".csv")
    # fout = open(fout_path, 'w')
    with open(fout_path, 'w', newline='') as fout:
        header = ['from', 'date', 'delivered', 'to', 'sender', 'subject', 'body', 'attachment_count', 'header']

        for message in message_list_notes:
            for head in header:
                if head not in message.keys():
                    message[head] = ""
            try:
                headers = message['header'].split('\n')

                for line in headers:

                    if 'Date: ' in line:
                        message['date'] = line
                    if 'From: ' in line:
                        message['from'] = line
                    if 'To: ' in line:
                        message['to'] = line


                del message['header']
                del message['attachment_count']
                del message['body']
                del message['subject']
                del message['delivered']
                del message['sender']


            except Exception as e:
                print("Error in folderreport: {}".format(e))
                continue


        try:
            csv_fout = csv.DictWriter(fout, fieldnames=header)
            csv_fout.writeheader()
            for x in message_list_notes:
                csv_fout.writerow(x)

        except Exception as e:
            print(e)
            pass
"""
def merge_csv_addresses():
    files = [x for x in os.listdir('C:\\shit') if x.startswith('verzameling_emailadressen')]

    with open('C:\\shit\\Alle_Email_Adressen.csv', 'wb') as out:
        for x in files:
            f_path = os.path.join('C:\\shit', x)
            with open(f_path, 'rb') as f:
                out.write(f.read())

    for f in files:
        os.remove(os.path.join('C:\\shit', f))

def merge_csv_emails():
    files = [x for x in os.listdir('C:\\shit') if x.startswith('map_')]

    with open('C:\\shit\\Alle_Emails_body_subject.csv', 'wb') as out:
        for x in files:
            f_path = os.path.join('C:\\shit', x)
            with open(f_path, 'rb') as f:
                out.write(f.read())

    for f in files:
        if not "Verwijderde" in f:
            os.remove(os.path.join('C:\\shit', f))

def merge_csv_email_notes():
    files = [x for x in os.listdir('C:\\shit') if x.startswith('notes')]

    with open('C:\\shit\\Emails_from_to.csv', 'wb') as out:
        for x in files:
            f_path = os.path.join('C:\\shit', x)
            with open(f_path, 'rb') as f:
                out.write(f.read())

    for f in files:
            os.remove(os.path.join('C:\\shit', f))
"""

def merge_general(start, merge_into, dont_delete):
    files = [x for x in os.listdir('C:\\shit') if x.startswith(start)]

    with open('C:\\shit\\' + merge_into + '.csv', 'wb') as out:
        for x in files:
            f_path = os.path.join('C:\\shit', x)
            with open(f_path, 'rb') as f:
                out.write(f.read())

    for f in files:
        if dont_delete == None:
            os.remove(os.path.join('C:\\shit', f))
        else:
            if dont_delete not in f:
                os.remove(os.path.join('C:\\shit', f))


if __name__ == "__main__":

    output_directory = os.path.abspath(output_directory)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    main(pst_file)
    merge_general(start='verzameling_emailadressen', merge_into='Alle_Email_Adressen', dont_delete=None)
    merge_general(start='map_',merge_into='Alle_Emails_body_subject', dont_delete='Verwijderde')
    merge_general(start='notes',merge_into='Emails_from_to', dont_delete=None)
    #merge_csv_addresses()
    #merge_csv_emails()
    #merge_csv_email_notes()

