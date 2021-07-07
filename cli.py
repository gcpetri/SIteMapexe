from SiteMap.main import Dashboard
from PyQt5 import QtWidgets
import sys

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Dashboard()
    app.exec()