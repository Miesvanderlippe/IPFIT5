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
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict


pst_file = "C:\\shit\\bramchoufoer@hotmail.com.pst"
output_directory = "C:\\shit"

def main(pst_file):


    pst_name = os.path.split(pst_file)[1]
    file = pypff.file()
    file.open(pst_file)
    root = file.get_root_folder()

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
        header = ['delivered', 'date', 'from', 'to', 'subject', 'sender', 'body', 'attachment_count', 'header']

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

def read_from_to():
    """
    with open("C:\\shit\\Emails_from_to.csv") as f:
        for line in f.readlines():
            for word in line.split(' '):
                if '@' in word:
                   replaced = word.replace('<','').replace('>', '')
    """
    columns = defaultdict(list)
    with open("C:\\shit\\Emails_from_to.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for(k,v) in row.items():
                if v != k:
                    columns[k].append(v)
    #print(columns["to"])
    froms= []
    for line in columns["from"]:
        for word in line.split(' '):
            if '@' in word:
                replaced = word.replace('<', '').replace('>', '').replace(r'"', '').strip()
                #print(replaced)
                froms.append(replaced)
                break
    tos = []
    for x in columns["to"]:
        for d in x.split(' '):
            if '@' in d:
                replaced2 = d.replace('<', '').replace('>', '').replace(r'"', '').strip()
                print(replaced2)
                tos.append(replaced2)
                break
    print(len(froms), len(tos))
    #return(froms, tos)
    combined= []

    for (f, t) in zip(froms, tos):
        combined.append({"from" : f,"to": t})

    fout_path = makePath("Gegevens_Graaf.csv")
    with open(fout_path, 'w') as fout:
        header = ['from','to']
        csv_fout = csv.DictWriter(fout, fieldnames=header)
        csv_fout.writeheader()
        for froms_to in combined:

            csv_fout.writerow(froms_to)

        '''
            "iets" : ....
        '''



def graph():
    fig = plt.figure(figsize=(40, 15))
    with open("C:\\shit\\Gegevens_Graaf.csv", 'rt') as f:
        f = csv.reader(f)
        headers = next(f)
        emails = [row for row in f]

    unique_emails = list(set([row[0] for row in emails if len(row) > 2]))
    id = list(enumerate(unique_emails))

    links = []
    print(emails)
    for row in emails:
        if len(row) > 1:
            links.append({row[0]: row[1]})

    G = nx.DiGraph(directed=True)
    email_node = []
    for row in id:
        email_node.append(row[0])

    G.add_nodes_from(email_node)

    for node in links:
        edges = list(node.items())
        G.add_edge(*edges[0])

    # nx.draw(G,with_labels=True)
    options = {
        'node_color': 'blue',
        'node_size': 200,
        'width': 2,
        'arrowstyle': '-|>',
        'arrowsize': 10,
    }
    nx.spectral_layout(G, dim=2, weight='weight', scale=0.1, center=None)
    nx.draw_networkx(G, arrows=True, **options)

    plt.show(G)
    # plt.savefig("C:\\shit\\Graaf.png", dpi=300)

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
    read_from_to()
    graph()
