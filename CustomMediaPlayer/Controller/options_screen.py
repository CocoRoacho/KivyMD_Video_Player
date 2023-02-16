
from View.OptionsScreen.options_screen import OptionsScreenView


class OptionsScreenController:
    """
    The `OptionsScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, model):
        self.model = model  # Model.options_screen.OptionsScreenModel
        self.view = OptionsScreenView(controller=self, model=self.model)


    def on_tap_chevron_back(self):
        self.view.manager_screens.current = "main screen"


    def get_view(self) -> OptionsScreenView:
        return self.view
