import os
from os import path
from pathlib import Path
import youtube_dl
import json
import PySimpleGUI as sg
import PIL
from PIL import Image
import urllib
import functions as fu


def create_gui():

    sg.theme('Dark Teal 11')

    col1 = [
        [sg.Text('', key='video_name', size=(40,4))],
        [sg.Text('', key='duration', size=(40,1))]
    ]

    layout = [[sg.Listbox(values='', size=(50, 25), enable_events=True, key='track_name'), sg.Button('Search',
               bind_return_key=True), sg.Button('Download'), sg.InputText(enable_events=True, key='folder'), sg.FolderBrowse()],
              [sg.Input('', key='search_field')],
              [sg.Image(r'', key='thumbnail'), sg.Column(col1)]
              ]

    window = sg.Window('Beat Saber Track Manager', layout, font='Courier 12').finalize()
    window.maximize()

    if path.exists('config.ini'):
        f = open('config.ini', 'r', encoding='utf-8')
        bs_path = f.read()
        print(bs_path)

        window['track_name'].update(fu.check_tracks(bs_path))  # window should be updated during the function, but gui.window doesn't work atm for some reason
        window.Refresh()

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':  # if user closes window or clicks cancel
            break

        if event == 'track_name':
            search = str(values['track_name'])  # The chosen folder
            search = search[search.find('(') + 1:search.find(
                '-') - 1]  # Cut the excess text from the folder name, based on ( and - symbols
            window['search_field'].update(search)
            window.Refresh()

        # When submit is pressed run youtubeDL script with the chosen folder

        if event == 'Search':
            ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s.%(ext)s'})

            info = ydl.extract_info('ytsearch:' + values['search_field'], download=False, ie_key='YoutubeSearch')
            info = info['entries'][0]  # TODO Turn this into if later on
            print(info)  # Print out the extracted video information for debug purposes
            print(info['title'])
            print(info['uploader'])
            #print(info['description'])
            print(info['duration'])  # Printed in seconds, convert this
            print(info['webpage_url'])
            print(info['thumbnail'])

            # Convert duration into mm:ss
            # Youtube seems to be off by a second from youtubedl, good enough I guess
            duration = str(int(info['duration'] / 60))
            duration = duration + ':' + str(info['duration'] % 60)

            urllib.request.urlretrieve(info['thumbnail'], 'thumbnail.png')
            img = PIL.Image.open('thumbnail.png')
            img = img.resize((360, 200))
            img.save('thumbnail.png')
            window['thumbnail'].update('thumbnail.png')
            window['video_name'].update(info['title'])
            window['duration'].update(duration)
            window.Refresh()

            #  build video.json, "loop":false fixed in a hacky way :D
            data_set = {'activeVideo':0,'videos':[{'title':info['title'],'author':info['uploader'],'description':info['description'],
                        'duration':duration,'URL':info['webpage_url'],'thumbnailURL':info['thumbnail'],'loop':'f' + 'alse','offset': 0,'videopath':info['title'] + '.mp4'}],'Count':1}

            # video.json debug
            print(json.dumps(data_set, ensure_ascii=False))

            #  save video.json, encoding is utf8 otherwise there will be problems with MVP
            with open('video.json', 'w', encoding='utf8') as outfile:
                json.dump(data_set, outfile, ensure_ascii=False)

        #  Download the video, when download button is pressed
        if event == 'Download':
            download = info['webpage_url']
            print(download)
            youtube_dl.YoutubeDL({'outtmpl': '%(title)s.%(ext)s'}).download([download]) #Outputs title.mp4

        if event == 'folder':

            f = open('config.ini', 'w', encoding='utf-8')
            f.writelines(values['folder'])
            f.close()

            window['track_name'].update(fu.check_tracks(values['folder']))
            window.Refresh()


    window.close()  # Don't forget to close your window!