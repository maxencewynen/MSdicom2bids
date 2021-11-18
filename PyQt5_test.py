#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 14:25:40 2021

@author: ColinVDB
BIDS MANAGER GUI
"""

import sys
from dicom2bids import *
import logging
from PyQt5.QtCore import QSize, Qt, QModelIndex
from PyQt5.QtWidgets import QDesktopWidget, QApplication, QWidget, QPushButton, QMainWindow, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QFileDialog, QDialog, QTreeView, QFileSystemModel, QGridLayout, QPlainTextEdit, QMessageBox, QListWidget, QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QFont

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Main Window')
        self.window = QWidget(self)
        self.setCentralWidget(self.window)
        self.center()
        
        self.bids_dir = str(QFileDialog.getExistingDirectory(self, "Select BIDS Directory"))
        while self.bids_dir=="":
            self.bids_dir = str(QFileDialog.getExistingDirectory(self, "Please, select BIDS Directory"))
        
        self.bids = BIDSHandler(root_dir=self.bids_dir, dicom2niix_path="dcm2niix")
        bids_dir_split = self.bids_dir.split('/')
        self.bids_name = bids_dir_split[len(bids_dir_split)-1]
        self.bids_lab = QLabel(self.bids_name)
        self.bids_lab.setFont(QFont('Calibri', 30))
        
        self.bids_dir_view = BidsDirView(self)
        
        self.bids_metadata = BidsMetadata(self)
        
        self.bids_actions = BidsActions(self)
        
        self.bids_dialog = BidsDialog(self)
        
        layout = QGridLayout()
        layout.addWidget(self.bids_lab, 0, 1, 1, 2)
        layout.addWidget(self.bids_dir_view, 0, 0, 3, 1)
        layout.addWidget(self.bids_metadata, 1, 1)
        layout.addWidget(self.bids_actions, 1, 2)
        layout.addWidget(self.bids_dialog, 2, 1, 1, 2)
        
        self.window.setLayout(layout)
        
        self.center()
    
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    def closeEvent(self, event):
        sys.stdout = self.bids_dialog.stdout
        
    def update_bids(self):
        print("update_bids!")
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
            layout.addWidget(self.bids_dialog, 2, 1, 1, 2)
            self.window = QWidget(self)
            self.setCentralWidget(self.window)
            self.window.setLayout(layout)
        else:
            pass
        
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
#         print('Browse')       
#         self.folderpath = QFileDialog.getExistingDirectory(self, 'Select Folder')
        
#         print(self.folderpath)
 
class BidsDirView(QWidget):
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
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
        # self.tree.rightClicked.connect(self.treeMedia_rightClicked)
        
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
            print(f"[INFO] Opening {item_path}")
            if '.nii' in item_path:
                os.system(f"itksnap -g {item_path}")
            else:
                os.system(f"xdg-open {item_path}")
        else:
            pass
    
    # def treeMedia_rightClicked(self, index):
    #     item = self.tree.selectedIndexes()[0]
    #     print(item.model().filePath(index))
    #     item_path = item.model().filePath(index)
    #     if os.path.isfile(item_path):
    #         print("rC: file")
    #     else:
    #         print("rC: folder")
    #         pass

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
        self.setLayout(layout)
    
    def update_metadata(self):
        self.bids = self.parent.bids
        self.number_of_subjects.setText(f"Number of subjects: {self.bids.number_of_subjects}")
        
class BidsActions(QWidget):
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.bids = self.parent.bids
        
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
        
        layout = QVBoxLayout()
        sub_layout = QHBoxLayout()
        sub_layout.addWidget(self.add_button)
        sub_layout.addWidget(self.remove_button)
        sub_layout_1 = QHBoxLayout()
        sub_layout_1.addWidget(self.rename_sub_button)
        sub_layout_1.addWidget(self.rename_ses_button)
        layout.addWidget(self.change_bids_dir_button)
        layout.addLayout(sub_layout)
        layout.addLayout(sub_layout_1)
        
        self.setLayout(layout)
        
    def change_bids_dir(self):
        print("change_bids_dir")
        # bids_dir = str(QFileDialog.getExistingDirectory(self, "Select BIDS Directory"))
        # if os.path.isdir(bids_dir):
        #     self.bids = BIDSHandler(root_dir=bids_dir, dicom2niix_path="dcm2niix")
        #     self.parent.bids = self.bids
        #     self.parent.update_bids()
        self.parent.update_bids()
        
    def add(self):
        print("add")
        self.add_win = AddWindow(self)
        self.add_win.show()
        
    def remove(self):
        print("remove")
        self.rm_win = RemoveWindow(self)
        self.rm_win.show()
        
    def rename_sub(self):
        print("rename_sub")
        self.renameSub_win = RenameSubject(self)
        self.renameSub_win.show()
        
    def rename_ses(self):
        print("rename_ses")
        
    def update_bids(self, parent):
        self.parent = parent
        self.bids = self.parent.bids
        
class RemoveWindow(QMainWindow):
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.bids = self.parent.bids
        
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
        print(f"Removing sub-{subject} ses-{session}")
        if subject != "":
            if session != "":
                self.bids.delete_session(subject, session)
            else:
                self.bids.delete_subject(subject)
        
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
class AddWindow(QMainWindow):          
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.bids = self.parent.bids
        
        self.setWindowTitle("Add subject or session")
        self.window = QWidget(self)
        self.setCentralWidget(self.window)
        self.center()
        
        self.list_to_add = []
        
        self.label = QLabel("Select DICOM folders to add to BIDS directory")
        self.label.setAlignment(Qt.AlignHCenter)
        self.subject = QLineEdit(self)
        self.subject.setPlaceholderText('Subject number')
        self.session = QLineEdit(self)
        self.session.setPlaceholderText('Session number')
        self.add_folder_button = QPushButton("Add DICOM Folder")
        self.add_folder_button.clicked.connect(self.add_folder)
        self.add_files_button = QPushButton("Add DICOM Files")
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
        layout.addWidget(self.subject, 1, 0, 1, 1)
        layout.addWidget(self.session, 1, 1, 1, 1)
        layout.addWidget(self.add_folder_button, 2, 0, 1, 1)
        layout.addWidget(self.add_files_button, 2, 1, 1, 1)
        layout.addWidget(self.list_view, 3, 0, 1, 2)
        layout.addWidget(self.add_button, 4, 0, 1, 2)
        
        self.window.setLayout(layout)
        
    def add_folder(self):
        dicom_folder = str(QFileDialog.getExistingDirectory(self, "Select DICOM folder"))
        rowPosition = len(self.list_to_add)
        self.list_view.insertRow(rowPosition)
        subject = self.subject.text()
        session = self.session.text()
        if len(subject) != 3:
            subject = None
        if len(session) != 2:
            session = None
        self.list_view.setItem(rowPosition , 0, QTableWidgetItem(dicom_folder))
        self.list_view.setItem(rowPosition , 1, QTableWidgetItem(subject))
        self.list_view.setItem(rowPosition , 2, QTableWidgetItem(session))
        self.list_to_add.append((dicom_folder, subject, session))

    
    def add_files(self):
        dicom_folder = QFileDialog.getOpenFileName(self, 'Select DICOM zip file')[0]
        rowPosition = len(self.list_to_add)
        self.list_view.insertRow(rowPosition)
        subject = self.subject.text()
        session = self.session.text()
        if len(subject) != 3:
            subject = None
        if len(session) != 2:
            session = None
        self.list_view.setItem(rowPosition , 0, QTableWidgetItem(dicom_folder))
        self.list_view.setItem(rowPosition , 1, QTableWidgetItem(subject))
        self.list_view.setItem(rowPosition , 2, QTableWidgetItem(session))
        self.list_to_add.append((dicom_folder, subject, session))
    
    def add(self):
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
                pat_id, session, dicom_series = self.bids.convert_dicoms_to_bids(dicomfolder = DICOM_FOLDER, 
                                                                                pat_id      = PATIENT_ID,
                                                                                session     = SESSION, 
                                                                                return_dicom_series=True)
                print(f"[INFO] done for patient {pat_id}")
            except:
                print(f'[ERROR] Didom to Bids failed for {DICOM_FOLDER}')
        print("[INFO] All done.")
        
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
class RenameSubject(QMainWindow):
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.bids = self.parent.bids
        
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
        
        self.bids.rename_subject(old_sub, new_sub)
        print(f"sub-{old_sub} renamed to sub-{new_sub}")
        
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
        
class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)

class BidsDialog(QDialog, QPlainTextEdit):
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        
        self.setMinimumSize(700,300)
        
        logTextBox = QTextEditLogger(self)
        logTextBox.setFormatter(logging.Formatter('%(message)s'))
        logger = logging.getLogger()
        logger.addHandler(logTextBox)
        logger.setLevel(logging.DEBUG)
        self.stdout = sys.stdout
        stdout_logger = logging.getLogger('STDOUT')
        sl = StreamToLogger(stdout_logger, logging.INFO)
        sys.stdout = sl
        
        # self._button = QPushButton('Test me')
        # self._button.clicked.connect(self.test)
        
        layout = QVBoxLayout()
        layout.addWidget(logTextBox.widget)
        # layout.addWidget(self._button)
        self.setLayout(layout)
        
    # def test(self):
    #     print('damn, a bug')
    #     print('something to remember')
    #     print('that\'s not right')
    #     print('foobar')
        
    def closeEvent(self, event):
        sys.stdout = self.stdout
        
    def close(self):
        sys.stdout = self.stdout
    
class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        temp_linebuf = self.linebuf + buf
        self.linebuf = ''
        for line in temp_linebuf.splitlines(True):
            # From the io.TextIOWrapper docs:
            #   On output, if newline is None, any '\n' characters written
            #   are translated to the system default line separator.
            # By default sys.stdout.write() expects '\n' newlines and then
            # translates them so this is still cross platform.
            if line[-1] == '\n':
                self.logger.log(self.log_level, line.rstrip())
            else:
                self.linebuf += line

    def flush(self):
        if self.linebuf != '':
            self.logger.log(self.log_level, self.linebuf.rstrip())
        self.linebuf = ''
        
# class MyDialog(QDialog, QPlainTextEdit):
#     def __init__(self, parent=None):
#         super().__init__(parent)

#         logTextBox = QTextEditLogger(self)
#         # You can format what is printed to text box
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

if __name__ == "__main__":
        
    app = QApplication([])
    
    window = MainWindow()
    
    window.show()
    
    app.exec()