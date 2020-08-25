# BeatSaberTrackManager
Lists all downloaded custom tracks and allows downloading videos for the MVP(https://github.com/rie-kumar/MusicVideoPlayer) mod without booting up Beat Saber. MVP video.json file generation and auto offset are included.  

Notes:
- Application is currently adjusted for the MVP v1.10.0 version. 
- Auto offset has two options: fast and normal
  - Normal is the same the one in MVP mod
  - Fast uses python to quickly find the offset by comparing the audio onsets
    - ffmpeg is required for the fast auto offset. You can right click a track to quickly access the track's folder.
- Custom track folder naming should follow the same format as when downloaded with the More Songs mod:</br>
  - TrackID (TrackName - TrackMaker)</br>
  - 8149 (Great Days - Joetastic)
- Applicaton currently supports only one video at a time. If multiple videos are in the folder the application picks the one set as active(activeVideo) in video.json.

Installation:
- Unzip release, run BSTM.exe
- To display tracks choose File -> Select CustomLevels Folder -> Choose your CustomLevels folder
- If you want to use fast auto offset, add a copy of ffmpeg.exe to the same folder as BSTM.exe.

Developed with:
- Coded in Python using pyCharm.
- Videos are downloaded with youtube-dl (https://youtube-dl.org)
- GUI implemented with PySimpleGUI (https://pysimplegui.readthedocs.io/en/latest/)
- Auto Offset implemented with librosa (https://librosa.org/doc/latest/index.html)
- .exe created using PyInstaller
- Also using various other libraries for smaller tasks.

![Preview image](https://www.dropbox.com/s/d9teb2xio3r2nsw/Screenshot%202020-08-24%2002.26.48.png?raw=1)

