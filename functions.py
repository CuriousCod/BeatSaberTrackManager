import GUI
import os
from os import path
from pathlib import Path


def check_tracks():
    event, values = GUI.window.read(timeout=0)

    yes_video = []
    no_video = []
    both_video = []

    tracks = os.listdir(values['folder'])
    for i in tracks:
        print(i)
        both_video.append(i)
        my_file = Path(values['folder'] + '\\' + i + '\\video.json')
        if my_file.is_file():
            print('yes')
            yes_video.append(i)
        else:
            no_video.append(i)

    """

    # Not needed, txt file stuff
    f = open('yes_video.txt', 'w', encoding='utf-8')
    yes_videos = map(lambda x: x + '\n', yes_video)
    f.writelines(yes_videos)
    f.close()

    # Not needed, txt file stuff
    f = open('no_video.txt', 'w', encoding='utf-8')
    no_videos = map(lambda x: x + '\n', no_video)
    f.writelines(no_videos
                 )
    f.close()

    """

    # Python doesn't have case/switch statement?!
    # This part ignores the txt files, they will be removed later completely
    if values['track_filter'] == 'All':
        GUI.window['tracklist'].update(both_video)
    elif values['track_filter'] == 'Tracks without video':
        GUI.window['tracklist'].update(no_video)
        #GUI.window['tracklist'].update(text_color='green')
    elif values['track_filter'] == 'Tracks with video':
        GUI.window['tracklist'].update(yes_video)

    """

    # Read both files and print the info into the listboxes
    # Not needed, txt file stuff
    f = open("no_video.txt", 'r', encoding='utf-8')
    lines = f.read().splitlines()
    f.close()

    # Debug stuff
    # Not needed, txt file stuff
    for i in lines:
        name_start = i.find('(') + 1
        name_end = i.find('-') - 1
        print(i[name_start:name_end])

    # Not needed, txt file stuff
    f = open("yes_video.txt", 'r', encoding='utf-8')
    lines = f.read().splitlines()
    f.close()

    """

    GUI.window.Refresh()
