import pypff
import os
import csv
import sys
import argparse


# !!!!!!!!!!!!!!!!!!!!CONCEPT CODE!!!!!!

class EmailModule():


# opgeven waar de output (CSV lijsten) moeten worden weergegeven)
    output_directory = "C:\\shit"

# main functie moet het bestand openen enzo. Dit moet worden gekoppeld aan de image!
    def main(self, pst_file, report_name):


        pst_name = os.path.split(pst_file)[1]
        opst = pypff.file()
        opst.open(pst_file)
        root = opst.get_root_folder()
        self.folderTraverse(root)

    # output path maken voor de CSV bestanden.
    def makePath(file_name):

        return os.path.abspath(os.path.join(output_directory, file_name))

    #Door de mappen heenlopen  ! nog niet duidelijk hoe pypff door de mappen heen loopt.
    def folderTraverse(self, base):
        for folder in base.sub_folders:
            if folder.number_of_sub_folders:
                self.folderTraverse(folder)  # Blijft door de mappen heenlopen
            self.checkForMessages(folder)
            self.deletedMessages(folder)
            self.allSenders(folder)

    # Naar email berichten  zoeken. De emails gaan vervolgens in een lijst.
    def checkForMessages(self, folder):
        message_list = []
        for message in folder.sub_messages:
            message_dict = self.processMessage(message)
            message_list.append(message_dict)
            self.folderReport(message_list, folder.name)

    #lijst van deleted emails. Ik weet niet of "folder.deleted_messages" correct is voor pypff. Ben dit nog aan het uitzoeken.

    def deletedMessages(self, folder):
        deletedMessages_list = []
        for message in folder.deleted_messages:
            message_dict = self.processMessage(message)
            deletedMessages_list.append(message_dict)
            self.deletedMessagesReport(deletedMessages_list, folder.name)

    def allSenders(self, folder):
        Senders_list = []
        for message in folder.sub_messages:
            Senders_dict = self.processAllSenders(message)
            Senders_list.append(Senders_dict)
            self.allSendersReport(Senders_list, folder.name)


    #alle email adress verwerken
    def processAllSenders(self, message):
        return {
            "sender": message.sender_name,
            # dit moet dus email adress worden. Nog niet duidelijk of name gelijk staat aan email adres
        }

    def process_tabel(self, message):
        return {
            "delivery_time": message.delivery_time,
            "sender": message.sender_name,
            "subject": message.subject,
        }

    #berichten verwerken.
    def processMessage(self, message):
        delivery_time = ''
        return {
            "subject": message.subject,
            "sender": message.sender_name,
            "header": message.transport_headers,
            "body": message.plain_text_body,
            "creation_time": message.creation_time,
            "submit_time": message.client_submit_time,
            "delivery_time": message.delivery_time,
            "attachment_count": message.number_of_attachments,
        }

    #lijst van alle berichten (zonder gebruiker) met body en attachements.
    def folderReport(self, message_list, folder_name):
        if not len(message_list):
            return

        # CSV Report
        fout_path = self.makePath("folder_report_" + folder_name + ".csv")
        fout = open(fout_path, 'wb')
        header = ['creation_time', 'submit_time', 'delivery_time'
              ,'header','sender', 'subject','body', 'attachment_count']
        csv_fout = csv.DictWriter(fout, fieldnames=header, extrasaction='ignore')
        csv_fout.writeheader()
        csv_fout.writerows(message_list)
        fout.close()


    #lijst met gedelete emails
    def deletedMessagesReport(self, deletedMessages_list, folder_name):
        if not len(deletedMessages_list):
            return

        fout_path = self.makePath("folder_report_" + folder_name + ".csv")
        fout = open(fout_path, 'wb')
        header = ['creation_time', 'submit_time', 'delivery_time'
              ,'header','sender', 'subject','body', 'attachment_count']
        csv_fout = csv.DictWriter(fout, fieldnames=header, extrasaction='ignore')
        csv_fout.writeheader()
        csv_fout.writerows(deletedMessages_list)
        fout.close()


    def allSendersReport(self, Senders_list, folder_name ):
        """
        Deze functie zet alle gevonden emailadressen in een lijst
        :param Senders_list: Dit is de lijst die wordt gemaakt
        :param folder_name: Dit is de naam van de map waar de lijst wordt opgeslagen
        :return:
        """
        if not len(Senders_list):
            return

        fout_path = self.makePath("folder_report_" + folder_name + ".csv")
        fout = open(fout_path, 'wb')
        header = ['sender']
        csv_fout = csv.DictWriter(fout, fieldnames=header, extrasaction='ignore')
        csv_fout.writeheader()
        csv_fout.writerows(Senders_list)
        fout.close()



if __name__ == '__main__':


    parser = argparse.ArgumentParser()
    parser.add_argument('PST_FILE', help="PST File Format from Microsoft Outlook")
    parser.add_argument('OUTPUT_DIR', help="Directory of output for temporary and report files.")
    parser.add_argument('--title', help="title bla bla")
    args = parser.parse_args()

    output_directory = os.path.abspath(args.OUTPUT_DIR)

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)



