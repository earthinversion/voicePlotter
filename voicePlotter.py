from gui import main as guiMain
from gui import main, app
from PyQt5 import QtCore, QtWidgets, QtGui
import sys


def main(guiMain=guiMain):
    mainWindow = guiMain()
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()