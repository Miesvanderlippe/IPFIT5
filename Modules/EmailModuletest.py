import os, os.path
import pypff
import csv
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import math
from Interfaces.ModuleInterface import ModuleInterface
from Utils.ImageHandler import ImageHandler
import pandas as pd

class EmailModuleTest(ModuleInterface):

    def __init__(self) -> None:
        super().__init__()
        self.imagehandling = ImageHandler()
        self._status = "Initialised"
        self._progress = 0
        self.pst_file = "C:\\shit\\bramchoufoer@hotmail.com.pst"
        self.output_directory = "C:\\shit"

    def progress(self) -> int:
        return self._progress

    def status(self) -> str:
        return self._status
        self._progress = 100
        #pst_file = "C:\\shit\\bramchoufoer@hotmail.com.pst"
        #output_directory = "C:\\shit"

    def run(self):
        output_directory = os.path.abspath(self.output_directory)
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        self.checkxls()
        self.main(self.pst_file)
        self.merge_csv_addresses()
        self.merge_csv_emails()
        self.merge_csv_email_notes()
        self.read_from_to()
        self.graph()
        self.convert_to_xls()
        self.del_csv()

    def checkxls(self):
        files = [x for x in os.listdir('C:\\shit')]
        for item in files:
            if item.endswith(".xlsx"):
                os.remove(os.path.join('C:\\shit', item))

    def main(self,pst_file):
        self.pst_name = os.path.split(pst_file)[1]
        self.file = pypff.file()
        self.file.open(self.pst_file)
        root = self.file.get_root_folder()

        self.folderTraverse(root)
        print("bestand inladen....")

    def makePath(self,file_name):

        return os.path.abspath(os.path.join(self.output_directory, file_name))

    def folderTraverse(self,base):

        for folder in base.sub_folders:

            if folder.number_of_sub_folders:
                self.folderTraverse(folder) # Call new folder to traverse:
            self.checkForMessages(folder)


    def checkForMessages(self,folder):

        message_list = []
        message_list_notes = []

        for message in folder.sub_messages:
            message_dict = self.processMessage(message)
            message_dict_notes = self.processMessage(message)
            message_list.append(message_dict)
            message_list_notes.append(message_dict_notes)
        self.folderReport(message_list, folder.name)
        self.folderReport_sender(message_list, folder.name)
        self.folderReport_from_to(message_list_notes, folder.name)
        print("Emails zoeken......")

    def processMessage(self,message):

        return {
            "subject": message.subject,
            "sender": message.sender_name,
            "header": message.transport_headers,
            "body": message.plain_text_body.decode(),
            "attachment_count": message.number_of_attachments,
        }

    def processSender(self,message):
        return {
            "sender": message.sender_name,
        }

    def folderReport(self,message_list, folder_name):

        fout_path = self.makePath("map_" + folder_name + ".csv")
        #fout = open(fout_path, 'w')
        with open (fout_path, 'w',  encoding="utf-8" ,newline='') as fout:
            header = ['from','date','delivered', 'to', 'subject', 'body', 'attachment_count']

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
                    del message['sender']


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

    def folderReport_sender(self,message_list, folder_name):

        fout_path = self.makePath("verzameling_emailadressen"+folder_name+".csv")
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

    def folderReport_from_to(self,message_list_notes, folder_name):

        fout_path = self.makePath("notes_from_to"+folder_name+".csv")
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

    def merge_csv_addresses(self):

        files = [x for x in os.listdir('C:\\shit') if x.startswith('verzameling_emailadressen')]
        with open('C:\\shit\\Alle_Email_Adressen.csv', 'wb') as out:
            for x in files:
                f_path = os.path.join('C:\\shit', x)
                with open(f_path, 'rb') as f:
                    out.write(f.read())

        for f in files:
            os.remove(os.path.join('C:\\shit', f))

    def merge_csv_emails(self):

        files = [x for x in os.listdir('C:\\shit') if x.startswith('map_')]

        with open('C:\\shit\\Alle_Emails_body_subject.csv', 'wb') as out:
            for x in files:
                f_path = os.path.join('C:\\shit', x)
                with open(f_path, 'rb') as f:
                    out.write(f.read())

        for f in files:
            if not "Verwijderde" in f:
                os.remove(os.path.join('C:\\shit', f))

    def merge_csv_email_notes(self):

        files = [x for x in os.listdir('C:\\shit') if x.startswith('notes')]
        with open('C:\\shit\\Emails_from_to.csv', 'wb') as out:
            for x in files:
                f_path = os.path.join('C:\\shit', x)
                with open(f_path, 'rb') as f:
                    out.write(f.read())

        for f in files:
                os.remove(os.path.join('C:\\shit', f))

    def read_from_to(self):

        print("Mergen......")
        columns = defaultdict(list)
        with open("C:\\shit\\Emails_from_to.csv") as f:
            reader = csv.DictReader(f)
            for row in reader:
                for(k,v) in row.items():
                    if v != k:
                        columns[k].append(v)

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
                    #print(replaced2)
                    tos.append(replaced2)
                    break
        #print(len(froms), len(tos))
        combined= []
        #xlslijst = []

        for (f, t) in zip(froms, tos):
            combined.append({"from" : f,"to": t})
           #xlslijst.append([f, t])

        fout_path = self.makePath("Gegevens_Graaf.csv")
        with open(fout_path, 'w') as fout:
            header = ['from', 'to']
            csv_fout = csv.DictWriter(fout, fieldnames=header)
            csv_fout.writeheader()
            for froms_to in combined:

                csv_fout.writerow(froms_to)

        #xslx_writer = XlsxWriter("JOHANNES")
        #xslx_writer.add_worksheet("SWAGMEISTER4000")

        #xslx_writer.write_headers("SWAGMEISTER4000", ['from', 'to'])
        #xslx_writer.write_items("SWAGMEISTER4000", xlslijst)

    def graph(self):

        print("Graaf maken.....")
        fig = plt.figure(figsize=(40, 15))
        with open("C:\\shit\\Gegevens_Graaf.csv", 'rt') as f:
            f = csv.reader(f)
            headers = next(f)
            emails = [row for row in f]

        unique_emails = list(set([row[0] for row in emails if len(row) > 2]))
        id = list(enumerate(unique_emails))

        links = []

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


        options = {
            'node_color': 'grey',
            'node_size': 200,
            'width': 1,
            'arrowstyle': '-|>',
            'arrowsize': 12,
        }

        pos = nx.spring_layout(G, k=5 / math.sqrt(G.order()), iterations=20)
        nx.draw_networkx(G, pos, arrows=True, **options, edge_color='r', with_labels=False)
        nx.draw_networkx_labels(G, pos, font_size=14)

        plt.axis('off')
        plt.savefig("C:\\shit\\Graaf.png", dpi=300)

        print("Alle CSV bestanden naar XLSX converten.......")

    def convert_to_xls(self):

        filename = 'C:\\shit\\Alle_Emails_body_subject.xlsx'
        with open(filename, 'w'):
            df_new = pd.read_csv('C:\\shit\\Alle_Emails_body_subject.csv')
            writer = pd.ExcelWriter(filename)
            df_new.to_excel(writer, index=False)
            writer.save()


        filename_two = 'C:\\shit\\Alle_Email_Adressen.xlsx'
        with open(filename_two, 'w', encoding="utf-8"):
            df_new = pd.read_csv('C:\\shit\\Alle_Email_Adressen.csv')
            writer = pd.ExcelWriter(filename_two)
            df_new.to_excel(writer, index=False)
            writer.save()


        filename_three = 'C:\\shit\\Emails_from_to.xlsx'
        with open(filename_three, 'w', encoding="utf-8"):
            df_new = pd.read_csv('C:\\shit\\Emails_from_to.csv')
            writer = pd.ExcelWriter(filename_three)
            df_new.to_excel(writer, index=False)
            writer.save()

        filename_four = 'C:\\shit\\map_Verwijderde items.xlsx'
        with open(filename_four, 'w', encoding="utf-8"):
            df_new = pd.read_csv('C:\\shit\\map_Verwijderde items.csv')
            writer = pd.ExcelWriter(filename_four)
            df_new.to_excel(writer, index=False)
            writer.save()

    def del_csv(self):
        files = [x for x in os.listdir('C:\\shit')]
        for item in files:
            if item.endswith(".csv"):
                os.remove(os.path.join('C:\\shit', item))

        print("Klaar...!")

if __name__ == "__main__":
    module = EmailModuleTest()
    module.run()
