from logging import root
from random import randint

from functools import partial

from kivy.metrics import dp, sp
from kivy.properties import BooleanProperty, ObjectProperty, StringProperty
from kivy.uix.video import Video
from kivy.animation import Animation
from kivy.clock import Clock

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton, MDFlatButton
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.tooltip import MDTooltip
from kivymd.uix.behaviors import HoverBehavior
from kivymd.toast import toast

from View.base_screen import BaseScreenView

from libs.disk_operations import deletefile, movefile, get_new_videofile
from libs.playlist_manipulation import delete_from_playlist, get_listindex, update_playlistitem_path


class PlayerButtonBox(MDBoxLayout):
    """
    Implements a container for the control buttons of the video player:
    Stop/Play/Full screen/Volume and Progress sliders.
    """

    video = ObjectProperty()  # 'CustomVideoPlayer' object


class SideControls(MDGridLayout):
    """
    Implements a container for the special control buttons.
    
    Delete File
    Send to hot, hottest folder or edit

    open file
    file infos
    """

    video = ObjectProperty()  # 'CustomVideoPlayer' object


class RandomJumps(MDGridLayout):
    """
    Implements a container for the special control buttons.
    
    Random jumps back & forth
    """

    video = ObjectProperty()  # 'CustomVideoPlayer' object

    # TODO: No Animation on press! (no visibility of a button press) --> OK (ripple_scale: 0 # makes ripplebehavior invisible)

# -------------------------------- Custom slider -------------------------------

class ProgressBarVideo(MDProgressBar):
    video = ObjectProperty()  # 'CustomVideoPlayer' object

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return
        self._update_seek(touch.x)

    def _update_seek(self, x):
        if self.width == 0:
            return
        x = max(self.x, min(self.right, x)) - self.x
        self.video.seek(x / float(self.width))


# --------------------------- Custom control buttons ---------------------------

class BasePlayerButton(MDIconButton, MDTooltip):
    """ Implements a basic button for video player buttons. """

    video = ObjectProperty()  # 'CustomVideoPlayer' object
    # Default property button.
    valign = "center"
    halign = "center"
    theme_icon_color = 'Custom'
    icon_color = 'white'
    icon_size = sp(20)
    adaptive_size = True
    
    tooltip_bg_color = (1, 1, 1, 0.4)
    #tooltip_text_color = "white"
    shift_y = 25

class SpecialFunctionsButton(MDIconButton, MDTooltip):
    """ Implements a button for my special functions. """

    video = ObjectProperty()  # 'CustomVideoPlayer' object

    valign = "center"
    halign = "right"
    adaptive_size = True
    icon_size = sp(24)
    
    #md_bg_color= 232/255, 42/255, 0, .3 #.95 # -> reddish color for debug

    tooltip_bg_color = (1, 1, 1, 0.4)
    #tooltip_text_color = "white"
    shift_y = 30

class ButtonVideoStop(BasePlayerButton):
    
    def on_release(self, *args):    
        """ calls video stop function.
            turn play/pause icon to play.
        """

        self.video.stop_video()
        
class ButtonVideoPlayPause(BasePlayerButton):
    
    def on_release(self, *args):
        """ no video source declared then open a file 
            otherwise play or pause the video
        """

        MDApp.get_running_app().screensaver_off(False)

        def callback(value):
            """ needed to return a value from clock.schedule_once... for starting the loaded video. """
            MDApp.get_running_app().myControl.video_player.load_video(value)


        playlist = MDApp.get_running_app().myControl.playlist

        if self.video.source: 
            self.video.state = "pause" if self.video.state == "play" else "play"
        else:
            # TODO: open first entry in playlist, if playlist empty: open File dialog --> ok
            
            if len(playlist): # wenn mindestens ein objekt in playlist...
                # lade es!
                self.video.load_video(playlist[0]['film_path'])
            else:
                
                # open file dialog to look for a new file to load
                get_new_videofile(callback)

            # set play icon to right state
            self.icon = "pause"
        
        return True

class ButtonRandomJump(MDFlatButton):
    
    def random_jump(self, direction):
        """ Jumps to a new position on the video progressbar.
            The new position is found randomly within 1 or 23 %.

            This function needs arg 'direction' (of type string) to know in which direction to 'jump'
        
        """

        if self.video.state != "stop":

            pos = self.video.position # in seconds
            rnd = (randint(1, 23) / 100) #random value in percent

            if direction == "backward":
                self.video.jump_to_position(pos - (rnd * self.video.position)) # arg in seconds
                # so that the function can never go below 0...
            else:
                self.video.jump_to_position(pos + (rnd * self.video.duration))

class ButtonVideoVolume(BasePlayerButton):
    
    def on_release(self, *args):
        self.video.volume = 0 if self.video.volume > 0 else .75
        return True

class ButtonLastVideo(BasePlayerButton):
    pass
        
class ButtonNextVideo(BasePlayerButton):
    pass

class ButtonShowPlaylist(BasePlayerButton):

    def on_release(self, *args):
        
        screen = MDApp.get_running_app().manager_screens.screens[0]

        # call function which calls next screen
        screen.controller.on_tap_hero(screen.ids.hero_from)
        
        return True
    
class ButtonVideoFullScreen(BasePlayerButton):

    # f_screen variable needed for icon change
    f_screen = BooleanProperty(False)
    
    def on_release(self, *args):
        
        self.f_screen = MDApp.get_running_app().fullscreening()

        return True

class ButtonSettings(BasePlayerButton):
    """ settings for paths to send the videos to... """

    def on_release(self, *args):

        # TODO: open options screen --> ok

        screen = MDApp.get_running_app().manager_screens.screens[0]

        # call function which calls next screen
        screen.controller.on_click_settings()
        
        return True

class ButtonShowSidebar(BasePlayerButton):

    visible = True

    def on_release(self):

        self.visible = self.show_sidebar() if self.visible == False else self.hide_sidebar()
        
    
    def show_sidebar(self, *args):
        """ Shows the container with the sidebar controls of the player """

        def add_sidebar_container(*args):
            MDApp.get_running_app().manager_screens.get_screen('main screen').ids.side_bar.pos_hint = {"right": 1} #.height = dp(56)
            #print(f"pos: {MDApp.get_running_app().manager_screens.get_screen('main screen').ids.side_bar.pos_hint}")

        this_screen = MDApp.get_running_app().manager_screens.get_screen('main screen')
        sidebar = this_screen.ids.side_bar.ids

        for instance in [
            sidebar.btn_folder3,
            sidebar.btn_folder2,
            sidebar.btn_del,
            sidebar.btn_open,
            sidebar.btn_folder1
        ]:
            Animation(opacity=1, d=0.2).start(instance)

        anim = Animation(opacity=1, d=0.2)
        anim.bind(on_complete=add_sidebar_container)
        anim.start(sidebar.btn_about)

        return True

    
    def hide_sidebar(self, *args):
        """ Hides the container with the sidebar controls of the player """

        def remove_sidebar_container(*args):
            MDApp.get_running_app().manager_screens.get_screen('main screen').ids.side_bar.pos_hint = {"right": 2} #.height = 0
            #print(f"pos: {MDApp.get_running_app().manager_screens.get_screen('main screen').ids.side_bar.pos_hint}")

        this_screen = MDApp.get_running_app().manager_screens.get_screen('main screen')
        sidebar = this_screen.ids.side_bar.ids

        for instance in [
            sidebar.btn_folder3,
            sidebar.btn_folder2,
            sidebar.btn_del,
            sidebar.btn_open,
            sidebar.btn_folder1
        ]:
            Animation(opacity=0, d=0.2).start(instance)

        anim = Animation(opacity=0, d=0.2)
        anim.bind(on_complete=remove_sidebar_container)
        anim.start(sidebar.btn_about)

        return False


class ButtonAbout(SpecialFunctionsButton):
    
    def on_release(self, *args):
        
        MDApp.get_running_app().get_window_size()

        print(f"playlist: {MDApp.get_running_app().myControl.playlist}")

        toast(str(MDApp.get_running_app().myControl.playlist)) # --> show info message...
        
        return True

        # TODO: file infos: make a dialog message to show metadata of the selected video
        # TODO: Dialog should have an ok button but also a timer and hide dialog after maybe 10 seconds?


class ButtonOpen(SpecialFunctionsButton):

    # TODO: make a dropmenu for choosing open file or open folder dialog

    def on_release(self):
        """ exits fullscreen if app in fullscreen mode """

        app = MDApp.get_running_app()
        
        app.myControl.btn_fullscreen.f_screen = app.exit_fullscreen()

        # wait 0.1 seconds for the former task to complete
        # then call function to select new videofile

        def callback(value):
            """ needed to return a value from clock.scheduleonce... for starting the loaded video. """
            MDApp.get_running_app().myControl.video_player.load_video(value)
            
        Clock.schedule_once(lambda dt: get_new_videofile(callback), 0.1)


class ButtonDelVideo(SpecialFunctionsButton):
    
    def on_release(self):

        video = MDApp.get_running_app().myControl.video_player
        video.delete_sourcefile()
       

class ButtonSendToFolder2(SpecialFunctionsButton):

    def on_release(self):

        video = MDApp.get_running_app().myControl.video_player

        if video.state != "stop":

            new_folder = MDApp.get_running_app().myControl.path_folder2

            video.move_sourcefile_to_new_location(new_folder)
        

class ButtonSendToFolder1(SpecialFunctionsButton):

    tooltip = StringProperty()
    
    def on_release(self):

        video = MDApp.get_running_app().myControl.video_player

        new_folder = MDApp.get_running_app().myControl.path_folder1

        video.move_sourcefile_to_new_location(new_folder)


class ButtonSendToFolder3(SpecialFunctionsButton):
    
    def on_release(self):

        video = MDApp.get_running_app().myControl.video_player

        new_folder = MDApp.get_running_app().myControl.path_folder3

        video.move_sourcefile_to_new_location(new_folder)


# ------------------------------- videoplayer ------------------------------------
class VideoScreen(Video):
    """ here you set and control the videoplayer widget 
        inherited from the kivy video class """

    #preview = "assets\images\Sexy01.png"
    preview = "assets\images\Steamwalker_banner.png"

    def _on_eos(self, *largs):
        """ function called on end of video stream. I will go to next video in playlist."""

        playlist = MDApp.get_running_app().myControl.playlist
        loop = MDApp.get_running_app().myControl.loop_playlist
        actual_index = get_listindex(self.source)

        if actual_index < len(playlist)-1:
            self.load_video(playlist[actual_index+1]['film_path'])
        else:
            # Loopfunction wenn true dann springe vom Ende der Liste zum anfang... oder stop nach letztem video
            self.load_video(playlist[0]['film_path']) if loop else self.stop_video()


    def load_video(self, video_file, v_position=0, *args):
        """ function to load a video into the streamer and start to play.
        
            args:
                video_file: String, contains "path + filename"
                v_position: int(or float), contains position where to start the video in seconds

        """

        app = MDApp.get_running_app()
        app_control = app.myControl

        # reset viduration for using in label
        app.viduration = -1

        plist_item = app_control.playlist[get_listindex(video_file)]
        
        # TODO: basevalue or get duration from playlist item if available --> ok
        app_control.lbl_time_dur.text = "0:00:00" if plist_item['duration'] == "" else plist_item['duration']
    
        self.source = video_file
        self.color = 1,1,1,1
        self.state = "play"

        # jump to specific position        
        if v_position > 0:
            Clock.schedule_interval(partial(self.jump_to_position, v_position), 0)    
        
        # video name for the Label lbl_video_title
        ###vid_name = self.source[self.source.rfind("/")+1:]
        app_control.lbl_video_title.text = plist_item['film_name']


    def jump_to_position(self, position, *args):
        """ jumps to a specific position of the video but only after the video is loaded """

        if not self.loaded:
            print("load video yet")
        else:
            print(f"video.loaded: {self.loaded} --> jump to {position}: {((position*100)/self.duration/100)}")
            self.seek(((position*100)/self.duration)/100, precise=True)

            return False


    def stop_video(self, keep_fullscreen=False):
        """ stops and unload video and shows BG-Logo.
            eventually exits fullscreen mode.
        """

        self.state = "stop"
        
        self.source = ""
        
        ###self.unload()
        self.color = 0,0,0,1
        
        app = MDApp.get_running_app()

        if not keep_fullscreen:
            app.exit_fullscreen()
        
        # allw screensaver again
        app.screensaver_off(True)
        
        # reset 
        app.myControl.lbl_video_title.text = ""

        # reset progressbar for video position and corresponding labels
        app.myControl.progress_container.children[1].value = 0

        # format the progress time to my belongings & fill lbl_time
        app.myControl.lbl_time_pos.text = "0:00:00"
        app.myControl.lbl_time_dur.text = "0:00:00"


        app.myControl.btn_play_pause.icon = "play" # default the play button to play icon


    def prev_video(self, *args):    
        """ loads previous video from playlist to videoplayer.

            checks length from playlist:
                does nothing when only one video in playlist,
                goes to last video when reached first video
        """

        playlist = MDApp.get_running_app().myControl.playlist

        actual_index = get_listindex(self.source)
            
        if len(playlist) > 1: # damit kein autoplay wenn nur ein objekt in playlist...
            if actual_index > 0:
                self.load_video(playlist[actual_index-1]['film_path'])
            else:
                self.load_video(playlist[-1]['film_path'])
        
        # highlight the right child in playlist_screen
        MDApp.get_running_app().manager_screens.screens[1].color_current_active_playlist_item()
    
        return True
        

    def next_video(self, *args):    
        """ loads next video from playlist to videoplayer.

            checks length from playlist:
                does nothing when only one video in playlist,
                goes to first video when reached last video
        """

        playlist = MDApp.get_running_app().myControl.playlist

        actual_index = get_listindex(self.source)

        if len(playlist) > 1: # damit kein autoplay wenn nur ein objekt in playlist...
            if actual_index < len(playlist)-1:
                self.load_video(playlist[actual_index+1]['film_path'])
            else:
                self.load_video(playlist[0]['film_path'])
        
        # highlight the right child in playlist_screen
        MDApp.get_running_app().manager_screens.screens[1].color_current_active_playlist_item()
        
        return True


    def move_sourcefile_to_new_location(self, new_path):
        """ move loaded file to new location. video.stop needed for correct functonality...
            needs new path as argument!
        """
        if self.state != 'stop':
            playlist = MDApp.get_running_app().myControl.playlist


            source_index = get_listindex(self.source)
            source_item = playlist[source_index]
            old_path = source_item['film_path']
            

            keep_in_list = True if MDApp.get_running_app().myControl.keep_in_plist else False
            v_progress = self.position # actual position taken to eventually start the video again on this position
            
            if len(playlist)> 1 and not keep_in_list:
                self.next_video()
            else:
                self.stop_video(True)
            
            # wait 5 seconds for the former task to complete
            # then call function to move videofile
            Clock.schedule_once(partial(movefile, source_item['film_path'], new_path), 5)
            
            print(f"moved file: {source_item['film_path'][source_item['film_path'].rfind('/')+1:]} to {new_path}") ###

            # TODO: Choose keep moved file in playlist or remove from playlist??? --> ok
            if keep_in_list:
                # update playlist widget
                new_path_w_filename = f"{new_path}/{source_item['film_path'][source_item['film_path'].rfind('/')+1:]}" # TODO: use what you have in playlist dict!!!
                update_playlistitem_path(new_path_w_filename, source_index)
                # TODO: get new path to playlist or delete from playlist --> OK

                # TODO: remember video position and restart video from there --> OK
                
                Clock.schedule_once(partial(self.load_video, source_item['film_path'], v_progress), 5)
                
            else:
                # remove moved file from playlist
                delete_from_playlist(old_path)
        

    def delete_sourcefile(self):
        """ deletes the file currently loaded into videoplayer.
            Needs to stop and unload the file for proper functionaliy
        """

        if self.state != 'stop':
            playlist = MDApp.get_running_app().myControl.playlist

            vpath = self.source
            
            if len(playlist)> 1:
                self.next_video()
            else:
                self.stop_video()

            # wait 5 seconds for the former task to complete
            # then call function to delete videofile
            Clock.schedule_once(partial(deletefile, vpath), 5)
            
            print(f"removed file: {vpath[vpath.rfind('/')+1:]}")

            # remove from playlist completely
            delete_from_playlist(vpath)
            

class HoverOverApp(MDBoxLayout, HoverBehavior):
    '''Custom item implementing hover behavior.
       for tracking the mouse over the video app '''

    def on_enter(self, *args):
        '''The method will be called when the mouse cursor
        is within the borders of the current widget.'''
        
        self.show_button_box()


    def on_leave(self, *args):
        '''The method will be called when the mouse cursor goes beyond
        the borders of the current widget.'''

        # TODO check video.state and only do something when state == 'play' ???notwendig or not???

        self.hide_button_box()
        #Clock.schedule_once(self.hide_button_box, 2) <-- funzt nicht richtig 

    def show_button_box(self, *args):
        """ Shows the container with the control box of the player """

        def add_button_box(*args):
            MDApp.get_running_app().myControl.button_box.pos_hint = {"y": 0}
            #print(f"pos: {MDApp.get_running_app().manager_screens.get_screen('main screen').ids.button_box.pos_hint}")

        
        widge_control = MDApp.get_running_app().myControl

        for instance in [
            widge_control.btn_last,
            widge_control.btn_stop,
            widge_control.btn_play_pause,
            widge_control.btn_next,
            widge_control.btn_fullscreen,
            widge_control.btn_volume,
            widge_control.volume_container,
            widge_control.btn_sidebar_on,
            widge_control.btn_settings,
            widge_control.btn_playlist,
            widge_control.lbl_video_title
        ]:
            Animation(opacity=1, d=0.2).start(instance)

        anim = Animation(opacity=1, d=0.2)
        anim.bind(on_complete=add_button_box)
        anim.start(widge_control.progress_container)

    
    def hide_button_box(self, *args):
        """ Hides the container with the control box of the player """

        def remove_button_box(*args):
            MDApp.get_running_app().myControl.button_box.pos_hint = {"y": -1} #.height = 0

        widge_control = MDApp.get_running_app().myControl

        for instance in [
            widge_control.btn_last,
            widge_control.btn_stop,
            widge_control.btn_play_pause,
            widge_control.btn_next,
            widge_control.btn_fullscreen,
            widge_control.btn_volume,
            widge_control.volume_container,
            widge_control.btn_sidebar_on,
            widge_control.btn_settings,
            widge_control.btn_playlist,
            widge_control.lbl_video_title
        ]:
            Animation(opacity=0, d=0.2).start(instance)

        anim = Animation(opacity=0, d=0.2)
        anim.bind(on_complete=remove_button_box)
        anim.start(widge_control.progress_container)


# TODO: create a label inside buttonbox where to show the tooltip_text for the buttons instead of these annoying bubbles...   

# -------------------------------------------------------------------------------

class MainScreenView(BaseScreenView):

    full_screen = BooleanProperty(False)
    title = None

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
        

"""
Damit kann ich noch verbessern, was passiert, wenn der cursor das Fenster "betritt" oder das Fenster "verlässt"

from: Lib\site-packages\kivy\core\window

    def on_cursor_enter(self, *largs):
        '''Event called when the cursor enters the window.

        .. versionadded:: 1.9.1

        .. note::
            This feature requires the SDL2 window provider.
        '''
        pass

    def on_cursor_leave(self, *largs):
        '''Event called when the cursor leaves the window.

        .. versionadded:: 1.9.1

        .. note::
            This feature requires the SDL2 window provider.
        '''
        pass


"""