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
import subprocess

# TODO Maybe implement best of three results ytsearch3
# DONE Make sure the app doesn't download 10 hour videos! -> Limit is now 1.5x duration of the track or if over 900sec
# DONE Generate video.json
# DONE Enable youtubedl
# DONE Make file paths dynamic
# DONE Window references from functions.py don't work -> use global window
# DONE Display duration of the BS track
# DONE Duration seconds are not display with double digits, if seconds are less than 10
# DONE Download files to right folder
# DONE Set maximum character limit for description -> Max is now 106 characters
# TODO Make sure that .mp4 is the only output format
# TODO A lot of code cleaning
# DONE Implement a decent GUI -> Maybe ok now
# DONE Standardize folder format for searches '0000 (trackname - maker)' -> added to readme
# DONE Extra - symbols in folder names are an issue -> Using rfind now to find the last - symbol
# TODO Web interface?
# DONE Get rid of the txt files
# DONE Clean images from the folder after closing
# DONE Exception video.json exists, but is empty -> Added try
# DONE Exception info.dat missing, added try
# DONE Exception for missing data in json files (video.json, info.dat) -> Added try
# DONE Exception missing thumbnail from deleted video -> try, except
# DONE Exception Bring It On crashes search: This video requires payment to watch -> Added try
# DONE Quick filter for tracks
# TODO Add delete function
# DONE Easy way for user to read error log -> Using sg.popup
# DONE Add file size display
# TODO video.json with 2 or more videos might cause issues
# DONE Video titles with unsupported symbols cause issues during download * / \ : ? < > | -> Replace during display
# DONE youtubeDL turns " into ' -> Added replace
# TODO 2df2 crashes auto offset


# Verify if the browsed CustomLevels folder is valid and write the location to config.ini
def browse_bs_folder():
    event, values = window.read(timeout=0)
    if values['bs_folder'].find('CustomLevels') == -1:
        print('This is not the custom tracks folder!')
        window['tracklist'].update('')
        window['track_filter'].update(disabled=True)
        window['filter'].update(visible=False)
        window.Refresh()
        return False
    else:
        f = open('config.ini', 'w', encoding='utf-8')
        f.writelines(values['bs_folder'])
        f.close()
        window['track_filter'].update(disabled=False)
        window['filter'].update(visible=True)
        check_tracks()


# Check config.ini for the bs folder location
def config_bs_folder():
    event, values = window.read(timeout=0)
    if path.exists('config.ini'):
        f = open('config.ini', 'r', encoding='utf-8')
        verifyfolder = f.read()
        window['bs_folder'].update(verifyfolder)
        f.close()
        if verifyfolder.find('CustomLevels') == -1:
            print('This is not the custom tracks folder!')
            window['tracklist'].update('')
            window['track_filter'].update(disabled=True)
            window['filter'].update(visible=False)
            window.Refresh()
        else:
            check_tracks()


# Clears displayed info in the GUI
def clear_info(clear):

    if not clear:
        clear = ['track_name_and_author', 'track_duration', 'cover_image', 'video_name', 'video_duration', 'thumbnail', 'video_size', 'offset']

    for i in clear:
        window[i].update('')

    window['Auto Offset'].update(disabled=True)


# Read and print the CustomLevels folder
def check_tracks():
    event, values = window.read(timeout=0)

    global yes_video
    global no_video
    global both_video

    yes_video = []
    no_video = []
    both_video = []

    try:
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
    except OSError:
        print('CustomLevels folder is not valid!')
        sg.popup('CustomLevels folder is not valid.\nPlease select the CustomLevels folder from the file menu.')

    window.Refresh()


def create_gui():
    sg.theme('Dark Teal 11')

    menu_def = [['File', ['Select CustomLevels Folder', 'Exit']],
                ['Help', 'About'], ]

    col1 = [
        [sg.Text(size=(38,2), key='track_name_and_author')],
        [sg.Text(size=(38,1), key='track_duration')],
        [sg.Image(key='cover_image')],
        [sg.Text('', size=(38, 1))],  # Empty line
        [sg.Text('', key='video_name', size=(38, 2))],
        [sg.Text('', key='video_duration', size=(38, 1))],
        [sg.Image(r'', key='thumbnail')],
        [sg.Text('Video Downloaded - ', size=(38, 1), visible=False, key='video_size')],
        [sg.Text('Offset ', size=(38, 1), visible=False, key='offset')]
    ]

    layout = [
              [sg.Menu(menu_def)],
              [sg.Combo(values=('All tracks', 'Tracks without video', 'Tracks with video'),
                        default_value='All tracks', enable_events=True, key='track_filter', size=(30, 1)),
                        sg.Text('Filter'), sg.InputText(size=(10, 1), key='filter', enable_events=True)],
              [sg.Listbox(values='', size=(50, 34), enable_events=True, key='tracklist',
                          right_click_menu=['&Right', ['Search Youtube', 'Open track folder']]), sg.Column(col1)],
              [sg.Text('Youtube Search Term:')],
              [sg.Input('', size=(50, 1), key='search_field')],
              [sg.Button('Search Youtube', bind_return_key=True),
               sg.Button('Download', disabled=True), sg.InputText(enable_events=True, key='bs_folder', visible=False),
               sg.Button('Auto Offset', disabled=True)]
              ]

    global window
    window = sg.Window('Beat Saber Track Manager', layout, font='Courier 12').finalize()

    # Check for config.ini
    config_bs_folder()

    # These symbols don't work on filenames
    ng_symbols = ['*', '/', '\\', ':', '?', '<', '>', '|', ]

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':  # if user closes window or clicks cancel
            if os.path.exists('cover.png'):
                os.remove('cover.png')

            if os.path.exists('thumbnail.png'):
                os.remove('thumbnail.png')
            break

        # Grab the text from the chosen listbox choice and paste it into searchbox in readable format.
        # Also grabs the data from the track's info.dat
        if event == 'tracklist':
            info = None  # Clear video info from previous searches
            clear_info('')
            if not values['tracklist']:
                print('No tracks!')
            else:
                search = str(values['tracklist'])  # Chosen track
                track_path = values['bs_folder'] + '/' + search.replace('[\'', '').replace('\']', '').replace('"]', '').replace('["', '')
                try:
                    with open(track_path + '/info.dat', encoding='utf8') as f:
                        info_dat = True
                        track_json = json.load(f)
                        img = PIL.Image.open(track_path + '/' + track_json['_coverImageFilename'])
                        img.thumbnail((200, 200))
                        img.save('cover.png')
                        f.close()
                    tag = TinyTag.get(track_path + '/' + track_json['_songFilename'])
                    track_seconds = tag.duration  # Variable to check video length vs track length

                    # Convert duration into m:ss
                    track_duration = str(int(tag.duration / 60))
                    track_duration = track_duration + ':' + str(int(tag.duration % 60)).zfill(2)

                    # Update track fields
                    window['cover_image'].update('cover.png')
                    window['track_name_and_author'].update(
                        track_json['_songName'] + ' - ' + track_json['_levelAuthorName'])
                    # window['track_author'].update(track_json['_levelAuthorName'])
                    window['track_duration'].update(track_duration)

                #  Reset fields and set duration to 600 seconds, if info.dat is not found
                except FileNotFoundError:
                    info_dat = False
                    print('Missing info.dat file!')
                    track_seconds = 600
                    window['track_name_and_author'].update('info.dat missing!')
                    #clear_info(['cover_image', 'track_duration'])

                #  Reset fields and set duration to 600 seconds, if info.dat is in weird format or empty
                except json.decoder.JSONDecodeError:
                    info_dat = False
                    print('info.dat empty or not in proper format!')
                    track_seconds = 600
                    window['track_name_and_author'].update('info.dat empty or not in proper format!')
                    #clear_info(['cover_image', 'track_duration'])

                if Path(track_path + '/video.json').is_file():
                    with open(track_path + '/video.json', encoding='utf8') as f:
                        try:
                            video_json = json.load(f)
                            # Check if the json is in the new format, if not convert it
                            # Currently only the first video in the json file is grabbed
                            if 'videos' not in video_json:
                                video_json = {'activeVideo': 0, 'videos': [video_json]}

                            av = video_json['activeVideo']  # Grab only the active video

                            # Fix lowercase key
                            if 'videopath' in video_json['videos'][av]:
                                video_json['videos'][av]['videoPath'] = video_json['videos'][av]['videopath']
                                del video_json['videos'][av]['videopath']

                            print(video_json['videos'][av]['title'])
                            print(video_json['videos'][av]['duration'])
                            print(video_json['videos'][av]['thumbnailURL'])

                            # Find video thumbnail
                            try:
                                urllib.request.urlretrieve(video_json['videos'][av]['thumbnailURL'], 'thumbnail.png')
                            except urllib.error.HTTPError:
                                urllib.request.urlretrieve('https://s.ytimg.com/yts/img/no_thumbnail-vfl4t3-4R.jpg', 'thumbnail.png')
                            img = PIL.Image.open('thumbnail.png')
                            img.thumbnail((360, 200))
                            img.save('thumbnail.png')

                            # Update fields
                            window['video_name'].update(video_json['videos'][av]['title'])
                            window['video_duration'].update(video_json['videos'][av]['duration'].replace('.', ':'))
                            window['thumbnail'].update('thumbnail.png')
                            window['offset'].update('{}{}'.format('Offset: ', video_json['videos'][av]['offset']), visible=True)
                            window['Auto Offset'].update(disabled=False)

                            # Find video in folder
                            try:
                                video_path = video_json['videos'][av]['videoPath']
                                for i in ng_symbols:
                                    video_path = video_path.replace(i, '_')
                                video_size = os.stat(track_path + '/' + video_path).st_size / 1000000
                                window['video_size'].update('{}{:.2f}{}'.format('Video downloaded - ', video_size, ' MB'), visible=True)
                            except FileNotFoundError:
                                print('Video not found!')
                                window['video_size'].update('Video file not found in folder', visible=True)
                            f.close()

                        #  Skip printing video info, if video.json is in weird format or empty
                        except json.decoder.JSONDecodeError:
                            print('video.json empty or not in proper format!')
                            window['video_name'].update('video.json empty or not in proper format!')

                # If track contains proper info.dat, display track name and author on the search field
                if info_dat:
                    search = track_json['_songName'] + ' ' + track_json['_songAuthorName']
                # Otherwise cut the excess text from the folder name, based on ( and - symbols. Display on search field
                else:
                    search = search[search.find('(') + 1:search.rfind('-') - 1]
                window['search_field'].update(search)

                window['Download'].update(disabled=True)
                window.Refresh()

        # Run search with the search term, only grabs the 1st result
        if event == 'Search Youtube':
            clear_info(['video_size', 'offset'])

            if not values['search_field']:
                print('Search field empty!')
                sg.popup('Please input a search term.\n')
            elif not values['tracklist']:
                print('No track selected!')
                sg.popup('Please select a track from the list.\n')
            else:
                try:
                    ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s.%(ext)s'})

                    info = ydl.extract_info('ytsearch:' + values['search_field'], download=False, ie_key='YoutubeSearch')
                    info = info['entries'][0]  # Grab only the first entry, in case the result is a playlist
                    print(info)  # Print out the extracted video information for debug purposes
                    print(info['title'])
                    print(info['uploader'])
                    # print(info['description'])
                    print(info['duration'])  # Printed in seconds, convert this
                    print(info['webpage_url'])
                    print(info['thumbnail'])

                    # Convert duration into mm:ss
                    # Youtube seems to be off by a second from youtubedl, good enough I guess
                    video_duration = str(int(info['duration'] / 60))
                    video_duration = video_duration + ':' + str(info['duration'] % 60).zfill(2)

                    urllib.request.urlretrieve(info['thumbnail'], 'thumbnail.png')
                    img = PIL.Image.open('thumbnail.png')
                    img = img.resize((360, 200))
                    img.save('thumbnail.png')
                    window['thumbnail'].update('thumbnail.png')
                    window['video_name'].update(info['title'])
                    window['video_duration'].update(video_duration)
                    window.Refresh()

                    #  Build video.json, "loop":false fixed in a hacky way :D, limited description to 106 characters
                    #  Unsupported symbols in Windows cause issues, manually replace " - > ' in videoPath
                    data_set = {'activeVideo': 0, 'videos': [
                        {'title': info['title'], 'author': info['uploader'], 'description': info['description'][0:106] + ' ...',
                         'duration': video_duration, 'URL': info['webpage_url'], 'thumbnailURL': info['thumbnail'],
                         'loop': 'f' + 'alse', 'offset': 0, 'videoPath': info['title'].replace('\"', '\'') + '.mp4'}], 'Count': 1}

                    # video.json debug
                    print(json.dumps(data_set, ensure_ascii=False))

                    window['Download'].update(disabled=False)

                    # TODO Fix file size grab
                    #print(info)
                    #video_size = int(info['formats'][0]['filesize']) #/ 1000000
                    #window['video_size'].update('{:.2f}{}'.format(video_size, ' MB'), visible=True)
                    window.Refresh()

                except youtube_dl.utils.DownloadError:
                    print('No video found or unable to download video!')
                    sg.popup('No video found or unable to download video\n')

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
                if info['duration'] > track_seconds * 1.5:
                    print('Video is way longer than the track!')
                else:
                    #  Save video.json, encoding is utf8 otherwise there will be problems with MVP
                    with open(track_path + '/video.json', 'w', encoding='utf8') as outfile:
                        json.dump(data_set, outfile, ensure_ascii=False)
                        outfile.close()
                    #  Download the video
                    youtube_dl.YoutubeDL({'outtmpl': track_path + '/%(title)s.%(ext)s'}).download([download])  # Outputs title + extension
                    try:
                        video_path = data_set['videos'][0]['videoPath']
                        for i in ng_symbols:
                            video_path = video_path.replace(i, '_')
                        video_size = os.stat(track_path + '/' + video_path).st_size / 1000000
                        window['video_size'].update('{}{:.2f}{}'.format('Video downloaded - ', video_size, ' MB'),
                                                    visible=True)
                        #window['Auto Offset'].update(disabled=False)  # TODO track_json not updated during download
                        window['offset'].update('{}{}'.format('Offset: ', data_set['videos'][0]['offset']),
                                                visible=True)

                    except OSError:
                        print('Could not grab video file size, probably because of a weird symbol in filename')
                        window['video_size'].update('Video downloaded - File size not available', visible=True)

        # Calculate audio/video offset using the MVP's tools
        if event == 'Auto Offset':

            window['offset'].update('Calculating offset...', visible=True)
            window.Refresh()

            offset_tool = values['bs_folder'][0:values['bs_folder'].find('Beat Saber_Data')]
            offset_tool = '\"' + offset_tool + 'Youtube-dl/SyncVideoWithAudio/SyncVideoWithAudio.exe' + '\"' + ' offset'

            search = str(values['tracklist'])  # Chosen track
            track_path = values['bs_folder'] + '/' + search.replace('[\'', '').replace('\']', '').replace('"]', '').replace('["', '')

            offset_audio = ' \"' + track_path + '/' + track_json['_songFilename'] + '\"'  # TODO track_json not updated during download
            print(offset_audio)

            for i in ng_symbols:
                video_json['videos'][av]['videoPath'].replace(i, '_')
                offset_video = ' \"' + track_path + '/' + video_json['videos'][av]['videoPath'] + '\"'
            print(offset_video)

            offset = subprocess.run(offset_tool + offset_audio + offset_video, shell=True, capture_output=True)
            # Convert results to str and search the string for the result. There's probably an easier way for this.
            offset = str(offset)
            print(offset)
            offset = offset[offset.rfind('%') + 10:offset.find(',', offset.rfind('%') + 10)]
            print(offset)
            offset = int(float(offset))
            offset *= -1  # Values are flipped in video.json
            window['offset'].update('{}{}'.format('Offset: ', offset), visible=True)
            window['Auto Offset'].update(disabled=True)

        if event == 'bs_folder':
            browse_bs_folder()

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

        if event == 'Select CustomLevels Folder':
            trackfolder = sg.popup_get_folder('', title='Select CustomLevels folder',
                                              no_window=True, modal=True, keep_on_top=True)
            if not trackfolder:
                print('No folder selected!')
            else:
                clear_info()
                window['bs_folder'].update(trackfolder)
                browse_bs_folder()

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

            # Don't filter, if the filter has less than 3 characters
            if len(values['filter']) < 3:
                continue
            else:
                clear_info('')
                for i in filter_list:
                    if (values['filter']) in i.lower():
                        results.append(i)
                window['tracklist'].update(results)
                window.Refresh()

        if event == 'About':
            webbrowser.open('https://github.com/CuriousCod/BeatSaberTrackManager/tree/master')

    window.close()


create_gui()
