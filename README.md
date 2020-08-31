# BeatSaberTrackManager
An application to complement the MVP mod (https://github.com/rie-kumar/MusicVideoPlayer) for Beat Saber. Lists all downloaded custom tracks and allows downloading videos for the MVP mod without booting up Beat Saber. MVP video.json file generation and auto offset features are included.

<h3>Installation:</h3>

- Unzip release => run BSTM.exe
- To display tracks choose File => Select CustomLevels Folder => Choose your CustomLevels folder
- If you want to use fast auto offset (on by default), add a copy of ffmpeg.exe to the same folder as BSTM.exe

<h3>Notes:</h3>

- Video is downloaded with the following video/audio arguments: mp4[height<=720]+bestaudio[ext=m4a]
  - Audio is required for the auto offset feature
- Video and audio won't be merged to mkv, since MVP doesn't support mkv files and re-encoding has not been implemented
  - This means that in some rare cases the quality of the downloaded mp4 will be low, if there's no high resolution version of it available with m4a audio
- Application is currently adjusted for the MVP v1.10.0 version
- You can right click a track to quickly access the track's folder
- Auto offset has two options: fast and normal
  - Normal uses the same software as the one in MVP mod
    - Requires SyncVideoWithAudio.exe to be in \Beat Saber Folder\Youtube-dl\SyncVideoWithAudio\
  - Fast uses Python to quickly find the offset by comparing the audio onsets
    - ffmpeg is required for the fast auto offset
- Custom track folder naming should follow the same format as when downloaded with the More Songs mod:</br>
  - TrackID (TrackName - TrackMaker)</br>
  - 8149 (Great Days - Joetastic)
- If there are multiple videos downloaded for the track, the application picks the one set as active (activeVideo) in video.json. 
- If you encounter any bugs or have feature requests, create a new issue please

<h3>Developed with:</h3>

- Coded in Python using pyCharm
- Videos are downloaded with youtube-dl (https://youtube-dl.org)
- GUI implemented with PySimpleGUI (https://pysimplegui.readthedocs.io/en/latest/)
- Fast auto offset implemented with librosa (https://librosa.org/doc/latest/index.html)
- .exe created using PyInstaller
- Also using various other libraries for smaller tasks

![Preview image](https://www.dropbox.com/s/d9teb2xio3r2nsw/Screenshot%202020-08-24%2002.26.48.png?raw=1)

