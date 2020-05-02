#! python3
# notable_helper.py keeps notes from notable sync'd on phone without header data

import os, logging, pickle
logging.basicConfig(level=logging.DEBUG)


original_folder = r'A:\Google Drive\Notable\notes'
modified_folder = r'A:\Google Drive\Notable_phone'

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
            header_name, header_data = header_line[:split_point-1], header_line[split_point:]
            headers[header_name[:-1]] = header_data
        return headers

    def remove_header(self):
        if self.content[0] == '---' and self.content[4] == '---':
            self.read_header()
            new_content = self.content[5:]
            logging.debug(self.header_data['title'] + ': header removed')
            return new_content
        else:
            logging.debug(self.header_data['title'] )


class Notes:
    def __init__(self, folder):
        self.folder = folder
        self.notes = []

    def get_notes(self, folder):
        existing_notes = [note.title for note in self.notes]
        for filename in os.listdir(folder):
            if filename.endswith('.md') and filename.split('.')[0] not in existing_notes:
                path= self.computer_folder + '\\' + filename
                self.notes.append(Note(path))
            else:
                logging.debug('file skipped: '+ filename)



class System:
    def __init__(self, phone_folder, computer_folder):
        self.phone_folder = phone_folder
        self.computer_folder = computer_folder
        self.phone_notes = Notes(phone_folder)
        self.computer_notes = Notes(computer_folder)


if __name__ == '__main__':
    if 'notable_helper.pickle' in os.listdir():
        with open('notable_helper.pickle', 'rb') as file:
            manager = pickle.load(file)
    else:
        manager = System(original_folder, modified_folder)

    with open('notable_helper.pickle', 'wb') as file:
        pickle.dump(manager, file)