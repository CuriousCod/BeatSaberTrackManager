import os
from os import path
import youtube_dlc as youtube_dl
import json
import PySimpleGUI as sg
import PIL
from PIL import Image
import urllib
from tinytag import TinyTag
import webbrowser
import subprocess
import librosa
import audioread
import cv2
import requests
from bs4 import BeautifulSoup

# DONE Maybe implement best of three results ytsearch3 -> Not needed
# DONE Make sure the app doesn't download 10 hour videos! -> Limit is now 1.5x duration of the track or if over 900sec
# DONE Generate video.json
# DONE Enable youtubedl
# DONE Make file paths dynamic
# DONE Window references from functions.py don't work -> use global window
# DONE Display duration of the BS track
# DONE Duration seconds are not display with double digits, if seconds are less than 10
# DONE Download files to right folder
# DONE Set maximum character limit for description -> Max is now 106 characters
# DONE Make sure that .mp4 is the only output format with 720p preferred + audio - 6c79, 360b -> Added format
# TODO A lot of code cleaning
# DONE Implement a decent GUI -> Maybe ok now
# DONE Standardize folder format for searches '0000 (trackname - maker)' -> added to readme
# DONE Extra - symbols in folder names are an issue -> Using rfind now to find the last - symbol
# TODO Web interface? Will probably cause issues
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
# TODO Implement proper support for multiple video files
# DONE Video titles with unsupported symbols cause issues during download * / \ ? < > | -> Replace function
# DONE youtubeDL turns " into ' and : into  - -> Replace function
# DONE 2df2 crashes auto offset -> Offset tool not very successful, added try
# DONE Listbox chooses lowest option, if empty space clicked -> Feature, not a bug
# TODO Update video.json format to the next MVP version
# TODO Bad url in video.json crashes app, probably a lot more exceptions than just this
# TODO Try to reduce app size
# DONE Download audio and video separately -> Fixed by always merging mp4 with m4a
# TODO Check 3e24, there's some problem with the mp4 file
# DONE HTTP Error 429: Too Many Requests -> Added backup search
# TODO Catch Youtube SSL error CERTIFICATE_VERIFY_FAILED
# DONE Window resizing


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
        clear = ['track_name_and_author', 'track_duration', 'cover_image', 'video_name', 'video_duration', 'thumbnail',
                 'video_size', 'offset']

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
            my_file = values['bs_folder'] + '\\' + i + '\\video.json'
            if os.path.isfile(my_file):
                print('yes')
                yes_video.append(i)
            else:
                no_video.append(i)

        # Python doesn't have case/switch statement?!
        if values['track_filter'] == 'All tracks':
            window['tracklist'].update(both_video)
        elif values['track_filter'] == 'Tracks without video':
            window['tracklist'].update(no_video)
        elif values['track_filter'] == 'Tracks with video':
            window['tracklist'].update(yes_video)
    except OSError:
        print('CustomLevels folder is not valid!')
        sg.popup('CustomLevels folder is not valid.\nPlease select the CustomLevels folder from the file menu.')

    window.Refresh()


# Replace unsupported symbols from file names, uses same logic as youtubeDl
def replace_symbols(filename):
    # These symbols don't work on filenames and also ? " :
    ng_symbols = ['*', '/', '\\', '<', '>', '|']

    for i in ng_symbols:
        filename = filename.replace(i, '_')

    filename = filename.replace('?', '')
    filename = filename.replace(':', ' -')
    filename = filename.replace('\"', '\'')

    return filename


# Fetches and updates video.json to the newest format
def fetch_video_json(track_path):

    if os.path.isfile(track_path + '/video.json'):
        with open(track_path + '/video.json', 'r+',  encoding='utf8') as f:
            try:
                video_json = json.load(f)
                # Check if the json is in the new format, if not convert it
                # Currently only the active video in the json file is grabbed
                if 'videos' not in video_json:
                    video_json = {'activeVideo': 0, 'videos': [video_json]}

                av = video_json['activeVideo']  # Grab only the active video

                # Fix lowercase key
                if 'videopath' in video_json['videos'][av]:
                    video_json['videos'][av]['videoPath'] = video_json['videos'][av]['videopath']
                    del video_json['videos'][av]['videopath']

                # Clean unsupported symbols from from videoPath
                video_json['videos'][av]['videoPath'] = replace_symbols(video_json['videos'][av]['videoPath'])

                # Save video.json with the changes
                f.seek(0)  # Return to the beginning of the file
                json.dump(video_json, f, ensure_ascii=False)
                f.truncate()  # Clean old data from file

                return video_json

            #  Skip printing video info, if video.json is in weird format or empty
            except json.decoder.JSONDecodeError:
                print('video.json empty or not in proper format!')
                window['video_name'].update('video.json empty or not in proper format!')
                return False
    else:
        return False


# Updates track information when a track is selected from the list
def tracklist():
    event, values = window.read(timeout=0)

    global video_exists
    global track_path
    global track_seconds

    clear_info('')
    if not values['tracklist']:
        print('No tracks!')
    else:
        search = str(values['tracklist'])  # Chosen track
        track_path = values['bs_folder'] + '/' + search.replace('[\'', '').replace('\']', '').replace('"]', '').replace(
            '["', '')
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
            print('Missing info.dat or cover image!')
            track_seconds = 600
            window['track_name_and_author'].update('info.dat or cover image missing!')
            # clear_info(['cover_image', 'track_duration'])

        #  Reset fields and set duration to 600 seconds, if info.dat is in weird format or empty
        except json.decoder.JSONDecodeError:
            info_dat = False
            print('info.dat empty or not in proper format!')
            track_seconds = 600
            window['track_name_and_author'].update('info.dat empty or not in proper format!')
            # clear_info(['cover_image', 'track_duration'])

        # Grab video info
        video_json = fetch_video_json(track_path)
        if video_json is not False:
            av = video_json['activeVideo']  # Grab only the active video

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

            # Find video in folder and print info
            try:
                video_path = video_json['videos'][av]['videoPath']
                video_size = os.stat(track_path + '/' + video_path).st_size / 1000000

                # Grab video height
                # TODO This doesn't work on some videos, results show up as 0p
                cv2video = cv2.VideoCapture(track_path + '/' + video_path)
                video_height = cv2video.get(cv2.CAP_PROP_FRAME_HEIGHT)
                cv2.VideoCapture.release(cv2video)

                video_exists = True

                window['video_size'].update(
                    '{}{:.2f}{}{:.0f}p'.format('Video downloaded - ', video_size, ' MB - ', video_height), visible=True)

            except FileNotFoundError:
                print('Video not found!')
                video_exists = False
                window['video_size'].update('Video file not found in folder', visible=True)
        else:
            video_exists = False

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
def search_youtube():
    event, values = window.read(timeout=0)
    clear_info(['video_size', 'offset'])

    global info
    global video_path
    global data_set

    if not values['search_field']:
        print('Search field empty!')
        sg.popup('Please input a search term.\n')
    elif not values['tracklist']:
        print('No track selected!')
        sg.popup('Please select a track from the list.\n')
    else:
        try:
            # Run youtube search with youtubeDl
            ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s.%(ext)s'})
            # In some cases users might get HTTP Error 429 if they download too much
            # Since ytsearch doesn't support cookies this will result in a download error
            info = ydl.extract_info('ytsearch:' + values['search_field'], download=False)
            info = info['entries'][0]  # Grab only the first entry, in case the result is a playlist

        # This error should occur when video is not found or accessible, for example error 429
        except youtube_dl.utils.DownloadError:
            try:
                # If user has cookies file, run another search with beautiful soup, this can workaround the 429 error
                if os.path.exists('cookies.txt'):
                    print('Cookies are available, running another search with soup')
                    page = requests.get('https://www.youtube.com/results?search_query=' + values['search_field'].replace(' ', '+'))
                    soup = BeautifulSoup(page.content, 'html.parser')
                    soup = soup.find_all('script')

                    # Grab the video id from the search page
                    text = str(soup)  # Convert tag object in string, result 26 in tag object contains the video id
                    video_id = text.find('watch?') # Finding the first video result
                    video_id = text[video_id + 8:video_id + 19]
                    print('https://www.youtube.com/watch?v=' + video_id)

                    # Run normal youtubedl url extractor, this one supports cookies
                    ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s.%(ext)s', 'cookiefile': 'cookies.txt'})
                    info = ydl.extract_info('https://www.youtube.com/watch?v=' + video_id, download=False)
                else:
                    print('No video found or unable to download video!')
                    sg.popup('No video found or unable to download video\n')
                    return False

            except youtube_dl.utils.DownloadError:
                print('No video found or unable to download video!')
                sg.popup('No video found or unable to download video\n')
                return False

        # Print out the extracted video information for debug purposes
        print(info)
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

        # Shorten webpage url
        webpage_url = info['webpage_url'][info['webpage_url'].find('/watch'):-1]

        urllib.request.urlretrieve(info['thumbnail'], 'thumbnail.png')
        img = PIL.Image.open('thumbnail.png')
        img = img.resize((360, 200))
        img.save('thumbnail.png')
        window['thumbnail'].update('thumbnail.png')
        window['video_name'].update(info['title'])
        window['video_duration'].update(video_duration)
        window.Refresh()

        #  Build video.json, "loop":false fixed in a hacky way :D, limited description to 106 characters
        #  Unsupported symbols in Windows cause issues, running function to clean those up
        video_path = replace_symbols(info['title'])

        # Remove everything from thumbnail url starting from ? symbol
        thumbnail_url = info['thumbnail']
        if thumbnail_url.find('?') != -1:
            thumbnail_url = thumbnail_url[0:thumbnail_url.find('?')]
            print(thumbnail_url)

        # Dataset for video.json
        data_set = {'activeVideo': 0, 'videos': [
            {'title': info['title'], 'author': info['uploader'],
             'description': info['description'][0:106] + ' ...',
             'duration': video_duration, 'URL': webpage_url, 'thumbnailURL': thumbnail_url,
             'loop': 'f' + 'alse', 'offset': 0, 'videoPath': video_path + '.mp4'}], 'Count': 1}

        # video.json debug
        print(json.dumps(data_set, ensure_ascii=False))

        window['Download'].update(disabled=False)

        # TODO Fix file size grab and add resolution information
        # print(info)
        # video_size = int(info['formats'][0]['filesize']) #/ 1000000
        # window['video_size'].update('{:.2f}{}'.format(video_size, ' MB'), visible=True)
        window.Refresh()

        return True

#  Download the video, when download button is pressed
def download_video():
    event, values = window.read(timeout=0)
    av = data_set['activeVideo']

    if not values['tracklist']:
        print('No track selected!')
    elif not info:
        print('No video selected!')
    else:
        # Delete previous video
        try:
            if video_exists:
                os.remove(track_path + '/' + data_set['videos'][av]["videoPath"])
        except FileNotFoundError:
            print('Could not delete previous video.')
            sg.popup('Could not delete previous video.\nPlease delete it manually from the folder.')

        download = info['webpage_url']
        print(download)
        #  Display warning, if video is 1.5 times longer than the bs track
        #  TODO Add a confirmation window here
        #  If info.dat is missing, the limit is 900 seconds
        if info['duration'] > track_seconds * 1.5:
            print('Video is way longer than the track!')
            window['video_size'].update('Video is way longer than the track.', visible=True)
            window.Refresh()
            return False
        else:
            # Save video.json, encoding in utf8, otherwise there will be problems with MVP
            with open(track_path + '/video.json', 'w', encoding='utf8') as outfile:
                json.dump(data_set, outfile, ensure_ascii=False)
            # Download the video
            # TODO See if there is a way to overwrite previous video
            try:
                youtube_dl.YoutubeDL({'format': 'mp4[height>=480][height<1080]+bestaudio[ext=m4a]',
                                      'cookiefile':'cookies.txt',
                                      'outtmpl': track_path + '/%(title)s.%(ext)s'}).download(
                    [download])  # Outputs title + extension
            except youtube_dl.utils.DownloadError:
                print('Unable to download video format, lowering requirements.')
                youtube_dl.YoutubeDL({'format': 'mp4[height<=720]+bestaudio[ext=m4a]',
                                      'outtmpl': track_path + '/%(title)s.%(ext)s'}).download(
                    [download])
            try:
                av = data_set['activeVideo']

                #video_path = data_set['videos'][av]['videoPath']

                # Patchwork fix for bad symbols in filenames
                # The symbol replacement function is not enough in itself
                files = os.listdir(track_path + '/')
                for filename in files:
                    if filename.endswith('.mp4'):
                        with open(track_path + '/video.json', 'r', encoding='UTF-8') as f:
                            trackData = json.load(f)
                        if trackData['videos'][av]['videoPath'] != filename:
                            trackData['videos'][av]['videoPath'] = filename
                        with open(track_path + '/video.json', 'w', encoding='UTF-8') as f:
                            json.dump(trackData, f)

                video_size = os.stat(track_path + '/' + trackData['videos'][av]['videoPath']).st_size / 1000000

                cv2video = cv2.VideoCapture(track_path + '/' + trackData['videos'][av]['videoPath'])
                video_height = cv2video.get(cv2.CAP_PROP_FRAME_HEIGHT)
                cv2.VideoCapture.release(cv2video)

                window['video_size'].update(
                    '{}{:.2f}{}{:.0f}p'.format('Video downloaded - ', video_size, ' MB - ', video_height),
                    visible=True)
                window['Auto Offset'].update(disabled=False)
                window['offset'].update('{}{}'.format('Offset: ', data_set['videos'][0]['offset']),
                                        visible=True)
                return True

            except OSError:
                print('Could not grab video file size, probably because of a weird symbol in filename')
                window['video_size'].update('Video downloaded - File size not available', visible=True)
                return True


# Calculate audio/video offset using MVP's tools or librosa
def run_auto_offset(auto_offset):
    event, values = window.read(timeout=0)

    # Offset using MVP
    if auto_offset == 0:

        window['offset'].update('Calculating offset...', visible=True)
        window.Refresh()

        offset_tool = values['bs_folder'][0:values['bs_folder'].find('Beat Saber_Data')]
        offset_tool = '\"' + offset_tool + 'Youtube-dl/SyncVideoWithAudio/SyncVideoWithAudio.exe' + '\"' + ' offset'

        search = str(values['tracklist'])  # Chosen track
        track_path = values['bs_folder'] + '/' + search.replace('[\'', '').replace('\']', '').replace('"]',
                                                                                                      '').replace(
            '["', '')

        with open(track_path + '/info.dat', 'r', encoding='utf8') as outfile:
            track_json = json.load(outfile)
            offset_audio = ' \"' + track_path + '/' + track_json['_songFilename'] + '\"'
            print(offset_audio)

        with open(track_path + '/video.json', 'r', encoding='utf8') as outfile:
            video_json = json.load(outfile)
            av = video_json['activeVideo']
            offset_video = ' \"' + track_path + '/' + video_json['videos'][av]['videoPath'] + '\"'
            print(offset_video)

        try:
            offset = subprocess.run(offset_tool + offset_audio + offset_video, shell=True, capture_output=True,
                                    check=True, timeout=15)
            # Convert results to str and search the string for the result. There's probably an easier way for this.
            offset = str(offset)
            print(offset)
            offset = offset[offset.rfind('Results: ') + 8:offset.find(',', offset.rfind('Results: '))]
            print(offset)
            offset = int(float(offset))
            offset *= -1  # Values are flipped in video.json
            window['offset'].update('{}{}'.format('Offset: ', offset), visible=True)

            with open(track_path + '/video.json', 'r+', encoding='utf8') as outfile:
                json_offset = json.load(outfile)
                json_offset['videos'][av]['offset'] = offset

                outfile.seek(0)  # Return to the beginning of the file
                json.dump(json_offset, outfile, ensure_ascii=False)
                outfile.truncate()  # Clean old data from file

        except subprocess.CalledProcessError:
            window['offset'].update('Could not calculate offset', visible=True)
        except subprocess.TimeoutExpired:
            window['offset'].update('Could not calculate offset', visible=True)
        except ValueError:
            window['offset'].update('Could not calculate offset', visible=True)

    # Offset with librosa, usually faster
    elif auto_offset == 1:

        search = str(values['tracklist'])  # Chosen track
        track_path = values['bs_folder'] + '/' + search.replace('[\'', '').replace('\']', '').replace('"]',
                                                                                                      '').replace(
            '["', '')

        with open(track_path + '/info.dat', 'r', encoding='utf8') as outfile:
            track_name = json.load(outfile)
            track_name = track_path + '/' + track_name['_songFilename']
        with open(track_path + '/video.json', 'r', encoding='utf8') as outfile:
            track_video = json.load(outfile)
            av = track_video['activeVideo']
            track_video = track_path + '/' + track_video['videos'][av]['videoPath']

        try:
            y, sr = librosa.load(track_name, duration=8)
            track_onset = librosa.frames_to_time(librosa.onset.onset_detect(y=y))

            y, sr = librosa.load(track_video, duration=8)
            video_onset = librosa.frames_to_time(librosa.onset.onset_detect(y=y))

            print(track_onset[0] - video_onset[0])

            offset = int(round((track_onset[0] - video_onset[0]) * -1, 3) * 1000)
            print(offset)

            window['offset'].update('{}{}'.format('Offset: ', offset), visible=True)

            with open(track_path + '/video.json', 'r+', encoding='utf8') as outfile:
                json_offset = json.load(outfile)
                json_offset['videos'][av]['offset'] = offset

                outfile.seek(0)  # Return to the beginning of the file
                json.dump(json_offset, outfile, ensure_ascii=False)
                outfile.truncate()  # Clean old data from file

        except audioread.exceptions.NoBackendError:
            print('No audio track found in video. Are you missing ffmpeg.exe?')
            window['offset'].update('Video has no audio track.', visible=True)

        except IndexError:
            print('No onset found on audio track. Onset analyze duration might be too low.')
            window['offset'].update('No audio found.', visible=True)

        except FileNotFoundError:
            print('No video found!.')
            window['offset'].update('No video found.', visible=True)


# GUI loop
def create_GUI():
    sg.theme('Dark Teal 11')

    menu_def = [['File', ['Select CustomLevels Folder', 'Exit']],
                ['Settings', ['Use Normal Auto Offset', 'Use Fast Auto Offset            X']],
                ['Help', 'About'], ]

    menu_elem = sg.Menu(menu_def)

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
              [menu_elem],
              [sg.Combo(values=('All tracks', 'Tracks without video', 'Tracks with video'),
                        default_value='All tracks', enable_events=True, key='track_filter', size=(30, 1)),
                        sg.Text('Filter'), sg.InputText(size=(10, 1), key='filter', enable_events=True)],
              [sg.Listbox(values='', size=(50, 34), enable_events=True, key='tracklist',
                          right_click_menu=['&Right', ['Search Youtube', 'Open track folder', 'Automate']]), sg.Column(col1, vertical_alignment="top")],
              [sg.Text('Youtube Search Term:')],
              [sg.Input('', size=(50, 1), key='search_field')],
              [sg.Button('Search Youtube', bind_return_key=True),
               sg.Button('Download', disabled=True), sg.InputText(enable_events=True, key='bs_folder', visible=False),
               sg.Button('Auto Offset', disabled=True)]
              ]

    global window
    windowSize = (953, 783)  # Default window size
    window = sg.Window('Beat Saber Track Manager', layout, font='Courier 12', icon='BSTM.ico', size=(windowSize), resizable=True).finalize()

    # Check for config.ini
    config_bs_folder()
    auto_offset = 1  # Use fast auto offset as default

    while True:
        event, values = window.read(timeout=1000)
        if event == sg.WIN_CLOSED or event == 'Exit':  # if user closes window or clicks cancel
            if os.path.exists('cover.png'):
                os.remove('cover.png')

            if os.path.exists('thumbnail.png'):
                os.remove('thumbnail.png')
            break

        # Grab the text from the chosen listbox choice and paste it into searchbox in readable format.
        # Also grabs the data from the track's info.dat
        if event == 'tracklist':
            #info = None  # Clear video info from previous searches
            clear_info('')
            tracklist()

        # Run search with the search term, only grabs the 1st result
        if event == 'Search Youtube':
            search_youtube()

        #  Download the video, when download button is pressed
        if event == 'Download':
            download_video()

        # Calculate audio/video offset using MVP's tools or librosa
        if event == 'Auto Offset':
            run_auto_offset(auto_offset)

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
            except FileNotFoundError:
                print('No track selected')

        if event == 'Automate':
            if search_youtube():
                print('search success')
                if download_video():
                    print('dl success')
                    run_auto_offset(auto_offset)

        if event == 'Select CustomLevels Folder':
            trackfolder = sg.popup_get_folder('', title='Select CustomLevels folder',
                                              no_window=True, modal=True, keep_on_top=True)
            if not trackfolder:
                print('No folder selected!')
            else:
                clear_info('')
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

        if event == 'Use Normal Auto Offset':
            auto_offset = 0
            menu_def = [['File', ['Select CustomLevels Folder', 'Exit']],
                        ['Settings', ['Use Normal Auto Offset     X', 'Use Fast Auto Offset']],
                        ['Help', 'About'], ]
            menu_elem.Update(menu_def)

        if event == 'Use Fast Auto Offset':
            auto_offset = 1
            menu_def = [['File', ['Select CustomLevels Folder', 'Exit']],
                        ['Settings', ['Use Normal Auto Offset', 'Use Fast Auto Offset            X']],
                        ['Help', 'About'], ]
            menu_elem.Update(menu_def)

        if event == 'About':
            print(window.size)
            webbrowser.open('https://github.com/CuriousCod/BeatSaberTrackManager/tree/master')

        # Works perfectly when maximizing window, otherwise only updates when any action is taken in the window
        if windowSize != window.size:
            print(window.size)
            CurrentWindowSize = window.size
            TracksElementSize = (int(CurrentWindowSize[0] * 0.1) - 45, int(CurrentWindowSize[1] * 0.044))
            print(TracksElementSize)
            window['tracklist'].set_size(TracksElementSize)
            windowSize = window.size

    window.close()


create_GUI()
