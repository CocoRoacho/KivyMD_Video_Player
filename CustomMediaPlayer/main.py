"""
The entry point to the application.

The application uses the MVC template. Adhering to the principles of clean
architecture means ensuring that your application is easy to test, maintain,
and modernize.

You can read more about this template at the links below:

https://github.com/HeaTTheatR/LoginAppMVC
https://en.wikipedia.org/wiki/Model–view–controller
"""

# keine Ahnung wofür die nächsten 2 Zeilen sind, ich denke um ffpyplayer in PATH zu schreiben???
import os
os.environ["KIVY_VIDEO"] = "ffpyplayer"

from multiprocessing.resource_sharer import stop
from time import time

from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import StringProperty

from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager

from View.screens import screens

from libs.playlist_manipulation import get_listindex, update_playlistitem_duration, feed_playlist

from libs.disk_operations import join_path_with_file, get_files_from_folder
from libs.json_ops import write_json_file, open_json_file

#from kivy.config import Config #???



class ControlVariables():
    """ put here the ids of the widgets for maybe better accessing?"""

    playlist = []
    path_folder1 = "" #"E:/Coding/VideoAssets/edit"
    path_folder2 = "" #"E:/Coding/VideoAssets/hot"
    path_folder3 = "" #"E:/Coding/VideoAssets/hottest"
    path_thumbnails = "" #"E:/Coding/VideoAssets/thumbs"
    loop_playlist = False
    put_in_r_bin = False
    keep_in_plist = False
    allow_subfolders = False
    folder_1 = "edit"
    folder_2 = "hot"
    folder_3 = "hottest"

    init_dir = "E:\Coding\VideoAssets"

    # TODO: create an .ini-file to load (and save) initial settings and load on startup


    def __init__(self, video_player, button_box, btn_stop, btn_play_pause, btn_last, btn_next, btn_volume, btn_playlist, btn_fullscreen, btn_settings, progress_container, lbl_time_pos, lbl_time_dur, volume_container, lbl_video_title, side_bar, btn_open, btn_folder1, btn_folder2, btn_folder3, btn_sidebar_on) -> None:
        self.video_player = video_player
        self.button_box = button_box
        self.btn_stop = btn_stop
        self. btn_play_pause = btn_play_pause
        self.btn_last = btn_last
        self.btn_next = btn_next
        self.btn_volume = btn_volume
        self.btn_playlist = btn_playlist
        self.btn_fullscreen = btn_fullscreen
        self.btn_settings = btn_settings
        self.progress_container = progress_container
        self.lbl_time_pos = lbl_time_pos
        self.lbl_time_dur = lbl_time_dur
        self.volume_container = volume_container
        self.lbl_video_title = lbl_video_title
        self.side_bar = side_bar
        self.btn_open = btn_open
        self.btn_folder1 = btn_folder1
        self.btn_folder2 = btn_folder2
        self.btn_folder3 = btn_folder3
        self.btn_sidebar_on = btn_sidebar_on

        # TODO: make this much args better and more pythonian

    def create_dict_for_init_json(self):
        """ create a dictionary with all data needed for startup. 
            Used for save data to json file.
        """

        return {
            "path_folder1": self.path_folder1,
            "path_folder2": self.path_folder2,
            "path_folder3": self.path_folder3,
            "path_thumbnails": self.path_thumbnails,
            "loop_playlist": self.loop_playlist,
            "put_in_r_bin": self.put_in_r_bin,
            "keep_in_plist": self.keep_in_plist,
            "allow_subfolders": self.allow_subfolders,
            "init_dir": self.init_dir,
            "folder_1": self.folder_1,
            "folder_2": self.folder_2,
            "folder_3": self.folder_3
            }
    
    def update_settings(self, dic_settings):
        """ get data from a dictionary and get them to the corresponding variables. """

        self.path_folder1 = dic_settings["path_folder1"]
        self.path_folder2 = dic_settings["path_folder2"]
        self.path_folder3 = dic_settings["path_folder3"]
        self.path_thumbnails = dic_settings["path_thumbnails"]
        self.loop_playlist = dic_settings["loop_playlist"]
        self.put_in_r_bin = dic_settings["put_in_r_bin"]
        self.keep_in_plist = dic_settings["keep_in_plist"]
        self.allow_subfolders = dic_settings["allow_subfolders"]
        self.init_dir = dic_settings["init_dir"]
        self.folder_1 = dic_settings["folder_1"]
        self.folder_2 = dic_settings["folder_2"]
        self.folder_3 = dic_settings["folder_3"]


class CustomMediaPlayer(MDApp):
    
    myControl = None
    viduration = -1 # damit ich das label video duration füllen kann (video.duration bekommt den aktuellen wert erst sehr spät, das ist ein workaround)...
    initialisation_file = "assets/profiles/init.json" ### put in myControl!!!

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_all_kv_files(self.directory)

        # set a default screen size! Maybe 1280x720...
        Window.size = (1280, 720)
        

        # This is the screen manager that will contain all the screens of your
        # application.
        self.manager_screens = MDScreenManager()
        
        
    def build(self) -> MDScreenManager:
        
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"
        
        # set a default screen size! Maybe 1280x720...
        #Window.size = (1280, 720)
        
        # allow_screensaver but later in code forbid when play video
        self.screensaver_off(True)
        
        # connection for drag and drop stuff
        Window.bind(on_drop_file=self.on_file_drop)


        self.generate_application_screens()

        # fill object myControl with content kann ich hier im build up besser drauf zugreifen???
        self.myControl = self.create_myControl()

        #open json-file and store data to variables
        self.load_settings_from_jsonfile()

        # set startup values loaded from init.json to settings screen
        self.manager_screens.screens[2].set_values()

        self.rename_Folder_tips()
        
        
        return self.manager_screens

    
    def on_start(self):
        """ app start is finished, then this will be executed! """

        """
        --> def build(self)...
        # fill object myControl with content
        self.myControl = self.create_myControl()
        """

        # show fps on screen
        #self.fps_monitor_start()

        # TODO: create a backgroundimage for standby

        #???? 
        ###self.rename_Folder_tips()
        
        # schedule for updating time labels (once per second)
        Clock.schedule_interval(self.refresh_lbl_time, 1)
        # TODO: only get video.duration on load and then take out the label_dur.text from scheduling process --> ok


    def rename_Folder_tips(self):
        """  """

        #???? 
        self.myControl.btn_folder1.tooltip_text = f"Send to folder: {self.myControl.folder_1}"
        self.myControl.btn_folder2.tooltip_text = f"Send to folder: {self.myControl.folder_2}"
        self.myControl.btn_folder3.tooltip_text = f"Send to folder: {self.myControl.folder_3}"

    def screensaver_off(self, state):
        """ turns screensaver allowance on and off """

        Window.allow_screensaver = state


    def load_settings_from_jsonfile(self):
        """ open json-file and store data to variables """

        self.myControl.update_settings(open_json_file(self.initialisation_file))


    def write_settings_to_jsonfile(self):
        """ writes all data related to startup settings to a specific json-file. """

        write_json_file(self.initialisation_file, self.myControl.create_dict_for_init_json())

        return True


    def on_file_drop(self, window, file_path, *args):
        """ handle files which are dropped on the app.

            append these files to the playlist.
            # TODO: put this function to disk operations etc...
        """

        # check if file folder or link
        dropped = str(file_path.decode("utf-8"))

        if os.path.isfile(file_path):
            # TODO: handle files with extension .lnk ...
            print(f"is file: {dropped}")

            drpd_path = dropped[:dropped.rfind("\\")]
            drpd_file = dropped[dropped.rfind("\\")+1:]

            feed_playlist([join_path_with_file(drpd_path, drpd_file)]) # edit file, or she'll not be detected by different functions...
        
        elif os.path.isdir(file_path):
            
            print(f"is path: {dropped}")
            # TODO: handling an drag and drop folder
            files_in_dropped_folder = get_files_from_folder(dropped)
            print(f"{dropped} contains {len(files_in_dropped_folder)} items")
            feed_playlist(files_in_dropped_folder)

        elif os.path.islink(file_path):
            
            print(f"is link: {file_path}")
            # TODO: handling an drag and drop file or folder link
            print(f"is link: {file_path}")

        else:
            print(f"is none of my business: {file_path}")

        

    def get_video_duration(self, arg):
        """ make lbl_time show the actual video progress time. try to get it until it is available... """
        
        if self.viduration <= 1.0:
            self.viduration = self.myControl.video_player.duration
        
        else:
            # update video_player.lbl_time_dur
            vidur_frmtd = self.get_formatted_timecode(self.viduration)
            self.myControl.lbl_time_dur.text = vidur_frmtd if self.myControl.video_player.duration >= 3600 else vidur_frmtd[vidur_frmtd.find(':')+1:]

            # update playlist item duration
            print(f"Need to update playlist item duration: {self.myControl.video_player.source}")
            plist_item = self.myControl.playlist[get_listindex(self.myControl.video_player.source)]
            update_playlistitem_duration(plist_item, vidur_frmtd)

            return False


    def refresh_lbl_time(self, arg):
        """ make lbl_time show the actual video progress time """

        if self.myControl.video_player.state != 'stop': # sonst zeigt's immer die duration des 1. videos in playlist
            if self.myControl.lbl_time_dur.text in ["", "0:00:00"]:
                Clock.schedule_interval(self.get_video_duration, 0)
        
        if self.myControl.video_player.state == 'play':
            
            vid_progress = self.get_formatted_timecode(self.myControl.video_player.position)
            
            # format the progress time to my belongings & fill lbl_time
            self.myControl.lbl_time_pos.text = vid_progress if self.myControl.video_player.duration >= 3600 else vid_progress[vid_progress.find(':')+1:]

        
    def get_formatted_timecode(self, timecode):
        """ format time from value in seconds to 'h:mm:ss' """

        dauer = int(timecode) #schneidet alles nach dem komma ab!
        #dauer_rest = self.myControl.video_player.duration - dauer ist hier irrelevant! könnte aber angehängt werden...

        hours = dauer // 3600
        hours_rest = dauer % 3600
        minutes = hours_rest // 60
        seconds = hours_rest % 60

        return f"{hours}:{minutes:02d}:{seconds:02d}"
        

    def get_window_size(self):
        """
        returns the actual window-size as a tuple (x, y)
        """

        print(f"window size: {Window.size}")

        return Window.size


    def fullscreening(self):
        """
        puts the app in fullscreen mode
        'auto': to match the screen resolution

        or disables fullscreen
        """

        if not Window.fullscreen:
            Window.fullscreen = "auto"
        else:
            Window.fullscreen = False

        return Window.fullscreen


    def exit_fullscreen(self):
        """ does exit the fullscreen to avoid some issues with dialogs etc... """

        if Window.fullscreen:
            Window.fullscreen = False # end fullscreen to avoid some issues

        return Window.fullscreen

    

    def create_myControl(self):
        """ creates object from class ControlVariables 
            and fills all the initial variables with content.
        """

        path_to_main_ids = self.manager_screens.get_screen('main screen').ids

        #print(f"path to main ids: {path_to_main_ids}")
        #print(f"dir path to main ids: {path_to_main_ids.side_bar.ids}")

        return ControlVariables(
            path_to_main_ids.video_player, 
            path_to_main_ids.button_box,
            path_to_main_ids.button_box.ids.btn_stop,
            path_to_main_ids.button_box.ids.btn_play_pause,
            path_to_main_ids.button_box.ids.btn_last,
            path_to_main_ids.button_box.ids.btn_next,
            path_to_main_ids.button_box.ids.btn_volume,
            path_to_main_ids.button_box.ids.btn_show_playlist,
            path_to_main_ids.button_box.ids.btn_fullscreen,
            path_to_main_ids.button_box.ids.btn_settings,
            path_to_main_ids.button_box.ids.progress_container,
            path_to_main_ids.button_box.ids.lbl_time_pos,
            path_to_main_ids.button_box.ids.lbl_time_dur,
            path_to_main_ids.button_box.ids.volume_container,
            path_to_main_ids.lbl_video_title,
            path_to_main_ids.side_bar,
            path_to_main_ids.side_bar.ids.btn_open,
            path_to_main_ids.side_bar.ids.btn_folder1,
            path_to_main_ids.side_bar.ids.btn_folder2,
            path_to_main_ids.side_bar.ids.btn_folder3,
            path_to_main_ids.button_box.ids.btn_sidebar_on        
            )

        # TODO: create also controls for second and third screen
       

    def generate_application_screens(self) -> None:
        """
        Creating and adding screens to the screen manager.
        You should not change this cycle unnecessarily. He is self-sufficient.

        If you need to add any screen, open the `View.screens.py` module and
        see how new screens are added according to the given application
        architecture.
        """

        for i, name_screen in enumerate(screens.keys()):
            model = screens[name_screen]["model"]()
            controller = screens[name_screen]["controller"](model)
            view = controller.get_view()
            view.manager_screens = self.manager_screens
            view.name = name_screen
            self.manager_screens.add_widget(view)

            
# run here!!!

if __name__ == '__main__':

    """
    # doesn't work anymore???
    Config.set('graphics', 'width', '1280')
    Config.set('graphics', 'height', '720')
    """

    CustomMediaPlayer().run()

# TODO: Keyboard controls
# TODO: Mouse cursor in or out window, 
# TODO: Mouse cursor hide when not moved for 5 seconds
# TODO: drag and Drop behavior --> OK
# TODO: Add Button / method for renaming file
# TODO: Button for loading let's say 50 videos from one directory (incl. subfolders) in to playlist
# Todo: open preview picture in dialog window in a bigger version ?