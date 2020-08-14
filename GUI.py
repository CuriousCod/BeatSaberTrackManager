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
from tinytag import TinyTag


def create_gui():
    sg.theme('Dark Teal 11')

    col1 = [
        [sg.Text('', key='video_name', size=(40, 4))],
        [sg.Text('', key='video_duration', size=(40, 1))]
    ]

    col2 = [
        [sg.Text(size=(52,1), key='track_name')],
        [sg.Text(size=(52,1), key='track_author')],
        [sg.Text(size=(52,1), key='track_duration')],
        [sg.Image(key='cover_image')]
    ]

    layout = [[sg.Combo(values=('All', 'Tracks without video', 'Tracks with video'),
                        default_value='Tracks without video', enable_events=True, key='track_filter', size=(30, 1))],
              [sg.Listbox(values='', size=(50, 25), enable_events=True, key='tracklist'), sg.Column(col2)],
              [sg.Input('', key='search_field')],
              [sg.Button('Search', bind_return_key=True),
               sg.Button('Download'), sg.InputText(enable_events=True, key='folder'), sg.FolderBrowse()],
              [sg.Image(r'', key='thumbnail'), sg.Column(col1)]
              ]

    global window
    window = sg.Window('Beat Saber Track Manager', layout, font='Courier 12').finalize()

    if path.exists('config.ini'):
        f = open('config.ini', 'r', encoding='utf-8')
        window['folder'].update(f.read())
        fu.check_tracks()

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':  # if user closes window or clicks cancel
            break

        # Grab the text from the chosen listbox choice and paste it into searchbox in readable format.
        # Also grabs the data from the tracks info.dat
        if event == 'tracklist':
            search = str(values['tracklist'])  # Chosen track
            track_path = values['folder'] + '/' + search.replace('[\'', '').replace('\']', '').replace('"]', '').replace('["', '')
            with open(track_path + '/info.dat') as f:
                track_json = json.load(f)
                img = PIL.Image.open(track_path + '/' + track_json['_coverImageFilename'])
                img.thumbnail((200, 200))
                img.save('cover.png')
                f.close()
            tag = TinyTag.get(track_path + '/' + track_json['_songFilename'])

            # Convert duration into m:ss
            duration = str(int(tag.duration / 60))
            duration = duration + ':' + str(int(tag.duration % 60)).zfill(2)

            if Path(track_path + '/video.json').is_file():
                with open(track_path + '/video.json', encoding='utf8') as f:
                    video_json = json.load(f)
                    if 'videos' in video_json:  # Check if video.json has the new format
                        print('loli')
                        print(video_json['videos'][0]['title'])
                        print(video_json['videos'][0]['duration'])
                        print(video_json['videos'][0]['thumbnailURL'])
                        try:
                            urllib.request.urlretrieve(video_json['videos'][0]['thumbnailURL'], 'thumbnail.png')
                        except urllib.error.HTTPError:
                            urllib.request.urlretrieve('https://s.ytimg.com/yts/img/no_thumbnail-vfl4t3-4R.jpg', 'thumbnail.png')
                        img = PIL.Image.open('thumbnail.png')
                        img.thumbnail((360, 200))
                        img.save('thumbnail.png')
                        window['video_name'].update(video_json['videos'][0]['title'])
                        window['video_duration'].update(video_json['videos'][0]['duration'].replace('.', ':'))
                        window['thumbnail'].update('thumbnail.png')
                    else:
                        print(video_json['title'])
                        print(video_json['duration'])
                        print(video_json['thumbnailURL'])
                        try:
                            urllib.request.urlretrieve(video_json['thumbnailURL'], 'thumbnail.png')
                        except urllib.error.HTTPError:
                            urllib.request.urlretrieve('https://s.ytimg.com/yts/img/no_thumbnail-vfl4t3-4R.jpg', 'thumbnail.png')
                        img = PIL.Image.open('thumbnail.png')
                        img.thumbnail((360, 200))
                        img.save('thumbnail.png')
                        window['video_name'].update(video_json['title'])
                        window['video_duration'].update(video_json['duration'].replace('.', ':'))
                        window['thumbnail'].update('thumbnail.png')
                    f.close()
            else:
                window['video_name'].update('')
                window['video_duration'].update('')
                window['thumbnail'].update('')


            search = search[search.find('(') + 1:search.find(
                '-') - 1]  # Cut the excess text from the folder name, based on ( and - symbols
            window['cover_image'].update('cover.png')
            window['track_name'].update(track_json['_songName'])
            window['track_author'].update(track_json['_levelAuthorName'])
            window['track_duration'].update(duration)

            window['search_field'].update(search)
            window.Refresh()

        if event == 'Search':

            if values['search_field'] == '':
                continue
            else:
                ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s.%(ext)s'})

                info = ydl.extract_info('ytsearch:' + values['search_field'], download=False, ie_key='YoutubeSearch')
                info = info['entries'][0]  # TODO Turn this into if later on
                print(info)  # Print out the extracted video information for debug purposes
                print(info['title'])
                print(info['uploader'])
                # print(info['description'])
                print(info['duration'])  # Printed in seconds, convert this
                print(info['webpage_url'])
                print(info['thumbnail'])

                # Convert duration into mm:ss
                # Youtube seems to be off by a second from youtubedl, good enough I guess
                duration = str(int(info['duration'] / 60))
                duration = duration + ':' + str(info['duration'] % 60).zfill(2)

                urllib.request.urlretrieve(info['thumbnail'], 'thumbnail.png')
                img = PIL.Image.open('thumbnail.png')
                img = img.resize((360, 200))
                img.save('thumbnail.png')
                window['thumbnail'].update('thumbnail.png')
                window['video_name'].update(info['title'])
                window['video_duration'].update(duration)
                window.Refresh()

                #  build video.json, "loop":false fixed in a hacky way :D
                data_set = {'activeVideo': 0, 'videos': [
                    {'title': info['title'], 'author': info['uploader'], 'description': info['description'],
                     'duration': duration, 'URL': info['webpage_url'], 'thumbnailURL': info['thumbnail'],
                     'loop': 'f' + 'alse', 'offset': 0, 'videopath': info['title'] + '.mp4'}], 'Count': 1}

                # video.json debug
                print(json.dumps(data_set, ensure_ascii=False))

                #  save video.json, encoding is utf8 otherwise there will be problems with MVP
                with open('C:/Users/KonaKona/PycharmProjects/BeatSaberTrackManager/tracks/video.json', 'w', encoding='utf8') as outfile:
                    json.dump(data_set, outfile, ensure_ascii=False)
                    outfile.close()

        #  Download the video, when download button is pressed
        if event == 'Download':
            download = info['webpage_url']
            print(download)
            youtube_dl.YoutubeDL({'outtmpl': 'C:/Users/KonaKona/PycharmProjects/BeatSaberTrackManager/tracks/%(title)s.%(ext)s'}).download([download])  # Outputs title + extension

        if event == 'folder':
            f = open('config.ini', 'w', encoding='utf-8')
            f.writelines(values['folder'])
            f.close()
            fu.check_tracks()

        if event == 'track_filter':
            fu.check_tracks()

    window.close()  # Don't forget to close your window!0
