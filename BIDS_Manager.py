#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 14:25:40 2021

@author: ColinVDB
BIDS MANAGER GUI
"""

import output_redirection_tools # KEEP ME !!!

import time
import sys
import os
from os.path import join as pjoin
from os.path import exists as pexists
from dicom2bids import *
import logging
from PyQt5.QtCore import (QSize, 
                          Qt, 
                          QModelIndex, 
                          QMutex, 
                          QObject, 
                          QThread, 
                          pyqtSignal, 
                          pyqtSlot,
                          QRunnable, 
                          QThreadPool, 
                          QProcess)
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
                             QTextEdit,
                             QMessageBox, 
                             QListWidget, 
                             QTableWidget, 
                             QTableWidgetItem, 
                             QMenu, 
                             QAction)
from PyQt5.QtGui import (QFont, 
                         QIcon, 
                         QTextCursor)
import traceback
import threading
import subprocess
import pandas as pd
import platform
import json
from bids_validator import BIDSValidator
import faulthandler

from config import config_dict, STDOUT_WRITE_STREAM_CONFIG, TQDM_WRITE_STREAM_CONFIG, STREAM_CONFIG_KEY_QUEUE, \
    STREAM_CONFIG_KEY_QT_QUEUE_RECEIVER
from my_logging import setup_logging

faulthandler.enable()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.memory = {}
        try:
            memory_df = pd.read_pickle('memory.xz')
            self.memory = memory_df.to_dict()
            for key in self.memory.keys():
                self.memory[key] = self.memory[key][0]
        except FileNotFoundError:
            memory_df = {}
        self.system = platform.system()

        self.pipelines = {}
        self.pipelines_name = []

        for root, dirs, files in os.walk('Pipelines'):
            for file in files:
                if '.json' in file:
                    f = open(pjoin(root,file))
                    jsn = json.load(f)
                    self.pipelines_name.append(jsn.get('name'))
                    import_name = jsn.get('import_name')
                    attr = jsn.get('attr')
                    self.pipelines[jsn.get('name')] = jsn
                    self.pipelines[jsn.get('name')]['import'] = __import__(f'Pipelines.{import_name}', globals(), locals(), [attr], 0)
                    # self.pipelines[jsn.get('name')]['launcher'] = self.pipelines[jsn.get('name')]['import'].
                    f.close()

        # Create menu bar and add action
        self.menu_bar = self.menuBar()
        self.PipelinesMenu = self.menu_bar.addMenu('&Pipelines')

        for pipe in self.pipelines_name:
            new_action = QAction(f'&{pipe}', self)
            new_action.triggered.connect(lambda checked, arg=pipe: self.launch_pipeline(arg))
            self.PipelinesMenu.addAction(new_action)
        
        self.threads_pool = QThreadPool.globalInstance()
        
        
        # self.sys_stdout = sys.stdout
        # self.sys_stderr = sys.stderr
        # sys.stdout = logging.info
        # sys.stderr = logging.error

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('BIDS Manager')
        self.setWindowIcon(QIcon('bids_icon.png'))
        self.window = QWidget(self)
        self.setCentralWidget(self.window)
        self.window.closeEvent = self.closeEvent
        
        self.center()

        self.bids_dir = str(QFileDialog.getExistingDirectory(self, "Select BIDS Directory"))
        while self.bids_dir=="":
            self.bids_dir = str(QFileDialog.getExistingDirectory(self, "Please, select BIDS Directory"))

        self.dcm2niix_path = self.memory.get('dcm2niix_path')

        self.bids = BIDSHandler(root_dir=self.bids_dir, dicom2niix_path=self.dcm2niix_path)
        bids_dir_split = self.bids_dir.split('/')
        self.bids_name = bids_dir_split[len(bids_dir_split)-1]
        self.bids_lab = QLabel(self.bids_name)
        self.bids_lab.setFont(QFont('Calibri', 30))

        self.bids_dir_view = BidsDirView(self)

        self.bids_metadata = BidsMetadata(self)

        self.bids_actions = BidsActions(self)

        # self.bids_dialog = BidsDialog(self)
# =============================================================================
#         New logging
# =============================================================================
        setup_logging(self.__class__.__name__)

        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__logger.setLevel(logging.DEBUG)

        self.queue_std_out = config_dict[STDOUT_WRITE_STREAM_CONFIG][STREAM_CONFIG_KEY_QUEUE]
 
        self.text_edit_std_out = StdOutTextEdit(self)
        
        # std out stream management
        # create console text read thread + receiver object
        self.thread_std_out_queue_listener = QThread()
        self.std_out_text_receiver = config_dict[STDOUT_WRITE_STREAM_CONFIG][STREAM_CONFIG_KEY_QT_QUEUE_RECEIVER]
        # connect receiver object to widget for text update
        self.std_out_text_receiver.queue_std_out_element_received_signal.connect(self.text_edit_std_out.append_text)
        # attach console text receiver to console text thread
        self.std_out_text_receiver.moveToThread(self.thread_std_out_queue_listener)
        # attach to start / stop methods
        self.thread_std_out_queue_listener.started.connect(self.std_out_text_receiver.run)
        self.thread_std_out_queue_listener.finished.connect(self.thread_std_out_queue_listener.deleteLater)
        self.thread_std_out_queue_listener.start()
# =============================================================================
# 
# =============================================================================

        validator = BIDSValidator()
        if not validator.is_bids(self.bids_dir):
            logging.warning('/!\ Directory is not considered as a valid BIDS directory !!!')

        layout = QGridLayout()
        layout.addWidget(self.bids_lab, 0, 1, 1, 2)
        layout.addWidget(self.bids_dir_view, 0, 0, 3, 1)
        layout.addWidget(self.bids_metadata, 1, 1)
        layout.addWidget(self.bids_actions, 1, 2)
        layout.addWidget(self.text_edit_std_out, 2, 1, 1, 2)

        self.window.setLayout(layout)

        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        # time.sleep(3)
        memory_df = pd.DataFrame(self.memory, index=[0])
        memory_df.to_pickle('memory.xz')
        # output_redirection_tools.delete_config_dict(config_dict)
        self.std_out_text_receiver.deleteLater()
        self.std_out_text_receiver.stop()
        self.thread_std_out_queue_listener.quit()
        self.thread_std_out_queue_listener.wait()
    
    def close(self):
        # time.sleep(3)
        memory_df = pd.DataFrame(self.memory, index=[0])
        # output_redirection_tools.delete_config_dict(config_dict)
        self.std_out_text_receiver.deleteLater()
        self.std_out_text_receiver.stop()
        self.thread_std_out_queue_listener.quit()
        self.thread_std_out_queue_listener.wait()

    def update_bids(self):
        logging.info("update_bids!")
        # bids_dir_split = self.bids.root_dir.split('/')
        # self.bids_name = bids_dir_split[len(bids_dir_split)-1]
        # self.bids_lab.setText(self.bids_name)
        # self.bids_metadata.update_metadata()
        # self.bids_dir_view.update_dir()

        bids_dir = str(QFileDialog.getExistingDirectory(self, "Select BIDS Directory"))
        if os.path.isdir(bids_dir):
            self.bids_dir = bids_dir
            self.bids = BIDSHandler(root_dir=self.bids_dir, dicom2niix_path="dcm2niix")
            bids_dir_split = self.bids_dir.split('/')
            self.bids_name = bids_dir_split[len(bids_dir_split)-1]
            self.bids_lab = QLabel(self.bids_name)
            self.bids_lab.setFont(QFont('Calibri', 30))

            self.bids_dir_view = BidsDirView(self)

            self.bids_metadata = BidsMetadata(self)

            self.bids_actions.update_bids(self)

            layout = QGridLayout()
            layout.addWidget(self.bids_lab, 0, 1, 1, 2)
            layout.addWidget(self.bids_dir_view, 0, 0, 3, 1)
            layout.addWidget(self.bids_metadata, 1, 1)
            layout.addWidget(self.bids_actions, 1, 2)
            layout.addWidget(self.text_edit_std_out, 2, 1, 1, 2)
            self.window = QWidget(self)
            self.setCentralWidget(self.window)
            self.window.setLayout(layout)
        else:
            pass

    def launch_pipeline(self, pipe):
        self.pipelines[pipe]['import'].launch(self)
        

# class OpeningWindow(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.init_ui()

#     def init_ui(self):
#         self.setWindowTitle('OpeningWindow')
#         self.center()

#         label = QLabel("Select or Create your BIDS Directory")

#         button = QPushButton('Browse')
#         button.clicked.connect(self.browse)

#         layout = QVBoxLayout()
#         layout.addWidget(label)
#         layout.addWidget(button)

#         self.setLayout(layout)

#     def center(self):
#         qr = self.frameGeometry()
#         cp = QDesktopWidget().availableGeometry().center()
#         qr.moveCenter(cp)
#         self.move(cp)

#     def browse(self):
#         logging.info('Browse')
#         self.folderpath = QFileDialog.getExistingDirectory(self, 'Select Folder')

#         logging.info(self.folderpath)

    # def closeEvent(self, event):
    #     sys.stdout = self.sys_stdout
    #     sys.stderr = self.sys_stderr

    # def close(self):
    #     sys.stdout = self.sys_stdout
    #     sys.stderr = self.sys_stderr
        

class BidsDirView(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.bids = self.parent.bids
        self.threads_pool = self.parent.threads_pool
        dir_path = self.parent.bids_dir
        self.setWindowTitle('File System Viewer')
        self.setMinimumSize(250, 700)

        self.model = QFileSystemModel()
        self.model.setRootPath(dir_path)
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(dir_path))
        self.tree.setColumnWidth(0,250)
        self.tree.setAlternatingRowColors(True)
        self.tree.doubleClicked.connect(self.treeMedia_doubleClicked)
        self.tree.setDragEnabled(True)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.openMenu)
        self.threads = []
        
        self.itksnap = None

        layout = QVBoxLayout()
        layout.addWidget(self.tree)
        self.setLayout(layout)

    def update_dir(self):
        self.model = QFileSystemModel()
        self.model.setRootPath(self.parent.bids_dir)
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self.parent.bids_dir))

    def treeMedia_doubleClicked(self, index):
        item = self.tree.selectedIndexes()[0]
        item_path = item.model().filePath(index)
        if os.path.isfile(item_path):
            logging.info(f"[INFO] Opening {item_path}")
            if '.nii' in item_path:
                self.itksnap = self.parent.memory.get('itksnap')
                if self.itksnap == None:
                    logging.info(f'No application selected open MRI \n \t Please select itksnap path')
                else:
                    print(self.itksnap)
                    # subprocess.call([self.itksnap, '-g', f"{item_path}"])
                    # operation = RunnableSubprocess(f'{self.itksnap} -g {item_path}')
                    # self.parent.threads_pool.start(operation)
                    self.threads.append(QThread())
                    self.operation = SubprocessWorker(f'{self.itksnap} -g {item_path}')
                    self.operation.moveToThread(self.threads[-1])
                    self.threads[-1].started.connect(self.operation.run)
                    self.operation.finished.connect(self.threads[-1].quit)
                    self.operation.finished.connect(self.operation.deleteLater)
                    self.threads[-1].finished.connect(self.threads[-1].deleteLater)
                    self.threads[-1].start()
            else:
                if self.parent.system == 'Linux':
                    # subprocess.call(['xdg-open', f"{item_path}"])
                    # operation = RunnableSubprocess(f'xdg-open {item_path}')
                    # self.parent.threads_pool.start(operation)
                    self.threads.append(QThread())
                    self.operation = SubprocessWorker(f'xdg-open {item_path}')
                    self.operation.moveToThread(self.threads[-1])
                    self.threads[-1].started.connect(self.operation.run)
                    self.operation.finished.connect(self.threads[-1].quit)
                    self.operation.finished.connect(self.operation.deleteLater)
                    self.threads[-1].finished.connect(self.threads[-1].deleteLater)
                    self.threads[-1].start()
                elif self.parent.system == 'Darwin':
                    # subprocess.call(['open', f"{item_path}"])
                    # operation = RunnableSubprocess(f'open {item_path}')
                    # self.parent.threads_pool.start(operation)
                    self.threads.append(QThread())
                    self.operation = SubprocessWorker(f'open {item_path}')
                    self.operation.moveToThread(self.threads[-1])
                    self.threads[-1].started.connect(self.operation.run)
                    self.operation.finished.connect(self.threads[-1].quit)
                    self.operation.finished.connect(self.operation.deleteLater)
                    self.threads[-1].finished.connect(self.threads[-1].deleteLater)
                    self.threads[-1].start()
                elif self.parent.system == 'Windows':
                    # subprocess.call(['start', f"{item_path}"])
                    # operation = RunnableSubprocess(f'start {item_path}')
                    # self.parent.threads_pool.start(operation)
                    self.threads.append(QThread())
                    self.operation = SubprocessWorker(f'start {item_path}')
                    self.operation.moveToThread(self.threads[-1])
                    self.threads[-1].started.connect(self.operation.run)
                    self.operation.finished.connect(self.threads[-1].quit)
                    self.operation.finished.connect(self.operation.deleteLater)
                    self.threads[-1].finished.connect(self.threads[-1].deleteLater)
                    self.threads[-1].start()
                else:
                    logging.warning('The program does not recognize the OS')
        else:
            pass

    def openMenu(self, position):
        menu = QMenu()
        openWith = menu.addAction('Open with')
        openAdd = 'None'
        openSeg = 'None'
        index = self.tree.indexAt(position)
        item = self.tree.selectedIndexes()[0]
        item_path = item.model().filePath(index)
        if '.nii' in item_path:
            if self.itksnap == None:
                self.itksnap = self.parent.memory.get('itksnap')
            if self.itksnap != None:
                openAdd = menu.addAction('Open as additional image')
                openSeg = menu.addAction('Open as segmentation')
        action = menu.exec_(self.tree.viewport().mapToGlobal(position))

        if action == openWith:
            logging.debug('Open With')
            self.itksnap = QFileDialog.getOpenFileName(self, "Select the path to itksnap")[0]
            if self.itksnap != None and self.itksnap != '':
                # subprocess.call([self.itksnap, '-g', item_path])
                # operation = RunnableSubprocess(f'{self.itksnap} -g {item_path}')
                # self.parent.threads_pool.start(operation)
                self.threads.append(QThread())
                self.operation = SubprocessWorker(f'{self.itksnap} -g {item_path}')
                self.operation.moveToThread(self.threads[-1])
                self.threads[-1].started.connect(self.operation.run)
                self.operation.finished.connect(self.threads[-1].quit)
                self.operation.finished.connect(self.operation.deleteLater)
                self.threads[-1].finished.connect(self.threads[-1].deleteLater)
                self.threads[-1].start()
                self.parent.memory['itksnap'] = self.itksnap
            else:
                logging.info(f'No application selected open MRI \n \t Please select itksnap path')

        if action == openAdd:
            logging.debug('Open as additional image')
            # subprocess.call([self.itksnap, '-o', item_path])
            # operation = RunnableSubprocess(f'{self.itksnap} -o {item_path}')
            # self.parent.threads_pool.start(operation)
            self.threads.append(QThread())
            self.operation = SubprocessWorker(f'{self.itksnap} -o {item_path}')
            self.operation.moveToThread(self.threads[-1])
            self.threads[-1].started.connect(self.operation.run)
            self.operation.finished.connect(self.threads[-1].quit)
            self.operation.finished.connect(self.operation.deleteLater)
            self.threads[-1].finished.connect(self.threads[-1].deleteLater)
            self.threads[-1].start()

        if action == openSeg:
            logging.debug('Open as segmentation')
            # subprocess.call([self.itksnap, '-s', item_path])
            # operation = RunnableSubprocess(f'{self.itksnap} -s {item_path}')
            # self.parent.threads_pool.start(operation)
            self.threads.append(QThread())
            self.operation = SubprocessWorker(f'{self.itksnap} -s {item_path}')
            self.operation.moveToThread(self.threads[-1])
            self.threads[-1].started.connect(self.operation.run)
            self.operation.finished.connect(self.threads[-1].quit)
            self.operation.finished.connect(self.operation.deleteLater)
            self.threads[-1].finished.connect(self.threads[-1].deleteLater)
            self.threads[-1].start()



# class BidsDirView(QWidget):

#     def __init__(self, dir_path):
# 		super().__init__()
#         self.setWindowTitle('File System Viewer')
# 		self.setMinimumSize(250, 700)

# 		self.model = QFileSystemModel()
# 		self.model.setRootPath(dir_path)
# 		self.tree =  QTreeView()
# 		self.tree.setModel(self.model)
# 		self.tree.setRootIndex(self.model.index(dir_path))
# 		self.tree.setColumnWidth(0, 250)
# 		self.tree.setAlternatingRowColors(True)

# 		layout = QVBoxLayout()
# 		layout.addWidget(self.tree)
# 		self.setLayout(layout)

class BidsMetadata(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.bids = self.parent.bids
        self.number_of_subjects = QLabel(f"Number of subjects: {self.bids.number_of_subjects}")
        self.number_of_subjects.setFont(QFont('Calibri', 15))

        layout = QVBoxLayout()
        layout.addWidget(self.number_of_subjects)

        dataset_description = self.bids.get_dataset_description()
        bids_version = dataset_description.get('BIDSVersion')
        authors = dataset_description.get('Authors')

        self.bids_version = QLabel(f"BIDSVersion: {bids_version}")
        self.bids_version.setFont(QFont('Calibri', 12))
        layout.addWidget(self.bids_version)

        authors_lab = f"Authors: "
        authors = authors if authors != None else []
        for author in authors:
            if author == authors[-1]:
                authors_lab = authors_lab + author
            else:
                authors_lab = authors_lab + f'{author}\n         '
        self.authors = QLabel(authors_lab)
        self.authors.setFont(QFont('Calibri', 12))
        layout.addWidget(self.authors)

        self.setLayout(layout)

    def update_metadata(self):
        self.bids = self.parent.bids
        self.bids.update_number_of_subjects()
        self.number_of_subjects.setText(f"Number of subjects: {self.bids.number_of_subjects}")
        dataset_description = self.bids.get_dataset_description()
        bids_version = dataset_description.get('BIDSVersion')
        authors = dataset_description.get('Authors')
        authors_lab = f"Authors: "
        authors = authors if authors != None else []
        for author in authors:
            if author == authors[-1]:
                authors_lab = authors_lab + author
            else:
                authors_lab = authors_lab + f'{author}\n         '
        self.bids_version.setText(f"BIDSVersion: {bids_version}")
        self.authors.setText(authors_lab)

class BidsActions(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.bids = self.parent.bids
        self.threads_pool = self.parent.threads_pool

        self.change_bids_dir_button = QPushButton("Change BIDS Directory")
        self.change_bids_dir_button.clicked.connect(self.change_bids_dir)

        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add)

        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove)

        self.rename_sub_button = QPushButton("Rename subject")
        self.rename_sub_button.clicked.connect(self.rename_sub)

        self.rename_ses_button = QPushButton("Rename session")
        self.rename_ses_button.clicked.connect(self.rename_ses)

        self.rename_seq_button = QPushButton("Rename sequence")
        self.rename_seq_button.clicked.connect(self.rename_seq)

        self.update_authors_button = QPushButton("Update authors")
        self.update_authors_button.clicked.connect(self.update_authors)

        # layout = QVBoxLayout()
        # sub_layout = QHBoxLayout()
        # sub_layout.addWidget(self.add_button)
        # sub_layout.addWidget(self.remove_button)
        # sub_layout_1 = QHBoxLayout()
        # sub_layout_1.addWidget(self.rename_sub_button)
        # sub_layout_1.addWidget(self.rename_ses_button)
        # layout.addWidget(self.change_bids_dir_button)
        # layout.addLayout(sub_layout)
        # layout.addLayout(sub_layout_1)

        layout = QGridLayout()
        layout.addWidget(self.change_bids_dir_button, 0, 0, 1, 2)
        layout.addWidget(self.add_button, 1, 0, 1, 1)
        layout.addWidget(self.remove_button, 1, 1, 1, 1)
        layout.addWidget(self.rename_sub_button, 2, 0, 1, 1)
        layout.addWidget(self.rename_ses_button, 2, 1, 1, 1)
        layout.addWidget(self.rename_seq_button, 3, 0, 1, 1)
        layout.addWidget(self.update_authors_button, 3, 1, 1, 1)

        self.setLayout(layout)

    def change_bids_dir(self):
        logging.info("change_bids_dir")
        # bids_dir = str(QFileDialog.getExistingDirectory(self, "Select BIDS Directory"))
        # if os.path.isdir(bids_dir):
        #     self.bids = BIDSHandler(root_dir=bids_dir, dicom2niix_path="dcm2niix")
        #     self.parent.bids = self.bids
        #     self.parent.update_bids()
        self.parent.update_bids()

    def add(self):
        logging.info("add")
        if hasattr(self, 'add_win'):
            del self.add_win
        self.add_win = AddWindow(self)
        if not self.parent.dcm2niix_path:
            # ajouter une fenetre
            path = QFileDialog.getOpenFileName(self, "Select 'dcm2niix.exe' path")[0]
            self.parent.dcm2niix_path = path
            self.parent.memory['dcm2niix_path'] = path
            self.bids.setDicom2niixPath(self.parent.dcm2niix_path)
        self.add_win.show()

    def remove(self):
        logging.info("remove")
        if hasattr(self, 'rm_win'):
            del self.rm_win
        self.rm_win = RemoveWindow(self)
        self.rm_win.show()

    def rename_sub(self):
        logging.info("rename_sub")
        if hasattr(self, 'renameSub_win'):
            del self.renameSub_win
        self.renameSub_win = RenameSubject(self)
        self.renameSub_win.show()

    def rename_ses(self):
        logging.info("rename_ses")
        if hasattr(self, 'renameSes_win'):
            del self.renameSes_win
        self.renameSes_win = RenameSession(self)
        self.renameSes_win.show()

    def update_bids(self, parent):
        self.parent = parent
        self.bids = self.parent.bids

    def rename_seq(self):
        logging.info("rename_seq")
        if hasattr(self, 'renameSeq_win'):
            del self.renameSeq_win
        self.renameSeq_win = RenameSequence(self)
        self.renameSeq_win.show()

    def update_authors(self):
        logging.info("update_authors")
        if hasattr(self, 'updateAuthors_win'):
            del self.updateAuthors_win
        self.updateAuthors_win = UpdateAuthors(self)
        self.updateAuthors_win.show()
        
    def setEnabledButtons(self, enabled):
        self.change_bids_dir_button.setEnabled(enabled)
        self.add_button.setEnabled(enabled)
        self.remove_button.setEnabled(enabled)
        self.rename_sub_button.setEnabled(enabled)
        self.rename_ses_button.setEnabled(enabled)
        self.rename_seq_button.setEnabled(enabled)
        self.update_authors_button.setEnabled(enabled)


class RemoveWindow(QMainWindow):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.bids = self.parent.bids
        self.threads_pool = self.parent.threads_pool

        self.setWindowTitle("Remove subject or session")
        self.window = QWidget(self)
        self.setCentralWidget(self.window)
        self.center()

        self.label = QLabel("Select subject or session to remove")
        self.label.setAlignment(Qt.AlignHCenter)
        self.subject = QLineEdit(self)
        self.subject.setPlaceholderText('Subject number')
        self.session = QLineEdit(self)
        self.session.setPlaceholderText('Session number')

        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove)

        layout = QGridLayout()
        layout.addWidget(self.label, 0, 0, 1, 2)
        layout.addWidget(self.subject, 1, 0, 1, 1)
        layout.addWidget(self.session, 1, 1, 1, 1)
        layout.addWidget(self.remove_button, 2, 0, 1, 2)

        self.window.setLayout(layout)

    def remove(self):
        subject = self.subject.text()
        session = self.session.text()
        buttonReply = QMessageBox.question(self, 'Remove subject and/or session', "Do you want to delete the raw dicoms?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            logging.info(f"Removing sub-{subject} ses-{session}")
            if subject != "":
                if session != "":
                    # self.bids.delete_session(subject, session, delete_sourcedata=True)
                    # operation = RunnableOperation(self.bids.delete_session, args=[subject, session], kwargs={'delete_sourcedata':True})
                    # self.parent.threads_pool.start(operation)
                    self.parent.setEnabled(False)
                    self.thread = QThread()
                    self.operation = OperationWorker(self.bids.delete_session, args=[subject, session], kwargs={'delete_sourcedata':True})
                    self.operation.moveToThread(self.thread)
                    self.thread.started.connect(self.operation.run)
                    self.operation.finished.connect(self.thread.quit)
                    self.operation.finished.connect(self.operation.deleteLater)
                    self.thread.finished.connect(self.thread.deleteLater)
                    self.thread.start()
                    self.thread.finished.connect(
                        lambda: self.parent.setEnabled(True)
                    )

                    
                else:
                    # self.bids.delete_subject(subject, delete_sourcedata=True)
                    # operation = RunnableOperation(self.bids.delete_subject, args=[subject], kwargs={'delete_sourcedata':True})
                    # self.parent.threads_pool.start(operation)
                    self.parent.setEnabled(False)
                    self.thread = QThread()
                    self.operation = OperationWorker(self.bids.delete_subject, args=[subject], kwargs={'delete_sourcedata':True})
                    self.operation.moveToThread(self.thread)
                    self.thread.started.connect(self.operation.run)
                    self.operation.finished.connect(self.thread.quit)
                    self.operation.finished.connect(self.operation.deleteLater)
                    self.thread.finished.connect(self.thread.deleteLater)
                    # self.operation.logHandler.log.signal.connect(self.write_log)
                    self.thread.start()
                    self.thread.finished.connect(
                        lambda: self.parent.setEnabled(True)
                    )
        else:
            logging.info(f"Removing sub-{subject} ses-{session} while keeping the dicoms")
            if subject != "":
                if session != "":
                    # self.bids.delete_session(subject, session)
                    # operation = RunnableOperation(self.bids.delete_session, args=[subject, session])
                    # self.parent.threads_pool.start(operation)
                    self.parent.setEnabled(False)
                    self.thread = QThread()
                    self.operation = OperationWorker(self.bids.delete_session, args=[subject, session])
                    self.operation.moveToThread(self.thread)
                    self.thread.started.connect(self.operation.run)
                    self.operation.finished.connect(self.thread.quit)
                    self.operation.finished.connect(self.operation.deleteLater)
                    self.thread.finished.connect(self.thread.deleteLater)
                    # self.operation.logHandler.log.signal.connect(self.write_log)
                    self.thread.start()
                    self.thread.finished.connect(
                        lambda: self.parent.setEnabled(True)
                    )
                else:
                    # self.bids.delete_subject(subject)
                    # operation = RunnableOperation(self.bids.delete_subject, args=[subject])
                    # self.parent.threads_pool.start(operation)
                    self.parent.setEnabled(False)
                    self.thread = QThread()
                    self.operation = OperationWorker(self.bids.delete_subject, args=[subject])
                    self.operation.moveToThread(self.thread)
                    self.thread.started.connect(self.operation.run)
                    self.operation.finished.connect(self.thread.quit)
                    self.operation.finished.connect(self.operation.deleteLater)
                    self.thread.finished.connect(self.thread.deleteLater)
                    # self.operation.logHandler.log.signal.connect(self.write_log)
                    self.thread.start()
                    self.thread.finished.connect(
                        lambda: self.parent.setEnabled(True)
                    )
                    
        self.hide()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    # @pyqtSlot(str)
    # def write_log(self, log_text):
    #     logging.info(log_text)

class AddWindow(QMainWindow):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.bids = self.parent.bids
        self.threads_pool = self.parent.threads_pool

        self.setWindowTitle("Add subject or session")
        self.window = QWidget(self)
        self.setCentralWidget(self.window)
        self.center()

        self.list_to_add = []

        self.label = QLabel("Select DICOM folders to add to BIDS directory")
        self.label.setAlignment(Qt.AlignHCenter)
        # self.subject = QLineEdit(self)
        # self.subject.setPlaceholderText('Subject number')
        # self.session = QLineEdit(self)
        # self.session.setPlaceholderText('Session number')
        self.add_folder_button = QPushButton("Add DICOM Folder")
        self.add_folder_button.clicked.connect(self.add_folder)
        self.add_files_button = QPushButton("Add DICOM zip Files")
        self.add_files_button.clicked.connect(self.add_files)
        self.list_view = QTableWidget()
        self.list_view.setMinimumSize(800,200)
        self.list_view.setColumnCount(3)
        self.list_view.setColumnWidth(0, 600)
        self.list_view.setColumnWidth(1, 100)
        self.list_view.setColumnWidth(2, 100)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.setHorizontalHeaderLabels(["path", "subject", "session"])
        self.add_button = QPushButton("Add to BIDS directory")
        self.add_button.clicked.connect(self.add)

        layout = QGridLayout()
        layout.addWidget(self.label, 0, 0, 1, 2)
        # layout.addWidget(self.subject, 1, 0, 1, 1)
        # layout.addWidget(self.session, 1, 1, 1, 1)
        layout.addWidget(self.add_folder_button, 1, 0, 1, 1)
        layout.addWidget(self.add_files_button, 1, 1, 1, 1)
        layout.addWidget(self.list_view, 2, 0, 1, 2)
        layout.addWidget(self.add_button, 3, 0, 1, 2)

        self.window.setLayout(layout)

    def add_folder(self):
        dicom_folder = str(QFileDialog.getExistingDirectory(self, "Select DICOM folder"))
        rowPosition = len(self.list_to_add)
        self.list_view.insertRow(rowPosition)
        # subject = self.subject.text()
        # session = self.session.text()
        # if len(subject) != 3:
        #     subject = None
        # if len(session) != 2:
        #     session = None
        self.list_view.setItem(rowPosition , 0, QTableWidgetItem(dicom_folder))
        self.list_view.setItem(rowPosition , 1, QTableWidgetItem(None))
        self.list_view.setItem(rowPosition , 2, QTableWidgetItem(None))
        # self.list_to_add.append((dicom_folder, subject, session))


    def add_files(self):
        dicom_folder = QFileDialog.getOpenFileName(self, 'Select DICOM zip file')[0]
        rowPosition = len(self.list_to_add)
        self.list_view.insertRow(rowPosition)
        # subject = self.subject.text()
        # session = self.session.text()
        # if len(subject) != 3:
        #     subject = None
        # if len(session) != 2:
        #     session = None
        self.list_view.setItem(rowPosition , 0, QTableWidgetItem(dicom_folder))
        self.list_view.setItem(rowPosition , 1, QTableWidgetItem(None))
        self.list_view.setItem(rowPosition , 2, QTableWidgetItem(None))
        # self.list_to_add.append((dicom_folder, subject, session))

    def add(self):
        #get items
        for i in range(self.list_view.rowCount()):
            self.list_to_add.append((self.list_view.item(i,0).text(), self.list_view.item(i,1).text() if self.list_view.item(i,1).text() != '' else None, self.list_view.item(i,2).text() if self.list_view.item(i,2).text() != '' else None))

        # for item in self.list_to_add:

        #     dicom = item[0]

        #     if ".zip" in dicom:
        #         directory_to_extract_to = dicom[:-4]
        #         with zipfile.ZipFile(dicom, 'r') as zip_ref:
        #             zip_ref.extractall(directory_to_extract_to)
        #         dicom = directory_to_extract_to

        #     DICOM_FOLDER = dicom
        #     PATIENT_ID = item[1]
        #     SESSION = item[2]

        #     try:
        #         # pat_id, session, dicom_series = self.bids.convert_dicoms_to_bids(dicomfolder = DICOM_FOLDER,
        #         #                                                                 pat_id      = PATIENT_ID,
        #         #                                                                 session     = SESSION,
        #         #                                                                 return_dicom_series=True)
        #         operation = RunnableOperation(self.bids.convert_dicoms_to_bids, kwargs={'dicomfolder':DICOM_FOLDER, 'pat_id':PATIENT_ID, 'session':SESSION, 'return_dicom_series':True})
        #         self.parent.threads_pool.start(operation)
        #         operation.finished.connect(lambda last=(item == self.list_to_add[-1]): self.end_add(last))
        #         self.parent.add_button.setEnabled(False)
        #         self.thread = QThread()
        #         self.operation = OperationWorker(self.bids.convert_dicoms_to_bids, kwargs={'dicomfolder':DICOM_FOLDER, 'pat_id':PATIENT_ID, 'session':SESSION, 'return_dicom_series':True})
        #         self.operation.moveToThread(self.thread)
        #         self.thread.started.connect(self.operation.run)
        #         self.operation.finished.connect(self.thread.quit)
        #         self.operation.finished.connect(self.operation.deleteLater)
        #         self.thread.finished.connect(self.thread.deleteLater)
        #         self.thread.start()
        #         self.thread.finished.connect(
        #             lambda: self.parent.add_button.setEnabled(True)
        #         )
        #         self.thread.finished.connect(lambda last=(item == self.list_to_add[-1]): self.end_add(last))
        #         # logging.info(f"[INFO] done for patient {pat_id}")
        #     except Exception as e:
        #         logging.info(f'[ERROR] Dicom to Bids failed for {DICOM_FOLDER}: {e}')
        #         # exc_type, exc_obj, exc_tb = sys.exc_info()
        #         # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        #         # logging.info(exc_type, fname, exc_tb.tb_lineno)
        #         # traceback.logging.info_exc()
        
        self.parent.setEnabled(False)
        self.thread = QThread()
        self.worker = AddWorker(self.bids, self.list_to_add)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # self.worker.logHandler.log.signal.connect(self.write_log)
        # self.thread.finished.connect(lambda: self.parent.setEnabled(True))
        self.thread.finished.connect(lambda: self.end_add())
        self.thread.start()
        
        self.hide()
        
    def end_add(self):
        self.parent.parent.bids_metadata.update_metadata()
        logging.info(f'All done.')
        self.parent.setEnabled(True)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    # @pyqtSlot(str)
    # def write_log(self, log_text):
    #     logging.info(log_text)

class RenameSubject(QMainWindow):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.bids = self.parent.bids
        self.threads_pool = self.parent.threads_pool

        self.setWindowTitle("Rename Subject")
        self.window = QWidget(self)
        self.setCentralWidget(self.window)
        self.center()

        self.old_sub = QLineEdit(self)
        self.old_sub.setPlaceholderText("Old Subject ID")
        self.new_sub = QLineEdit(self)
        self.new_sub.setPlaceholderText("New Subject ID")
        self.rename_button = QPushButton("Rename Subject")
        self.rename_button.clicked.connect(self.rename)

        layout = QGridLayout()
        layout.addWidget(self.old_sub, 0, 0, 1, 1)
        layout.addWidget(self.new_sub, 0, 1, 1, 1)
        layout.addWidget(self.rename_button, 1, 0, 1, 2)

        self.window.setLayout(layout)

    def rename(self):
        old_sub = self.old_sub.text()
        new_sub = self.new_sub.text()

        # self.bids.rename_subject(old_sub, new_sub)
        # operation = RunnableOperation(self.bids.rename_subject, args=[old_sub, new_sub])
        # self.parent.threads_pool.start(operation)
        self.parent.setEnabled(False)
        self.thread = QThread()
        self.operation = OperationWorker(self.bids.rename_subject, args=[old_sub, new_sub])
        self.operation.moveToThread(self.thread)
        self.thread.started.connect(self.operation.run)
        self.operation.finished.connect(self.thread.quit)
        self.operation.finished.connect(self.operation.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # self.operation.logHandler.log.signal.connect(self.write_log)
        self.thread.start()
        self.thread.finished.connect(
            lambda: self.parent.setEnabled(True)
        )
        logging.info(f"sub-{old_sub} renamed to sub-{new_sub}")
        
        self.hide()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    # @pyqtSlot(str)
    # def write_log(self, log_text):
    #     logging.info(log_text)

class RenameSession(QMainWindow):
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.bids = self.parent.bids
        self.threads_pool = self.parent.threads_pool

        self.setWindowTitle("Rename Session")
        self.window = QWidget(self)
        self.setCentralWidget(self.window)
        self.center()
        
        self.sub = QLineEdit(self)
        self.sub.setPlaceholderText("Subject ID")
        self.old_ses = QLineEdit(self)
        self.old_ses.setPlaceholderText("Old Session")
        self.new_ses = QLineEdit(self)
        self.new_ses.setPlaceholderText("New Session")
        self.rename_button = QPushButton("Rename Session")
        self.rename_button.clicked.connect(self.rename)

        layout = QGridLayout()
        layout.addWidget(self.sub, 0, 0, 1, 1)
        layout.addWidget(self.old_ses, 0, 1, 1, 1)
        layout.addWidget(self.new_ses, 1, 1, 1, 1)
        layout.addWidget(self.rename_button, 2, 0, 1, 2)

        self.window.setLayout(layout)
        
    def rename(self):
        sub = self.sub.text()
        old_ses = self.old_ses.text()
        new_ses = self.new_ses.text()
        
        # self.bids.rename_session(sub, old_ses, new_ses)
        # operation = RunnableOperation(self.bids.rename_session, args=[sub, old_ses, new_ses])
        # self.parent.threads_pool.start(operation)
        self.parent.setEnabled(False)
        self.thread = QThread()
        self.operation = OperationWorker(self.bids.rename_session, args=[sub, old_ses, new_ses])
        self.operation.moveToThread(self.thread)
        self.thread.started.connect(self.operation.run)
        self.operation.finished.connect(self.thread.quit)
        self.operation.finished.connect(self.operation.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # self.operation.logHandler.log.signal.connect(self.write_log)
        self.thread.start()
        self.thread.finished.connect(
            lambda: self.parent.setEnabled(True)
        )
        logging.info(f"ses-{old_ses} renamed to ses-{new_ses} for sub-{sub}")
        
        self.hide()
        
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    # @pyqtSlot(str)
    # def write_log(self, log_text):
    #     logging.info(log_text)

class RenameSequence(QMainWindow):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.bids = self.parent.bids
        self.threads_pool = self.parent.threads_pool

        self.setWindowTitle("Rename Sequence")
        self.window = QWidget(self)
        self.setCentralWidget(self.window)
        self.center()

        self.old_seq = QLineEdit(self)
        self.old_seq.setPlaceholderText("Old Sequence")
        self.new_seq = QLineEdit(self)
        self.new_seq.setPlaceholderText("New Sequence")
        self.rename_button = QPushButton("Rename Sequence")
        self.rename_button.clicked.connect(self.rename_seq)

        layout = QGridLayout()
        layout.addWidget(self.old_seq, 0, 0, 1, 1)
        layout.addWidget(self.new_seq, 0, 1, 1, 1)
        layout.addWidget(self.rename_button, 1, 0, 1, 2)

        self.window.setLayout(layout)

    def rename_seq(self):
        old_seq = self.old_seq.text()
        new_seq = self.new_seq.text()

        # self.bids.rename_sequence(old_seq, new_seq)
        # operation = RunnableOperation(self.bids.rename_sequence, args=[old_seq, new_seq])
        # self.parent.threads_pool.start(operation)
        self.parent.setEnabled(False)
        self.thread = QThread()
        self.operation = OperationWorker(self.bids.rename_sequence, args=[old_seq, new_seq])
        self.operation.moveToThread(self.thread)
        self.thread.started.connect(self.operation.run)
        self.operation.finished.connect(self.thread.quit)
        self.operation.finished.connect(self.operation.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # self.operation.logHandler.log.signal.connect(self.write_log)
        self.thread.start()
        self.thread.finished.connect(
            lambda: self.parent.setEnabled(True)
        )
        logging.info(f"old {old_seq} renamed to new {new_seq}")
        
        self.hide()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    # @pyqtSlot(str)
    # def write_log(self, log_text):
    #     logging.info(log_text)

class UpdateAuthors(QMainWindow):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.bids = self.parent.bids
        self.threads_pool = self.parent.threads_pool

        self.setWindowTitle("Update Authors")
        self.window = QWidget(self)
        self.setCentralWidget(self.window)
        self.center()

        self.authors = QLineEdit(self)
        self.authors.setPlaceholderText("Authors")
        self.update_authors_button = QPushButton("Update Authors")
        self.update_authors_button.clicked.connect(self.update_authors)

        layout = QVBoxLayout()
        layout.addWidget(self.authors)
        layout.addWidget(self.update_authors_button)

        self.window.setLayout(layout)

    def update_authors(self):
        authors = self.authors.text()
        if ',' in authors:
            authors_list = authors.split(',')
        else:
            authors_list = [authors]
        # self.bids.update_authors_to_dataset_description(self.bids.root_dir, authors=authors_list)
        # operation = RunnableOperation(self.bids.update_authors_to_dataset_description, args=[self.bids.root_dir], kwargs={'authors':authors_list})
        # self.parent.threads_pool.start(operation)
        self.parent.setEnabled(False)
        self.thread = QThread()
        self.operation = OperationWorker(self.bids.update_authors_to_dataset_description, args=[self.bids.root_dir], kwargs={'authors':authors_list})
        logging.debug('OperationWorker instanciated')
        self.operation.moveToThread(self.thread)
        logging.debug('OperationWorker moved to thread')
        self.thread.started.connect(self.operation.run)
        logging.debug('Thread started and launching operation.run')
        self.operation.finished.connect(self.thread.quit)
        self.operation.finished.connect(self.operation.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # self.operation.logHandler.log.signal.connect(self.write_log)
        self.thread.start()
        self.thread.finished.connect(
            lambda: self.parent.setEnabled(True)
        )
        self.thread.finished.connect(lambda: self.end_update())
        logging.info(f"Updating {authors} as BIDS directory authors")
        # operation.finished.connect(self.end_update)
        self.parent.parent.bids_metadata.update_metadata()
        
        self.hide()
        
    def end_update(self):
        logging.info('Thread ended')
        self.parent.parent.bids_metadata.update_metadata()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    # @pyqtSlot(str)
    # def write_log(self, log_text):
    #     logging.info(log_text)


# class QTextEditLogger(logging.Handler):
#     def __init__(self, parent):
#         super().__init__()
#         self.widget = QPlainTextEdit(parent)
#         self.widget.setReadOnly(True)

#     def emit(self, record):
#         msg = self.format(record)
#         self.widget.appendPlainText(msg)

# class BidsDialog(QDialog, QPlainTextEdit):

#     def __init__(self, parent):
#         super().__init__()
#         self.parent = parent
#         self.bids = self.parent.bids
#         self.threads_pool = self.parent.threads_pool

#         self.setMinimumSize(700,300)

#         logTextBox = QTextEditLogger(self)
#         logTextBox.setFormatter(logging.Formatter('[%(levelname)s] - %(message)s'))
#         self.bids.addLoggerHandler(logTextBox)
#         # logger.addHandler(logTextBox)
#         # logger.setLevel(logging.DEBUG)
#         # self.stdout = sys.stdout
#         # stdout_logger = logging.getLogger('STDOUT')
#         # sl = StreamToLogger(stdout_logger, logging.INFO)
#         # sys.stdout = sl

#         # self._button = QPushButton('Test me')
#         # self._button.clicked.connect(self.test)

#         layout = QVBoxLayout()
#         layout.addWidget(logTextBox.widget)
#         # layout.addWidget(self._button)
#         self.setLayout(layout)

#     # def test(self):
#     #     logging.info('damn, a bug')
#     #     logging.info('something to remember')
#     #     logging.info('that\'s not right')
#     #     logging.info('foobar')

#     # def closeEvent(self, event):
#     #     sys.stdout = self.stdout

#     # def close(self):
#     #     sys.stdout = self.stdout

# class QTextEditLogger(logging.Handler):
#     def __init__(self, parent):
#         super().__init__()
#         self.widget = QPlainTextEdit(parent)
#         self.widget.setReadOnly(True)

#     def emit(self, record):
#         msg = self.format(record)
#         self.widget.appendPlainText(msg)


# class BidsDialog(QDialog):
#     def __init__(self, parent):
#         super().__init__()
#         self.parent = parent
#         self.bids = self.parent.bids
        
#         self.setMinimumSize(700,300)

#         # Setup logging here:
#         self.logTextBox = QTextEditLogger(self)
#         self.logTextBox.setFormatter(
#             logging.Formatter("%(levelname)s - %(message)s")
#         )
#         logging.getLogger().addHandler(self.logTextBox)
#         logging.getLogger().setLevel(logging.DEBUG)

#         # self._button = QtWidgets.QPushButton()
#         # self._button.setText("Start")

#         layout = QVBoxLayout(self)
#         layout.addWidget(self.logTextBox.widget)
#         # layout.addWidget(self._button)

#         # self._button.clicked.connect(self.test)

#         self.process = QProcess()
#         self.process.readyReadStandardOutput.connect(
#             self.handle_readyReadStandardOutput
#         )
#         # self.process.started.connect(lambda: print("Started!"))
#         # self.process.finished.connect(lambda: print("Finished!"))

#     # def test(self):
#     #     logging.debug("damn, a bug")
#     #     logging.info("something to remember")
#     #     logging.warning("that's not right")
#     #     logging.error("foobar")

#     #     script = os.path.join(CURRENT_DIR, "another_module.py")
#     #     self.process.start(sys.executable, [script])

#     def handle_readyReadStandardOutput(self):
#         text = self.process.readAllStandardOutput().data().decode()
#         self.logTextBox.widget.appendPlainText(text.strip())

# class StreamToLogger(object):
#     """
#     Fake file-like stream object that redirects writes to a logger instance.
#     """
#     def __init__(self, logger, log_level=logging.INFO):
#         self.logger = logger
#         self.log_level = log_level
#         self.linebuf = ''

#     def write(self, buf):
#         temp_linebuf = self.linebuf + buf
#         self.linebuf = ''
#         for line in temp_linebuf.splitlines(True):
#             # From the io.TextIOWrapper docs:
#             #   On output, if newline is None, any '\n' characters written
#             #   are translated to the system default line separator.
#             # By default sys.stdout.write() expects '\n' newlines and then
#             # translates them so this is still cross platform.
#             if line[-1] == '\n':
#                 self.logger.log(self.log_level, line.rstrip())
#             else:
#                 self.linebuf += line

#     def flush(self):
#         if self.linebuf != '':
#             self.logger.log(self.log_level, self.linebuf.rstrip())
#         self.linebuf = ''

# class MyDialog(QDialog, QPlainTextEdit):
#     def __init__(self, parent=None):
#         super().__init__(parent)

#         logTextBox = QTextEditLogger(self)
#         # You can format what is logging.infoed to text box
#         logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
#         logging.getLogger().addHandler(logTextBox)
#         # You can control the logging level
#         logging.getLogger().setLevel(logging.DEBUG)

#         self._button = QPushButton(self)
#         self._button.setText('Test Me')

#         layout = QVBoxLayout()
#         # Add the new logging box widget to the layout
#         layout.addWidget(logTextBox.widget)
#         layout.addWidget(self._button)
#         self.setLayout(layout)

#         # Connect signal to slot
#         self._button.clicked.connect(self.test)

#     def test(self):
#         logging.debug('damn, a bug')
#         logging.info('something to remember')
#         logging.warning('that\'s not right')
#         logging.error('foobar')

# class Signals(QObject):
#     finished = pyqtSignal()

class RunnableSubprocess(QObject, QRunnable):
    finished = pyqtSignal()
    
    def __init__(self, operation):
        super().__init__()
        self.operation = operation
        # self.signal = Signals()
        
    def run(self):
        subprocess.Popen(self.operation, shell=True).wait()
        # self.signal.finished.emit()
        self.finished.emit()
        
class SubprocessWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    
    def __init__(self, operation):
        super().__init__()
        self.operation = operation
        
        # # self.signal = Signals()
        # self.logger = logging.getLogger("Worker")

        # # set up log handler
        # self.logHandler = ThreadLogger()
        # self.logHandler.setFormatter(
        #     logging.Formatter('%(asctime)s - %(levelname)s - %(threadName)s - %(message)s'))
        # self.logger.addHandler(self.logHandler)

        # # set the logging level
        # self.logger.setLevel(logging.DEBUG)
        
    def run(self):
        subprocess.Popen(self.operation, shell=True).wait()
        # self.signal.finished.emit()
        self.finished.emit()
        
class RunnableOperation(QObject, QRunnable):
    finished = pyqtSignal()
    
    def __init__(self, function, args=[], kwargs={}):
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs
        # self.signal = Signals()
        
    def run(self):
        self.function(*self.args, **self.kwargs)
        # self.signal.finished.emit()
        self.finished.emit()
        
class OperationWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    
    def __init__(self, function, args=[], kwargs={}):
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs
        
        # # self.signal = Signals()
        # self.logger = logging.getLogger("Worker")

        # # set up log handler
        # self.logHandler = ThreadLogger()
        # self.logHandler.setFormatter(
        #     logging.Formatter('%(asctime)s - %(levelname)s - %(threadName)s - %(message)s'))
        # self.logger.addHandler(self.logHandler)

        # # set the logging level
        # self.logger.setLevel(logging.DEBUG)
        
        # self.kwargs['logger'] = self.logger
        
    def run(self):
        try:
            # logging.debug('Operation run has been called and is now running')
            self.function(*self.args, **self.kwargs)
            # self.signal.finished.emit()
        except Exception as e:
            pass
        self.finished.emit()
        
# class MyLog(QObject):
#     # create a new Signal
#     # - have to be a static element
#     # - class  has to inherit from QObject to be able to emit signals
#     signal = pyqtSignal(str)

#     # not sure if it's necessary to implement this
#     def __init__(self):
#         super().__init__()
        
# class ThreadLogger(logging.Handler):
#     def __init__(self):
#         super().__init__()
#         self.log = MyLog()

#     # logging.Handler.emit() is intended to be implemented by subclasses
#     def emit(self, record):
#         msg = self.format(record)
#         self.log.signal.emit(msg)
        
class AddWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    
    def __init__(self, bids, list_to_add):
        super().__init__()
        self.bids = bids
        self.list_to_add = list_to_add
        
        # # self.signal = Signals()
        # self.logger = logging.getLogger("Worker")

        # # set up log handler
        # self.logHandler = ThreadLogger()
        # self.logHandler.setFormatter(
        #     logging.Formatter('%(asctime)s - %(levelname)s - %(threadName)s - %(message)s'))
        # self.logger.addHandler(self.logHandler)

        # # set the logging level
        # self.logger.setLevel(logging.DEBUG)
        
    def run(self):
        for item in self.list_to_add:

            dicom = item[0]

            if ".zip" in dicom:
                directory_to_extract_to = dicom[:-4]
                with zipfile.ZipFile(dicom, 'r') as zip_ref:
                    zip_ref.extractall(directory_to_extract_to)
                dicom = directory_to_extract_to

            DICOM_FOLDER = dicom
            PATIENT_ID = item[1]
            SESSION = item[2]

            try:
                self.bids.convert_dicoms_to_bids(dicomfolder = DICOM_FOLDER,
                                                    pat_id      = PATIENT_ID,
                                                    session     = SESSION,
                                                    return_dicom_series=True)
                
                # logging.info(f"[INFO] done for patient {pat_id}")
            except Exception as e:
                # logging.info(f'[ERROR] Dicom to Bids failed for {DICOM_FOLDER}: {e}')
                # exc_type, exc_obj, exc_tb = sys.exc_info()
                # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                # logging.info(exc_type, fname, exc_tb.tb_lineno)
                # traceback.logging.info_exc()
                pass
        self.finished.emit()
        
class StdOutTextEdit(QPlainTextEdit):
    def __init__(self, parent):
        super(StdOutTextEdit, self).__init__()
        self.setParent(parent)
        self.setReadOnly(True)
        # self.setLineWidth(50)
        self.setMinimumSize(700,300)
        # self.setFont(QFont('Consolas', 11))

    @pyqtSlot(str)
    def append_text(self, text: str):
        self.moveCursor(QTextCursor.End)
        self.insertPlainText(text)


class StdTQDMTextEdit(QLineEdit):
    def __init__(self, parent):
        super(StdTQDMTextEdit, self).__init__()
        self.setParent(parent)
        self.setReadOnly(True)
        self.setEnabled(True)
        self.setMinimumWidth(500)
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setClearButtonEnabled(True)
        self.setFont(QFont('Consolas', 11))

    @pyqtSlot(str)
    def set_tqdm_text(self, text: str):
        new_text = text
        if new_text.find('\r') >= 0:
            new_text = new_text.replace('\r', '').rstrip()
            if new_text:
                self.setText(new_text)
        else:
            # we suppose that all TQDM prints have \r, so drop the rest
            pass


if __name__ == "__main__":

    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance() 
    
    # app = QApplication(sys.argv)

    window = MainWindow()

    window.show()

    app.exec()
    
    del config_dict['TQDM_WRITE_STREAM_CONFIG']['queue']
    del config_dict['TQDM_WRITE_STREAM_CONFIG']['write_stream']
    del config_dict['TQDM_WRITE_STREAM_CONFIG']['qt_queue_receiver']
    del config_dict['TQDM_WRITE_STREAM_CONFIG']
    del config_dict['STDOUT_WRITE_STREAM_CONFIG']['queue']
    del config_dict['STDOUT_WRITE_STREAM_CONFIG']['write_stream']
    del config_dict['STDOUT_WRITE_STREAM_CONFIG']['qt_queue_receiver']
    del config_dict['STDOUT_WRITE_STREAM_CONFIG']
    del config_dict
