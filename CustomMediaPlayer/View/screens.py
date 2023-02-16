# The screens dictionary contains the objects of the models and controllers
# of the screens of the application.


from Controller.main_screen import MainScreenController
from Controller.playlist_screen import PlaylistScreenController
from Controller.options_screen import OptionsScreenController

from Model.main_screen import MainScreenModel
from Model.playlist_screen import PlaylistScreenModel
from Model.options_screen import OptionsScreenModel

screens = {
    "main screen": {
        "model": MainScreenModel,
        "controller": MainScreenController,
    },
    "playlist screen": {
        "model": PlaylistScreenModel,
        "controller": PlaylistScreenController,
    },
    "settings screen": {
        "model": OptionsScreenModel,
        "controller": OptionsScreenController,
    },
}