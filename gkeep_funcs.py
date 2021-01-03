from ipchecker import User
from gkeepapi import Keep
import base64


user = User()


def gkeep_login():
    keep = Keep()
    keep.login(user.gmail_address, base64.b64decode(user.gmail_password).decode('utf-8'))
    return keep


def delete_test_notes():
    keep = gkeep_login()
    for note in keep.all():
        if note.title == 'Test':
            note.delete()
            print('note deleted')
    keep.sync()


def get_labels():
    keep = gkeep_login()
    return [label.name for label in keep.labels()]


def new_label(label_name):
    keep = gkeep_login()
    if label_name not in get_labels():
        label = keep.createLabel(label_name)
        keep.sync()
        print('label added!')
        return label
    else:
        print('label exists!')
        return keep.findLabel(query=label_name)


def create_note(title='Test', text='Test note', label='test'):
    keep = gkeep_login()
    note = keep.createNote(title, text)
    note.labels.add(new_label(label))
    note.pinned = True
    keep.sync()
    return note


def delete_labels():
    keep = gkeep_login()
    for label in keep.labels():
        label.delete()
    keep.sync()

