# Simple test that Nuitka can build a tk gui app with drag and drop library imported.
# ref: https://github.com/Nuitka/Nuitka/issues/1562

from tkinterdnd2 import *


ws = TkinterDnD.Tk()
ws.mainloop()
