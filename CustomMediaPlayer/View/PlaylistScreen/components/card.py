from kivy.properties import StringProperty

from kivymd.app import MDApp
from kivymd.uix.card import MDCard

from kivymd.uix.behaviors import RectangularElevationBehavior, RoundedRectangularElevationBehavior


# TODO: label with length of video (duration) --> ok

class VideoCard(MDCard, RoundedRectangularElevationBehavior):
    thumb = StringProperty() # path with filename of thumbnail
    text = StringProperty() # name of the file without path
    duration = StringProperty() #->"02:10:40"
    path = StringProperty() # store the complete path to the file - needed for example to load file in videoplayer

    # default card properties
    ripple_behavior = True

    def on_release(self):
        
        app = MDApp.get_running_app()
        video = app.myControl.video_player

        video.load_video(self.path) # load selected video
        app.manager_screens.screens[1].color_current_active_playlist_item() # highlight selected playlist item, de-highlight others
