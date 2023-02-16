
from kivymd.uix.dialog import MDDialog

from kivymd.uix.boxlayout import MDBoxLayout


from kivy.properties import StringProperty, BooleanProperty, NumericProperty



class DialogRename(MDDialog):
    
    new_folder_name = StringProperty()


class Content(MDBoxLayout):

    text = StringProperty()
