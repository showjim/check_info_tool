from check_info import CheckInfo
from gui_application import Application, Menu
from tempfile import TemporaryDirectory


with TemporaryDirectory() as temp_directory:
    CheckInfo_Inst = CheckInfo(temp_directory)
    app = Application(CheckInfo_Inst)
    app.add_menu(Menu)
    app.mainloop()
