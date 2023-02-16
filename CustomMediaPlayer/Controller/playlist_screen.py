
from View.PlaylistScreen.playlist_screen import PlaylistScreenView


class PlaylistScreenController:
    """
    The `PlaylistScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, model):
        self.model = model  # Model.playlist_screen.PlaylistScreenModel
        self.view = PlaylistScreenView(controller=self, model=self.model)


    def on_tap_chevron_back(self):
        self.view.manager_screens.current = "main screen"


    def get_view(self) -> PlaylistScreenView:
        return self.view
