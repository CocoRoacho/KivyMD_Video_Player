from View.base_screen import BaseScreenView

from kivy.properties import StringProperty, BooleanProperty, NumericProperty

from kivymd.app import MDApp

from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton


from View.MainScreen.components.dialogbox import DialogRename, Content

from libs.disk_operations import set_folder, delete_all_inside_a_folder, openjsonfile, open_savefile_dialog
from libs.json_ops import write_json_file, open_json_file



# TODO: Animation on call and exit - animate to come from right and go to right

class OptionsScreenView(BaseScreenView):

    app = MDApp.get_running_app()

    rename_dialog = None
    
    def on_enter(self, *args):
        
        # --> return super().on_enter(*args) --> ????
        super().on_enter(*args)

        self.tiptext("Hint", "")

    def set_values(self):
        """ loads the actual values based on variables to the widgets on settings screen """
        
        self.ids.check_loop.active = self.app.myControl.loop_playlist
        self.ids.check_bin.active = self.app.myControl.put_in_r_bin
        self.ids.check_keep.active = self.app.myControl.keep_in_plist
        self.ids.check_subfolders.active = self.app.myControl.allow_subfolders

        self.ids.set_folder1.text = self.app.myControl.path_folder1
        self.ids.set_folder2.text = self.app.myControl.path_folder2
        self.ids.set_folder3.text = self.app.myControl.path_folder3
        self.ids.set_init_directory.text = self.app.myControl.init_dir
        self.ids.set_thumbs_folder.text = self.app.myControl.path_thumbnails
        self.ids.set_folder1.name = self.app.myControl.folder_1
        self.ids.set_folder2.name = self.app.myControl.folder_2
        self.ids.set_folder3.name = self.app.myControl.folder_3
        self.ids.set_init_directory.name = "base"
        self.ids.set_thumbs_folder.name = "thumbnails"

    def delete_thumbs(self):
        """ clean up the folder for the thumbnails. """

        counts = delete_all_inside_a_folder(self.app.myControl.path_thumbnails)

        return counts

    def back_to_main_screen(self):
        """ go back to main screen and clean up a little afterwards """

        # save settings to json file
        print(MDApp.get_running_app().write_settings_to_jsonfile())
        
        screen = MDApp.get_running_app().manager_screens.screens[2]

        screen.controller.on_tap_chevron_back()

        self.tiptext("Hint", "")
        
    def save_settings(self):

        # set filename... 
        filename = open_savefile_dialog(appdir="profiles")

        # call function to save settings
        write_json_file(filename, self.app.myControl.create_dict_for_init_json())

        self.tiptext("Hint", "Saved settings in file:", filename)

    def load_settings(self):
        """ load settings and apply them to the programm """

        # select file...
        filename = openjsonfile(appdir="profiles")

        # call function to load settings
        self.app.myControl.update_settings(open_json_file(filename))

        self.set_values()

        self.tiptext("Hint", "Loaded settings from file:", filename)

    def tiptext(self, clr, txt, var=''):
        """ prints a text in the special label on options screen.
        
            args:
                clr: str --> what colorscheme shall be used? ['Hint', 'Error', ...?...]
                txt: str --> text tobe printed
                var: str --> variable text phrase included in the text main text; default = ''
        
        """

        screen = self.app.manager_screens.screens[2]

        screen.ids.lbl_info_panel.theme_text_color = clr
        screen.ids.lbl_info_panel.text = f"{txt} {var}"
        

    def show_rename_folder_dialog(self, fldr):
        """
            rename folders to your likings, f.e. 'edit', 'hot', ... 

            args:
                fldr  = str - contains folder_1, folder_2 or folder_3
        
        """

        # workin on which folder?
        cur_folder = fldr

        content_cls = Content()

        #if not self.rename_dialog: deaktiviert, da es nicht geht, weil die variablen nicht aktuell sind...
        self.rename_dialog = DialogRename(
            title=f"Rename {cur_folder}",
            content_cls=content_cls,
            buttons=[
                MDFlatButton(
                    text="CANCEL", on_release=lambda x:self.rename_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="OK",
                    on_release=lambda x:self.close_rename_dialog(x, content_cls, cur_folder)
                ),
            ]
        )

        self.rename_dialog.open()
    

    def close_rename_dialog(self, obj, cc, fldr):
        """ close dialog and use the new name created for the folder. 
            Apply the new name to myControl.folder..., on needing 'labels' on settings and main screen 
        """

        new_folder_name = cc.ids.text_field_new_name.text

        match fldr:
            case "folder_1":
                self.app.myControl.folder_1 = new_folder_name
                self.name = self.app.myControl.folder_1
                self.app.myControl.btn_folder1.tooltip_text = f"Send to folder: {new_folder_name}"
                self.tiptext("Hint", "Renamed folder 1 to", new_folder_name)
                
            case "folder_2":
                self.app.myControl.folder_2 = new_folder_name
                self.app.myControl.btn_folder2.tooltip_text = f"Send to folder: {new_folder_name}"
                self.tiptext("Hint", "Renamed folder 2 to", new_folder_name)

            case "folder_3":
                self.app.myControl.folder_3 = new_folder_name
                self.app.myControl.btn_folder3.tooltip_text = f"Send to folder: {new_folder_name}"
                self.tiptext("Hint", "Renamed folder 3 to", new_folder_name)

        # close dialog
        self.rename_dialog.dismiss()
        self.set_values()


class ClickableTextField(MDRelativeLayout):

    name = StringProperty() #"edit", "hot", "hottest"...
    
    text = StringProperty()
    hint_text = StringProperty()
    helper_text = StringProperty()
    belong_to = StringProperty()
    button_text = StringProperty()
    visible = NumericProperty(1)
    disable = BooleanProperty(False)

    def apply_path(self):

        # apply path to textfield
        self.text = str(set_folder())

        # apply path to variable in Class myControl
        app = MDApp.get_running_app()
        screen = app.manager_screens.screens[2]

        match self.belong_to:
            case "folder_1":
                app.myControl.path_folder1 = self.text
                screen.tiptext("Hint", "Your Folder 1 directory is:", self.text)

            case "folder_2":
                app.myControl.path_folder2 = self.text
                screen.tiptext("Hint", "Your Folder 2 directory is:", self.text)

            case "folder_3":
                app.myControl.path_folder3 = self.text
                screen.tiptext("Hint", "Your Folder 3 directory is:", self.text)
                
            case "init_dir":
                app.myControl.init_dir = self.text
                screen.tiptext("Hint", "Your main directory is:", self.text)
            
            case "thumbs":
                app.myControl.path_thumbnails = self.text
                screen.tiptext("Hint", "Your thumbnails directory is:", self.text)
            
            case _:
                screen.tiptext("Error", "This case is not set up:", self.belong_to)
                

    def button_clicked(self, obj):
        """
            when button clicked, rename folder from 'edit', 'hot' or 'hottest' to your liking.
            show a hint of what is done on a label on the lower end of the screen...

            Args:
                obj (str): rootobject from the clicked button #keeps the text of the button to do the right action for every Button
        """
        
        app = MDApp.get_running_app()
        screen = app.manager_screens.screens[2]

        match obj.button_text:

            case "Rename Folder":
                # open entry dialog for entering new name
                screen.show_rename_folder_dialog(fldr=obj.belong_to)
                
            case "Clear thumbs   ":
                screen.tiptext("Hint", "Removed files from thumbnails folder:", screen.delete_thumbs())

            case _:
                screen.tiptext("Error", "This case is not set up:", self.belong_to)


class CheckItem(MDFloatLayout):
    text = StringProperty()
    belong_to = StringProperty()
    active = BooleanProperty()
    
    def on_select(self, argx):
        """ when called you get 1 arg type tuple.
        
            (state (Bool), belonging (str))
        """

        app = MDApp.get_running_app()
        screen = app.manager_screens.screens[2]

        match argx[1]:
            case "loop_pl":
                app.myControl.loop_playlist = argx[0]
                screen.tiptext("Hint", "Looping the Playlist:", argx[0])

            case "r_bin":
                app.myControl.put_in_r_bin = argx[0]
                screen.tiptext("Hint", "Use Recycle bin:", argx[0])

            case "keep_files":
                app.myControl.keep_in_plist = argx[0]
                screen.tiptext("Hint", "Keep files in Playlist:", argx[0])

            case "subfolders":
                app.myControl.allow_subfolders = argx[0]
                screen.tiptext("Hint", "Load files from sub folders:", argx[0])

            case _:
                screen.tiptext("Error", "This case is not set up:", argx[1])
