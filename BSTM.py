import os
from os import path
from pathlib import Path
import youtube_dl
import json
import PySimpleGUI as sg
import PIL
from PIL import Image
import urllib
from tinytag import TinyTag
import webbrowser

# TODO Maybe implement best of three results ytsearch3
# DONE Make sure the app doesn't download 10 hour videos! -> Limit is now 1.5x duration of the track or if over 900sec
# DONE Generate video.json
# DONE Enable youtubedl
# DONE Make file paths dynamic
# DONE Window references from functions.py don't work -> use global window
# DONE Display duration of the BS track
# DONE Duration seconds are not display with double digits, if seconds are less than 10
# DONE Download files to right folder
# TODO Set maximum character limit for description
# TODO Make sure that .mp4 is the only output format
# TODO A lot of code cleaning
# DONE Implement a decent GUI -> Maybe ok now
# TODO Standardize folder format for searches '0000 (trackname - maker)'
# TODO Exception handling: no folder chosen, no video found
# DONE Extra - symbols in folder names are an issue -> Using rfind now to find the last -
# TODO Web interface?
# DONE Get rid of the txt files
# DONE Clean images from the folder after closing
# TODO Exception video.json exists, but is empty
# DONE Exception info.dat missing, added try
# TODO Exception for missing data in json files (video.json, info.dat)
# DONE Exception missing thumbnail from deleted video -> try, except
# TODO More advanced way to check that the bs folder is currently selected
# TODO Exception Bring It On crashes search: This video requires payment to watch
# DONE Quick filter for tracks
# TODO Add delete function
# TODO Easy way to read error log for user


def bs_folder():
    event, values = window.read(timeout=0)
    if values['bs_folder'].find('CustomLevels') == -1:
        print('This is not the custom tracks folder!')
        window['tracklist'].update('')
        window['track_filter'].update(disabled=True)
        window.Refresh()
    else:
        f = open('config.ini', 'w', encoding='utf-8')
        f.writelines(values['bs_folder'])
        f.close()
        window['track_filter'].update(disabled=False)
        check_tracks()


def check_tracks():
    event, values = window.read(timeout=0)

    global yes_video
    global no_video
    global both_video

    yes_video = []
    no_video = []
    both_video = []

    tracks = os.listdir(values['bs_folder'])
    for i in tracks:
        print(i)
        both_video.append(i)
        my_file = Path(values['bs_folder'] + '\\' + i + '\\video.json')
        if my_file.is_file():
            print('yes')
            yes_video.append(i)
        else:
            no_video.append(i)

    # Python doesn't have case/switch statement?!
    if values['track_filter'] == 'All tracks':
        window['tracklist'].update(both_video)
    elif values['track_filter'] == 'Tracks without video':
        window['tracklist'].update(no_video)
        #window['tracklist'].update(text_color='green')  # TODO this doesn't work
    elif values['track_filter'] == 'Tracks with video':
        window['tracklist'].update(yes_video)

    window.Refresh()


def create_gui():
    sg.theme('Dark Teal 11')

    col1 = [
     #   [sg.Text('', key='video_name', size=(40, 4))],
     #   [sg.Text('', key='video_duration', size=(40, 1))]
    ]

    menu_def = [['File', ['Select BS Folder', 'Exit']],
                ['Help', 'About'], ]

    col2 = [
        [sg.Text(size=(38,2), key='track_name_and_author')],
        #[sg.Text(size=(40,2), key='track_author')],
        [sg.Text(size=(38,1), key='track_duration')],
        [sg.Image(key='cover_image')],
        [sg.Text('', size=(38, 1))],  # Empty line
        [sg.Text('', key='video_name', size=(38, 2))],
        [sg.Text('', key='video_duration', size=(38, 1))],
        [sg.Image(r'', key='thumbnail')],
        [sg.Text('Video downloaded', size=(38, 1), visible=False, key='downloaded')]
    ]

    layout = [
              [sg.Menu(menu_def)],
              [sg.Combo(values=('All tracks', 'Tracks without video', 'Tracks with video'),
                        default_value='All tracks', enable_events=True, key='track_filter', size=(30, 1)),
                        sg.Text('Filter'), sg.InputText(size=(10, 1), key='filter', enable_events=True)],
              [sg.Listbox(values='', size=(50, 33), enable_events=True, key='tracklist',
                          right_click_menu=['&Right', ['Search', 'Open track folder']]), sg.Column(col2)],
              [sg.Text('Youtube Search Term:')],
              [sg.Input('', key='search_field')],
              [sg.Button('Search Youtube', bind_return_key=True),
               sg.Button('Download', disabled=True), sg.InputText(enable_events=True, key='bs_folder', visible=False)]
              #[sg.Image(r'', key='thumbnail'), sg.Column(col1)]
              ]

    global window
    window = sg.Window('Beat Saber Track Manager', layout, font='Courier 12').finalize()

    # Check config.ini for the bs folder location
    if path.exists('config.ini'):  # TODO Turn this into a function
        f = open('config.ini', 'r', encoding='utf-8')
        verifyfolder = f.read()
        window['bs_folder'].update(verifyfolder)
        f.close()
        if verifyfolder.find('CustomLevels') == -1:
            print('This is not the custom tracks folder!')
            window['tracklist'].update('')
            window['track_filter'].update(disabled=True)
            window.Refresh()
        else:
            check_tracks()

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':  # if user closes window or clicks cancel
            if os.path.exists('cover.png'):
                os.remove('cover.png')

            if os.path.exists('thumbnail.png'):
                os.remove('thumbnail.png')
            break

        # Grab the text from the chosen listbox choice and paste it into searchbox in readable format.
        # Also grabs the data from the tracks info.dat
        if event == 'tracklist':
            info = None  # Clear video info, from previous searches
            if not values['tracklist']:
                print('No tracks!')
            else:
                search = str(values['tracklist'])  # Chosen track
                track_path = values['bs_folder'] + '/' + search.replace('[\'', '').replace('\']', '').replace('"]', '').replace('["', '')
                try:
                    with open(track_path + '/info.dat', encoding='utf8') as f:
                        track_json = json.load(f)
                        img = PIL.Image.open(track_path + '/' + track_json['_coverImageFilename'])
                        img.thumbnail((200, 200))
                        img.save('cover.png')
                        f.close()
                    tag = TinyTag.get(track_path + '/' + track_json['_songFilename'])

                    # Convert duration into m:ss
                    duration = str(int(tag.duration / 60))
                    duration = duration + ':' + str(int(tag.duration % 60)).zfill(2)

                    # Update track fields
                    window['cover_image'].update('cover.png')
                    window['track_name_and_author'].update(
                        track_json['_songName'] + ' - ' + track_json['_levelAuthorName'])
                    # window['track_author'].update(track_json['_levelAuthorName'])
                    window['track_duration'].update(duration)

                #  Reset fields and set duration to 600 seconds, if info.dat is not found
                except FileNotFoundError:
                    print('Missing info.dat file!')
                    tag.duration = 600
                    window['cover_image'].update('')
                    window['track_name_and_author'].update('info.dat missing!')
                    window['track_duration'].update('')

                if Path(track_path + '/video.json').is_file():
                    window['downloaded'].update(visible=True)
                    with open(track_path + '/video.json', encoding='utf8') as f:
                        video_json = json.load(f)
                        if 'videos' in video_json:  # Check if video.json has the new format
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
                    window['downloaded'].update(visible=False)
                    window['video_name'].update('')
                    window['video_duration'].update('')
                    window['thumbnail'].update('')

                # Cut the excess text from the folder name, based on ( and - symbols. Display on the search field
                search = search[search.find('(') + 1:search.rfind('-') - 1]
                window['search_field'].update(search)

                window['Download'].update(disabled=True)
                window.Refresh()

        if event == 'Search Youtube':
            window['downloaded'].update(visible=False)

            if not values['search_field']:
                print('Search field empty!')
            elif not values['tracklist']:
                print('No track selected!')
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
                with open(track_path + '/video.json', 'w', encoding='utf8') as outfile:
                    json.dump(data_set, outfile, ensure_ascii=False)
                    outfile.close()

                window['Download'].update(disabled=False)
                window.Refresh()

        #  Download the video, when download button is pressed
        if event == 'Download':
            if not values['tracklist']:
                print('No track selected!')
            elif not info:
                print('No video selected!')
            else:
                download = info['webpage_url']
                print(download)
                #  Display warning, if video is 1.5 times longer than the bs track
                #  If info.dat is missing, the limit is 900 seconds
                if info['duration'] > tag.duration * 1.5:
                    print('Video is way longer than the track!')
                else:
                    youtube_dl.YoutubeDL({'outtmpl': track_path + '/%(title)s.%(ext)s'}).download([download])  # Outputs title + extension
                    window['downloaded'].update(visible=True)

        if event == 'bs_folder':
            bs_folder()

        if event == 'track_filter':
            check_tracks()

        if event == 'Open track folder':
            try:
                search = str(values['tracklist'])  # Chosen track
                track_path = values['bs_folder'] + '/' + search.replace('[\'', '').replace('\']', '').replace('"]', '').replace('["', '')
                print(track_path)
                os.startfile(track_path)
            except UnboundLocalError:
                print('No track selected')
                continue

        if event == 'Select BS Folder':
            trackfolder = sg.popup_get_folder('', title='Select CustomLevels folder',
                                              no_window=True, modal=True, keep_on_top=True)
            if not trackfolder:
                print('No folder selected!')
            else:
                window['bs_folder'].update(trackfolder)
                bs_folder()

        if event == 'filter':

            results = []

            if values['track_filter'] == 'All tracks':
                filter_list = both_video
            elif values['track_filter'] == 'Tracks without video':
                filter_list = no_video
            elif values['track_filter'] == 'Tracks with video':
                filter_list = yes_video

            if len(values['filter']) < 2:
                window['tracklist'].update(filter_list)

            # Don't search, if filter has less than 3 characters
            if len(values['filter']) < 3:
                continue
            else:
                for i in filter_list:
                    if (values['filter']) in i.lower():
                        results.append(i)
                window['tracklist'].update(results)
                window.Refresh()

        if event == 'About':
            print('nope')
            webbrowser.open('https://github.com/CuriousCod/BeatSaberTrackManager/tree/master')

    window.close()


create_gui()
