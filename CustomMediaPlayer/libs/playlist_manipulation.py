from kivymd.app import MDApp

from random import shuffle
from os import path

from libs.retrieve_metadata import get_vid_duration, generate_thumbnail
### from libs.disk_operations import check_file_exist #--> does not work = circular import (???)


def feed_playlist(filmfileslist):
    """ if file is not yet in playlist: append file to playlist 
    
        filmfileslist must be a list of filenames (with path): '/assets/videos/baja.mp4'

    """
    
    alreadyinplaylist = [video["film_path"] for video in MDApp.get_running_app().myControl.playlist]
    ###print(f"alreadyinplaylist: {alreadyinplaylist}")

    for film in filmfileslist:
        
        if film not in alreadyinplaylist:
            # create sublist
            film_data_dict = create_playlist_dict_item(film)

            # attach to playlist
            MDApp.get_running_app().myControl.playlist.append(film_data_dict)


def shuffle_playlist():
    """ remix the playlist """

    # shuffle playlist
    shuffle(MDApp.get_running_app().myControl.playlist)

    # clear container playlist
    MDApp.get_running_app().manager_screens.screens[1].clear_complete_playlist()

    # fill container playlist
    MDApp.get_running_app().manager_screens.screens[1].create_playlist_widgets()


def delete_from_playlist(vpath):
    """
        Delete given file from myControl.playlist.

        arg vpath: path(incl. file name) from file to delete
    """

    plist = MDApp.get_running_app().myControl.playlist

    plist.remove(plist[get_listindex(vpath)])


    # update playlist_container
    # TODO: remove from container_playlist --> ok?
    MDApp.get_running_app().manager_screens.screens[1].clean_playlist_widgets()


def update_playlistitem_path(newpath, plist_index):
    """ updates the path of an playlist item after moving to a new location. 
        
        oldpath: (str) contains path with complete filename from old location ### not necessary anymore????
        newpath: (str) contains path with complete filename from new location
    """

    plist = MDApp.get_running_app().myControl.playlist

    indx_video = plist_index ###get_listindex(oldpath) 
    plist[indx_video]["film_path"] = newpath

    MDApp.get_running_app().manager_screens.screens[1].update_widget_props(plist[indx_video])


def update_container_playlist():
    """ update playlist_container - remove old entries, add new entries"""

    MDApp.get_running_app().manager_screens.screens[1].clean_playlist_widgets()
    MDApp.get_running_app().manager_screens.screens[1].create_playlist_widgets()


def update_playlistitem_duration(plist_item, new_duration):
    """ for videos with no duration in playlist_item, update duration after receiving it when watching video.
    
        plist_item: dict - ["...", "duration", "..."]

        new_duration: string in format "0:00:00"
    """

    #playlist = MDApp.get_running_app().myControl.playlist
    print(f"from function - before: {plist_item}") ###
    plist_item["duration"] = new_duration

    print(f"from function - after: {plist_item}") ###

    MDApp.get_running_app().manager_screens.screens[1].update_widget_props(plist_item)


def create_playlist_item(film):    # deprecated
    """
        returns an listobject as item for main myControl.playlist 
        
        input: Film = path with filename

        output: [film(path), duration(formatted), thumb(path)] <-- evtl. alles NUR in ein dictionary packen
        
    """

    # TODO change playlist item to dictionary: [film:path, duration:time, thumb:path, title:string, resolution:(x, y), ...] --> film and thumb are strings with path, duration is formatted timestamp

    app = MDApp.get_running_app()

    # retrieve video duration and format
    duration = get_vid_duration(film) # in seconds type float
    vduration = app.get_formatted_timecode(duration) if duration > 0 else "" # type str
    if vduration != "":
        vlength = vduration if duration >= 3600 else vduration[vduration.find(':')+1:]
    else:
        vlength = vduration

    # generate thumbnail
    out_path = f"{app.myControl.path_thumbnails}/{film[film.rfind('/')+1:film.rfind('.')]}.png"
    generate_thumbnail(film, out_path)

    return [film, vlength, out_path]


def create_playlist_dict_item(film):    
    """
        returns an dictobject as item for main myControl.playlist 
        
        input: Film = path with filename

        output: {
            "film_name" : "string",
            "film_path" : "str(path)", 
            "thumb_path" : "str(path)", 
            "duration" : "str(formatted 0:00:00)", 
            "format" : "str(avi)",
            "codec" : "str(h264)", 
            "Resolution" : "str(1280 x 720)",
            "size": MB, --> build something to convert value to GByte when needed...
            "currentPos": float(seconds)
            }
        
    """

    # TODO change playlist item to dictionary: [film:path, duration:time, thumb:path, title:string, resolution:(x, y), ...] --> film and thumb are strings with path, duration is formatted timestamp

    return {
        "film_name" : film[film.rfind('/')+1:film.rfind('.')],
        "extension" : film[film.rfind('.'):],
        "film_path" : film,
        "thumb_path" : get_thumbnail(film, create_thumb_path(film)),
        "duration" : get_video_duration(film)
        }


def get_video_duration(videofile):
    """
        get the video duration, format it and return it...
    """

    app = MDApp.get_running_app()

    # retrieve video duration and format
    duration = get_vid_duration(videofile) # in seconds type float
    vduration = app.get_formatted_timecode(duration) if duration > 0 else "" # type str
    if vduration != "":
        vlength = vduration if duration >= 3600 else vduration[vduration.find(':')+1:]
    else:
        vlength = vduration

    return vlength


def get_thumbnail(videofile, thumbfile):
    """ calls function to create thumbnailpath, then calls function to generate thumbnail """

    generate_thumbnail(videofile, thumbfile)
    return thumbfile # klingt komisch aber brauche ich für create_playlist_dict_item - sonst gibt es ein None...



def create_thumb_path(path_to_videofile, extension='png'):
    """ 
        generate thumbnail-filename for the thumbnail to create.

        args:
          path_to_videofile (str): path with filename as string
          extension (str): defines fileformat, default = 'png'
        
        return path to thumbnail-file as (str)
    """

    app = MDApp.get_running_app()
    film = path_to_videofile
    counter = 1

    thumb_path = f"{app.myControl.path_thumbnails}/{film[film.rfind('/')+1:film.rfind('.')]}.{extension}"
    
    # thumb-path file not found!!! --> create new thumb_path
    while path.isfile(thumb_path):
        thumb_path = f"{app.myControl.path_thumbnails}/{film[film.rfind('/')+1:film.rfind('.')]}_{counter:03d}.png"
        counter += 1
    
    return thumb_path
    


def get_listindex(film):
    """
        takes a path and look inside sublists if this path is available.

        if yes it returns the index of this item
        
    """
    app = MDApp.get_running_app()

    for item in app.myControl.playlist:
        if film in item["film_path"]:
            return app.myControl.playlist.index(item)
                