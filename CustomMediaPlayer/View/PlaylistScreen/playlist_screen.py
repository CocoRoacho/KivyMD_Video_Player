from View.base_screen import BaseScreenView
from View.PlaylistScreen.components.card import VideoCard

from kivy.uix.behaviors import ButtonBehavior

from libs.disk_operations import openmediafile, openmediafolder, open_savefile_dialog, openjsonfile, get_file_extension, check_file_exist

from libs.playlist_manipulation import feed_playlist, shuffle_playlist, create_thumb_path, get_video_duration, get_thumbnail
from libs.json_ops import write_json_file, open_json_file


from kivy.properties import StringProperty, ObjectProperty 

from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.hero import MDHeroTo

# TODO: get back to main screen when click on Hero(videoscreen) --> ok
# TODO: create functions for buttons: Liste speichern und Liste laden

class PlaylistScreenView(BaseScreenView):

    app = ObjectProperty(MDApp.get_running_app())
    
    def on_enter(self, *args):
        
        # --> return super().on_enter(*args) --> ????
        super().on_enter(*args)

        ###print(f"Count children: {len(self.ids.container_playlist.children)}; {bool(self.ids.container_playlist.children)}")

        playlist = self.app.myControl.playlist # MDApp.get_running_app().myControl.playlist
        
        # nur ausführen wenn differenz zwischen children in container_playlist und myControl.playlist.item
        if len(self.ids.container_playlist.children) != len(playlist):
            self.create_playlist_widgets()
            self.clean_playlist_widgets()

        self.color_current_active_playlist_item()


    def color_current_active_playlist_item(self):
        """ when videoplayer is active, show the selected playlist item highlighted in primary color """

        video = self.app.myControl.video_player

        # zeige aktives element der playlist farbig wenn videoplayer in play or pause mode
        if video.state != "stop":
            
            for child in self.ids.container_playlist.children:
                if child.path == video.source:
                    child.md_bg_color = self.app.theme_cls.primary_color #251/255, 69/255, 0, .6 --> cooles rot!!!

                else:
                    child.md_bg_color= self.app.theme_cls.bg_light
        
        else:
            for child in self.ids.container_playlist.children:
                child.md_bg_color= self.app.theme_cls.bg_light

        # TODO: When app in playlist_screen_view and next video starts to play, update highlighting!

    def update_widget_props(self, plist_item):
        """ finds the correct playlist child with filename (child.text).
            Looks for differences between playlist_child and playlist,
            changes values like in playlist.
            
            Does not work when rename child.text! [<-- not yet implemented...]
            """

        for child in self.ids.container_playlist.children:
            if child.text == plist_item["film_name"]:
                if child.path != plist_item["film_path"]:
                    child.path = plist_item["film_path"]

                if child.duration != plist_item["duration"]:
                    child.duration = plist_item["duration"]

                if child.thumb != plist_item["thumb_path"]:
                    child.thumb = plist_item["thumb_path"]


    def create_playlist_widgets(self):
        """ take stored variable playlist and create from their items the widgets and put in container_playlist """

        playlist = self.app.myControl.playlist # MDApp.get_running_app().myControl.playlist

        # list of yet existing playlist items
        playlist_children = [child.text for child in self.ids.container_playlist.children]

        # check if playlist-item already in playlist_children -> then skip!!!
        for playlist_item in playlist:

            # attach new items from myControl.playlist
            if playlist_item["film_name"] not in playlist_children:
                self.ids.container_playlist.add_widget(
                    VideoCard(
                        text=playlist_item["film_name"],
                        path=playlist_item["film_path"],
                        duration=playlist_item["duration"],
                        thumb=playlist_item["thumb_path"]
                    )
                )


    def clean_playlist_widgets(self):
        """ remove children from container_playlist when not in myControl.playlist anymore """

        playlist = self.app.myControl.playlist # MDApp.get_running_app().myControl.playlist

        # create playlist of items with indicator 'path'
        playlist_now = [pl["film_path"] for pl in playlist]

        for child in self.ids.container_playlist.children:
            if child.path not in playlist_now:
                self.ids.container_playlist.remove_widget(child)


    def clear_complete_playlist(self):
        """ clear all children from container_playlist """

        self.ids.container_playlist.clear_widgets()
   

    def back_to_main_screen(self):
        
        screen = MDApp.get_running_app().manager_screens.screens[1]

        screen.controller.on_tap_chevron_back()

class HeroTarget(ButtonBehavior, MDHeroTo):
    pass

#------------------ base class menu button --------------------
class PlaylistMenuButton(MDRectangleFlatButton):
    #increment_width = "364dp"
    pass

#----------------- specific buttons -----------------------

class ButtonPlMenuOpenFile(PlaylistMenuButton):
    
    def on_release(self):

        app = MDApp.get_running_app()

        film = openmediafile()

        feed_playlist([film])
        
        # aktualisiere Playlist JETZT!!!
        app.manager_screens.screens[1].create_playlist_widgets()


class ButtonPlMenuOpenFolder(PlaylistMenuButton):

    def on_release(self):

        app = MDApp.get_running_app()

        filmlinks = openmediafolder()

        print(f"{type(filmlinks)}: {filmlinks})")

        feed_playlist(filmlinks)

        # aktualisiere Playlist JETZT!!!
        app.manager_screens.screens[1].create_playlist_widgets() # TODO gibts da einen besseren zugriff drauf etwa get_current_screen(?) etc.??? <-- create Zugriff über myControl?


class ButtonPlMenuSaveList(PlaylistMenuButton):
    
    def on_release(self):

        appctrl = MDApp.get_running_app().myControl
        
        # set filename... 
        filename = open_savefile_dialog(appdir="playlists")

        write_json_file(filename, appctrl.playlist)


class ButtonPlMenuLoadList(PlaylistMenuButton):
    
    def on_release(self):
        appctrl = MDApp.get_running_app().myControl
        screen = MDApp.get_running_app().manager_screens.screens[1]

        # select file...
        filename = openjsonfile(appdir="playlists")

        # call function to load settings
        loadedpl = open_json_file(filename)

        # integrate loaded playlist in myControl.playlist -- incl. basic error handling
        for playlist_item in loadedpl:

            # filmpath muss sein!!! sonst next in line...
            if playlist_item["film_path"] == '':
                continue # --> go on to the next item

            if not check_file_exist(playlist_item["film_path"]):
                continue # --> go on to the next item

            attach_to_playlist= {"film_name": '', "extension": '', "film_path": '',"thumb_path": '', "duration": ''}
            for itemkey in attach_to_playlist.keys():
                attach_to_playlist[itemkey] = playlist_item.get(itemkey, '')

           
            ###"""
            # wenn andere einträge fehlen, versuche diese selbst zu erzeugen!!!
            for itemkey in attach_to_playlist.keys():
            ###"""    
                if attach_to_playlist[itemkey]== '':

                    ###print(f"{attach_to_playlist['film_path']}: {itemkey}: {attach_to_playlist[itemkey]}")
                    match itemkey:

                        case "film_name":
                            film = attach_to_playlist["film_path"]
                            attach_to_playlist["film_name"] = film[film.rfind('/')+1:film.rfind('.')]

                        case "extension":
                            attach_to_playlist["extension"] = get_file_extension(attach_to_playlist["film_path"])

                        case "thumb_path":
                            attach_to_playlist["thumb_path"] = create_thumb_path(attach_to_playlist["film_path"])
                        
                        case "duration":
                            attach_to_playlist["duration"] = get_video_duration(attach_to_playlist["film_path"])

            # thumb-path file not found!!! --> create new thumb
            if not check_file_exist(attach_to_playlist["thumb_path"]):
                get_thumbnail(attach_to_playlist["film_path"], attach_to_playlist["thumb_path"])


            appctrl.playlist.append(attach_to_playlist)


        # TODO: filmpath muss sein!!! --> ok
        # TODO: wenn andere einträge fehlen, versuche diese selbst zu erzeugen!!! --> ok

        # refresh playlist widget
        # nur ausführen wenn differenz zwischen children in container_playlist und myControl.playlist.item
        if len(screen.ids.container_playlist.children) != len(appctrl.playlist):
            screen.create_playlist_widgets()
            screen.clean_playlist_widgets()



class ButtonPlMenuClearList(PlaylistMenuButton):
    
    def on_release(self):

        app = MDApp.get_running_app()

        # stop videoplayer when playing
        if app.myControl.video_player.state != "stop":
            app.myControl.video_player.stop_video()
        
        app.manager_screens.screens[1].ids.container_playlist.clear_widgets()

        app.myControl.playlist = []

class ButtonPlMenuMixList(PlaylistMenuButton):
    
    def on_release(self):
         shuffle_playlist()