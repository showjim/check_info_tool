from src.check_info import CheckInfo
from src.gui_application import Application, Menu
from tempfile import TemporaryDirectory

def _quit():
    app.quit()
    app.destroy()

with TemporaryDirectory() as temp_directory:
    CheckInfo_Inst = CheckInfo(temp_directory)
    app = Application(CheckInfo_Inst)
    # delete process when close GUI
    app.protocol("WM_DELETE_WINDOW", _quit)
    app.add_menu(Menu)
    app.mainloop()
