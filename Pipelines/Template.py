import sys
import os
from os.path import join as pjoin
from os.path import exists as pexists
# from dicom2bids import *
import logging
from PyQt5.QtCore import (QSize,
                          Qt,
                          QModelIndex,
                          QMutex,
                          QObject,
                          QThread,
                          pyqtSignal,
                          QRunnable,
                          QThreadPool)
from PyQt5.QtWidgets import (QDesktopWidget,
                             QApplication,
                             QWidget,
                             QPushButton,
                             QMainWindow,
                             QLabel,
                             QLineEdit,
                             QVBoxLayout,
                             QHBoxLayout,
                             QFileDialog,
                             QDialog,
                             QTreeView,
                             QFileSystemModel,
                             QGridLayout,
                             QPlainTextEdit,
                             QMessageBox,
                             QListWidget,
                             QTableWidget,
                             QTableWidgetItem,
                             QMenu,
                             QAction,
                             QTabWidget,
                             QCheckBox)
from PyQt5.QtGui import (QFont,
                         QIcon)
import traceback
import threading
import subprocess
import pandas as pd
import platform
import json
from bids_validator import BIDSValidator
import time


# from my_logging import setup_logging
from tqdm.auto import tqdm


def launch(parent):
    window = MainWindow(parent)
    window.show()

class MainWindow(QMainWindow):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.bids = self.parent.bids

        self.setWindowTitle("Template")
        self.window = QWidget(self)
        self.setCentralWidget(self.window)
        self.center()
        
        self.tab = TemplateTab(self)
        layout = QVBoxLayout()
        layout.addWidget(self.tab)

        self.window.setLayout(layout)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

class TemplateTab(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.bids = self.parent.bids
        self.setMinimumSize(500, 200)
        
        self.label = QLabel("This is a Template Pipeline")
        self.button = QPushButton("Pipeline Action")
        self.button.clicked.connect(self.action)
        
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        
        self.setLayout(layout)

    def action(self):
        self.thread = QThread()
        self.action = ActionWorker()
        self.action.moveToThread(self.thread)
        self.thread.started.connect(self.action.run)
        self.action.finished.connect(self.thread.quit)
        self.action.finished.connect(self.action.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
        
        self.parent.hide()


class ActionWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self):
        super().__init__()

    def run(self):
        # Action
        logging.info('Beginning of the action')
        time.sleep(10)
        logging.info('End of the action')
        self.finished.emit()


