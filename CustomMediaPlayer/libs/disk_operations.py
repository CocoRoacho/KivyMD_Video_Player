import os, shutil, tkinter as tk
from kivymd.app import MDApp
from libs.playlist_manipulation import feed_playlist, delete_from_playlist, get_listindex

from send2trash import send2trash # for sending files to recycle bin


valid_video_formats = ['mp4', 'avi', 'wmv', 'mkv', 'mov', 'm4a', '3gp', '3g2', 'webm', 'flv']
files = []

def get_new_videofile(callback, *args):
        """ calls a function to get a new filename, gives this file to the videoplayer to start"""

        newfile = openmediafile()

        app = MDApp.get_running_app()
        
        feed_playlist([newfile])

        print(f"newfile: {newfile}")
        callback(newfile)


def open_file_dialog(appdir="base"):
    """
        TKinter filedialog open and return filename
    
        appdir: [Bool]  True = use current working directory + "/assets"
                        False = use folder given in myControl.init_dir
    """

    from tkinter import filedialog
    
    root = tk.Tk()

    ###startdir = f"{os.getcwd()}/assets/profiles" if appdir else MDApp.get_running_app().myControl.init_dir
    startdir = set_startdir(appdir)
    
    root.withdraw()
    return filedialog.askopenfilename(title='Select Media File', initialdir=startdir)

def openjsonfile(appdir="base"):
    """
        function to open file and check if format is json.

        Set appdir to True so to start with "special" directory (cwd+ /assets/profiles)...
     
       """
     
    newfile = open_file_dialog(appdir)

    ext = newfile[newfile.rfind('.')+1:].lower()

    return newfile if ext in ["json"] else openjsonfile()


def openmediafile():
    """ open file with file open dialog and return path and filename if file is a valid video file"""

    newfile = open_file_dialog()

    return newfile if check_right_videoformat(newfile) else openmediafile()
    # TODO: Abbruch bei Button abbrechen auslösen


def set_startdir(appdir):
    """
        return folder in which file and folder dialog boxes shall start.

        appdir (str): "base", "profiles" or "playlists" to return the corresponding value    
    """

    match appdir:
        case "base":
            return MDApp.get_running_app().myControl.init_dir
        
        case "profiles":
            return f"{os.getcwd()}/assets/profiles"

        case "playlists":
            return f"{os.getcwd()}/assets/playlists"


def open_savefile_dialog(appdir="base"):
    """
        TKinter filedialog for saving a file.
        
        appdir: [Bool]  True = use current working directory + "/assets/profiles"
                        False = use folder given in myControl.init_dir
    
    """

    from tkinter import filedialog
    
    root = tk.Tk()

    ###startdir = f"{os.getcwd()}/assets/profiles" if appdir else MDApp.get_running_app().myControl.init_dir
    startdir = set_startdir(appdir)

    
    root.withdraw()

    return filedialog.asksaveasfile(initialfile = 'Untitled.json', initialdir=startdir, defaultextension=".json", 
                                    filetypes=[("All Files","*.*"),("json Documents","*.json")]).name

# TODO: handle cancel / exit!!!


def openmediafolder():
    """ open folder with folder open dialog and return list of valid files """

    from tkinter import filedialog
    
    root = tk.Tk()
    root.withdraw()

    startdir = MDApp.get_running_app().myControl.init_dir

    folder = filedialog.askdirectory(title='Select Folder', initialdir=startdir)

    return get_files_from_folder(folder) if folder != '' else ''


def get_files_from_folder(dirpath):

    # check file or folder or different

    for item in os.listdir(dirpath):
        joined = join_path_with_file(dirpath, item)

        if os.path.isfile(joined):
            if check_right_videoformat(joined):
                files.append(joined)

        elif os.path.isdir(joined):

            if MDApp.get_running_app().myControl.allow_subfolders:
                get_files_from_folder(joined)
            else:
                continue
    
    return files 

    # TODO: also take videos from subfolders, maybe optional --> OK
    # TODO: Abbruch bei Button abbrechen auslösen


def check_file_exist(filename):
    """ returns true if file exists """

    return os.path.isfile(filename) 



def set_folder():
    """ select a folder from dialog,
        but don't get the content, get the folder (path) itself!
    """
    from tkinter import filedialog
    
    root = tk.Tk()
    root.withdraw()

    startdir = MDApp.get_running_app().myControl.init_dir
    
    return filedialog.askdirectory(title='Select Folder', initialdir=startdir)


def check_right_videoformat(filename):
    """ returns true or false depending on file extension matches right criteria """
    
    return True if get_file_extension(filename) in valid_video_formats else False
    # TODO: do also allow pictures...
        

def get_file_extension(filename):
    """ returns the extension of a file as string (f.e. 'mp4') """
    
    return filename[filename.rfind(".")+1:].lower()


def join_path_with_file(path, fileName):
    """ merge path and filename to one string"""

    return os.path.join(path, fileName).replace("\\","/")


def deletefile(vpath, *args):
    """ 
        deletes selected file from system. Eventually put file in recycle bin 
    
        drop *args is from clock schedule function...
    """
    recycle = MDApp.get_running_app().myControl.put_in_r_bin

    match recycle:
            case True:
                print(f"send {vpath} to Recycle Bin!")
                send2trash(vpath.replace("/","\\")) # try to use "\\" instead of "/"
            case False:
                print(f"Delete {vpath}! ")
                os.remove(vpath)

    return True


def delete_all_inside_a_folder(fpath):
        """ clean up the folder for the thumbnails. """

        t_files = os.listdir(fpath)

        countfiles = len(t_files)
        print(f"{countfiles} files from thumbs will be removed!")

        for t_file in t_files:
            deletefile = join_path_with_file(fpath, t_file)
            os.remove(deletefile)

        return countfiles


def remove_empty_folder():
    """  """
    # TODO: wenn dateien löschen einen leeren Ordner hinterlässt, diesen evtl löschen: os.rmdir("folder")

    # count files in folder
    # wenn keine files mehr vorhanden, lösche den letzten Folder, 

    # recursion: tue das bis kein leerer folder kommt oder laufwerk/root oder bis zu predefined folder



def movefile(old_path, new_path, *args):
    """ moves selected file to new location. specified in new_path """

    # TODO: handle file already exists in a proper way 

    try:
        shutil.move(old_path, new_path)
    except:
        f_name = old_path[old_path.rfind('/')+1:old_path.rfind('.')]+ "_002"
        ext = old_path[old_path.rfind('.'):]

        next_path = new_path + "/" + f_name + ext

        shutil.move(old_path, next_path)

    return True

