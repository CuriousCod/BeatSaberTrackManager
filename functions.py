import GUI
import os
from os import path
from pathlib import Path


def check_tracks(bs_path):
    yes_video = []
    no_video = []
    x = 0

    tracks = os.listdir(bs_path)  # Make this dynamic
    for i in tracks:
        print(i)
        my_file = Path(bs_path + i + '\\video.json')
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

    f = open("no_video.txt", 'r', encoding='utf-8')

    lines = f.read().splitlines()
    f.close()
    for i in lines:
        name_start = i.find('(') + 1
        name_end = i.find('-') - 1
        print(i[name_start:name_end])
    return lines

