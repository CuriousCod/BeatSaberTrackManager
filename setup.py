from setuptools import setup
from distutils.core import setup

setup(
    name='BeatSaberTrackManager',
    version='1.0.3',
    packages=[''],
    install_requires=['youtube_dlc', 'PySimpleGUI', 'Pillow', 'urllib3', 'tinytag', 'librosa', 'audioread', 'beautifulsoup4', 'opencv-python'],
    url='https://github.com/CuriousCod/BeatSaberTrackManager',
    license='',
    author='CuriousCod',
    author_email='',
    description='Lists all currently downloaded custom tracks and downloads video files for the MVP mod.',
    console=['BSTM.py']
)
