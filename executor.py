from check_info import CheckInfo
from gui_application import Application, Menu
from tempfile import TemporaryDirectory


with TemporaryDirectory() as temp_directory:
    app = Application(CheckInfo(temp_directory))
    app.add_menu(Menu)
    app.mainloop()
