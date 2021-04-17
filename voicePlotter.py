from gui import MainWindow, app
from PyQt5 import QtCore, QtWidgets, QtGui
import sys


def main():
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
