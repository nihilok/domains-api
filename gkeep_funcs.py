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
        if 'test' in [label.name for label in note.labels.all()]:
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
        print('new label added!')
        return label
    else:
        print('label exists')
        return keep.findLabel(query=label_name)


def create_note(title='Test', text='Test note', label='test'):
    keep = gkeep_login()
    note = keep.createNote(title, text)
    note.labels.add(new_label(label))
    note.pinned = True
    keep.sync()
    print('note created')
    return note


def delete_all_labels():
    keep = gkeep_login()
    for label in keep.labels():
        label.delete()
    keep.sync()


def delete_label(name):
    keep = gkeep_login()
    label = keep.findLabel(query=name)
    if label:
        label.delete()
        keep.sync()
        print(f'label "{name}" deleted')
    else:
        print(f'label with name "{name}" does not exist')


if __name__ == "__main__":
    delete_test_notes()
