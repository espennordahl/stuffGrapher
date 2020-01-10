import sys
import logging
import argparse

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import qdarkstyle

from ui.mainwindow import MainWindow


if __name__ == "__main__":    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--debug',
        help="Print lots of debugging statements",
        action="store_const", dest="loglevel", const=logging.DEBUG,
        default=logging.WARNING,
    )
    parser.add_argument(
        '-v', '--verbose',
        help="Be verbose",
        action="store_const", dest="loglevel", const=logging.INFO,
    )
    args = parser.parse_args()    
    logging.basicConfig(level=args.loglevel)

    app = QApplication(sys.argv)
    mainWindow = MainWindow()

    # setup stylesheet
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    mainWindow.show()

    sys.exit(app.exec_())
