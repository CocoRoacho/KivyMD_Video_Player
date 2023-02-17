# KivyMD_Video_Player
A videoplayer with standard functionality, a playlist and some buttons for deleting or moving the current videofiles straight from the screen. 
Project is realized with Python, Kivy, KivyMD, ffmpeg and Send2Trash. 
It is Based on a video from Youtube Channel KivyMD: https://www.youtube.com/watch?v=v8e-ukTAg5o

The player itself has a controlboard with usual buttons like play, stop, pause, next, previous, Fullscreen on/off, volume slider, interactive progressbar, etc.
When you click in the left half or in the right half of the videoscreen you can move back or forward for a random amount of seconds.
It also has a (hideable) Sideboard with button for loading video, show information, delete or move current video to other location.
There's also a working Playlist, you can load single movies or whole directories to the playlist. I also implemented a drag-and-drop functionality.
You can shuffle the playlist, or store playlist in a json-file for later.

The loading of the playlist is very slow, the reason is that there will be a preview picture for every playlist item, ffmpeg needs some time to extract this.
This is one reason for saving and loading the playlist.

Settingsscreen: for setting directories, set loop or stop at end of playlist, delete finally or use recycle bin
You can save and load your settings in different profiles.

The project is not finished yet, a lot of todos will improve this application further.
