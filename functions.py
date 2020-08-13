import GUI
import os
from os import path
from pathlib import Path


def check_tracks():
    event, values = GUI.window.read(timeout=0)

    yes_video = []
    no_video = []

    tracks = os.listdir(values['folder'])
    for i in tracks:
        print(i)
        my_file = Path(values['folder'] + '\\' + i + '\\video.json')
        if my_file.is_file():
            print('yes')
            yes_video.append(i)
        else:
            no_video.append(i)

    f = open('yes_video.txt', 'w', encoding='utf-8')
    yes_video = map(lambda x: x + '\n', yes_video)
    f.writelines(yes_video)
    f.close()

    f = open('no_video.txt', 'w', encoding='utf-8')
    no_video = map(lambda x: x + '\n', no_video)
    f.writelines(no_video)
    f.close()

    # Read both files and print the info into the listboxes
    f = open("no_video.txt", 'r', encoding='utf-8')
    lines = f.read().splitlines()
    f.close()
    for i in lines:
        name_start = i.find('(') + 1
        name_end = i.find('-') - 1
        print(i[name_start:name_end])

    GUI.window['tracklist_novideo'].update(lines)

    f = open("yes_video.txt", 'r', encoding='utf-8')
    lines = f.read().splitlines()
    f.close()

    GUI.window['tracklist_yesvideo'].update(lines)
    GUI.window.Refresh()
