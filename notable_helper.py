#! python3
# notable_helper.py keeps notes from notable sync'd on phone without header data

import os, logging, pickle, zipfile, datetime, send2trash, shutil
logging.basicConfig(level=logging.DEBUG)

backup_folder = r'D:\Achive\_BACKUP\Notable'
backup_period = 14  #days
original_folder = r'A:\Google Drive\Notable\notes'
modified_folder = r'A:\Google Drive\Notable_phone\notes'


class Backup:
    def __init__(self, computer_folder, phone_folder, backup_folder):
        self.backup_folder = backup_folder
        self.computer_folder = computer_folder
        self.phone_folder = phone_folder
        self.backups = []

    def backup(self):
        #backups files, returns a tuple of the time of backup and the path to that backup
        date = datetime.datetime.now().strftime('%a%d%b')
        fileName = 'computerBackup_' + date
        path = os.path.join(self.backup_folder+ '\\' + os.path.basename(fileName) + '.zip')

        compZip = zipfile.ZipFile(path, 'w')
        for file in os.listdir(self.computer_folder):
            #print('compressing:' + file)
            zip_path = self.computer_folder + '\\' + file
            compZip.write(zip_path, file, compress_type=zipfile.ZIP_DEFLATED)
        compZip.close()

        time_path = (datetime.datetime.now(), path)
        self.backups.append(time_path)

        return time_path

    def delete_backup(self, backup):
        send2trash.send2trash(backup)

    def clean_backups(self, delta=14):
        #deletes backups older than delta days if there is more than delta other backups
        if len(self.backups) > delta:
            for backup in self.backups:
                backup_time = backup[0]
                backup_path = backup[1]

                if datetime.datetime.now().date() - datetime.timedelta(days=delta) > backup_time.date():
                    print(backup_path)
                    self.delete_backup(backup_path)



class Note:
    def __init__(self, note_path):
        self.title = None
        self.path = note_path
        self.date_modified = os.path.getmtime(self.path)
        self.content = open(note_path,encoding='utf-8').readlines()
        for header_name, header_value in self.read_header().items():
            setattr(self, header_name, header_value)


    def read_header(self):
        #returns a dictionary of the header data ('title', 'created', 'modified')
        headers = {}
        end_of_header = self.content[1:].index('---\n')+1
        #header_data['title'] = self.content[1].rstrip()
        for header_line in self.content[1:end_of_header]:
            split_point = header_line.find(' ')
            header_name, header_data = header_line[:split_point], header_line[split_point:]
            if header_name != 'modified':
                headers[header_name[:-1]] = header_data


        return headers

    def remove_header(self):
        if self.content[0] == '---' and self.content[4] == '---':
            self.read_header()
            new_content = self.content[5:]
            logging.debug(self.header_data['title'] + ': header removed')
            return new_content
        else:
            logging.debug(self.header_data['title'])

    def is_same(self, other_note):
        if self.content == other_note.content:
            return True
        else:
            return False

    def newest_version(self, other_note):
        #returns the most recently modified version of the note
        if os.path.getmtime(self.path) > os.path.getmtime(other_note.path):
            return self
        elif os.path.getmtime(self.path) < os.path.getmtime(other_note.path):
            return other_note
        else:
            raise newestNoteError

class newestNoteError(Exception):
    pass


class Notes:
    def __init__(self, folder):
        self.folder = folder
        self.notes = self.notes_in_folder()


    def notes_in_folder(self):
        #returns set of notes in folder
        notes_in_folder = set()
        for filename in os.listdir(self.folder):
            if filename.endswith('.md'):
                path= self.folder + '\\' + filename
                notes_in_folder.add(Note(path))
            else:
                logging.debug('file skipped: '+ filename)
        return notes_in_folder

    def add_new_notes(self):
        self.notes = self.notes.union(self.notes_in_folder())


class System:
    def __init__(self, computer_folder, phone_folder):
        self.phone_folder = phone_folder
        self.computer_folder = computer_folder
        self.phone_notes = Notes(phone_folder)
        self.computer_notes = Notes(computer_folder)

    def find_modified_notes(self):
        modified_notes = []
        for computer_note in self.computer_notes.notes:
            phone_note = next((find_same_note for find_same_note in self.phone_notes.notes if
                               find_same_note.title == computer_note.title), None)
            # see if both notes have identical content
            if not phone_note.is_same(computer_note):
                modified_notes.append((computer_note, phone_note))
        return modified_notes

    def replace_old_notes(self):
        unsynched_notes = self.find_modified_notes()

        for note_pair in unsynched_notes:
            computer_note = note_pair[0]
            phone_note = note_pair[1]
            newest = computer_note.newest_version(phone_note)
            if phone_note == newest:
                send2trash.send2trash(computer_note.path)
                logging.debug("DELETING: "+ computer_note.path)
                shutil.copy(phone_note.path, computer_note.path)
                logging.debug("COPYING: " + phone_note.path + ' to ' + computer_note.path)

            if computer_note == newest:
                send2trash.send2trash(phone_note)
                logging.debug("DELETING: " + phone_note.path)
                shutil.copy(computer_note.path, phone_note.path)
                logging.debug("COPYING: " + computer_note.path +'  to ' + phone_note.path)




if __name__ == '__main__':
    manager = System(original_folder, modified_folder)
    manager.replace_old_notes()





def load():
    if 'notable_helper.pickle' in os.listdir():
        with open('notable_helper.pickle', 'rb') as file:
            manager = pickle.load(file)

    else:
        manager = System(original_folder, modified_folder)


def save():
    with open('notable_helper.pickle', 'wb') as file:
        pickle.dump(manager, file)
