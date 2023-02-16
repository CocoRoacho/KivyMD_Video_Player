
from View.MainScreen.main_screen import MainScreenView


class MainScreenController:
    """
    The `MainScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, model):
        self.model = model  # Model.main_screen.MainScreenModel
        self.view = MainScreenView(controller=self, model=self.model)


    def on_tap_hero(self, hero):
        self.view.manager_screens.current_hero = hero.tag
        self.view.manager_screens.current = "playlist screen"


    def on_click_settings(self):
        self.view.manager_screens.current_hero = ""
        self.view.manager_screens.current = "settings screen"


    def get_view(self) -> MainScreenView:
        return self.view
