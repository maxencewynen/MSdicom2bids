import sys
import os
from os.path import join as pjoin
from os.path import exists as pexists
# from dicom2bids import *
import logging
from PyQt5.QtCore import QSize, Qt, QModelIndex
from PyQt5.QtWidgets import QDesktopWidget, QApplication, QWidget, QPushButton, QMainWindow, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QFileDialog, QDialog, QTreeView, QFileSystemModel, QGridLayout, QPlainTextEdit, QMessageBox, QListWidget, QTableWidget, QTableWidgetItem, QMenu, QAction, QTabWidget, QCheckBox
from PyQt5.QtGui import QFont
import traceback
import threading
import subprocess
import pandas as pd
import platform
import json
from bids_validator import BIDSValidator

def launch(parent):
    window = MainWindow(parent)
    window.show()

class MainWindow(QMainWindow):
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.bids = self.parent.bids
        
        self.setWindowTitle("Registration")
        self.window = QWidget(self)
        self.setCentralWidget(self.window)
        self.center()
        
        self.tabs = QTabWidget(self)
        # Tab1
        self.tab1 = RegistrationTab(self)
        
        # Tab 2
        self.tab2 = TransformationTab(self)
        
        self.tabs.addTab(self.tab1, "Registration")
        self.tabs.addTab(self.tab2, "Transformation")
        
        # self.registration = TransformationTab(self)
        
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        
        self.window.setLayout(layout)
        
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
class RegistrationTab(QWidget):
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.bids = self.parent.bids
        self.setMinimumSize(500, 200)
        
        self.sequence_to_register = ""
        self.ref_sequence = ""
        self.subjects = []
        self.sess_to_register = []
        self.ref_ses = ""
        self.name_reg = ""
        self.sub_to_register = ""
        self.trans_sequences = []
        self.trans_sub = ""
        self.trans_ses = ""
        self.ref_path = []
        self.path_to_register = []
        self.trans_path_to_register = []
        
        self.select_sequence_to_register_button = QPushButton("Select image to register")
        self.select_sequence_to_register_button.clicked.connect(self.select_sequence_to_register)
        self.sequence_to_register_label = QLabel()
        
        self.select_ref_sequence_button = QPushButton("Select reference image")
        self.select_ref_sequence_button.clicked.connect(self.select_ref_sequence)
        self.ref_sequence_label = QLabel()
        
        self.subjects_input = QLineEdit(self)
        self.subjects_input.setPlaceholderText("Select subjects")
        
        self.sessions_input = QLineEdit(self)
        self.sessions_input.setPlaceholderText("Select sessions")
        
        self.select_name_reg = QLineEdit(self)
        self.select_name_reg.setPlaceholderText('Name of registration')
        
        # self.script = QCheckBox('Script?')
        # self.script_bool = False
        # self.script.stateChanged.connect(self.check_script)
        
        self.apply_same_transformation_check = QCheckBox('Apply same transformation ?')
        self.apply_same_transformation_check.stateChanged.connect(self.apply_same_transformation)
        self.apply_same_transformation_label = QLabel()
        
        self.registration_button = QPushButton("Registration")
        self.registration_button.clicked.connect(self.registration)
        
        self.layout = QGridLayout()
        self.layout.addWidget(self.select_sequence_to_register_button, 0, 0, 1, 1)
        self.layout.addWidget(self.sequence_to_register_label, 0, 1, 1, 1)
        self.layout.addWidget(self.select_ref_sequence_button, 1, 0, 1, 1)
        self.layout.addWidget(self.ref_sequence_label, 1, 1, 1, 1)
        self.layout.addWidget(self.subjects_input, 2, 0, 1, 1)
        self.layout.addWidget(self.sessions_input, 2, 1, 1, 1)
        self.layout.addWidget(self.select_name_reg, 3, 0, 1, 2)
        self.layout.addWidget(self.apply_same_transformation_check, 4, 0, 1, 1)
        self.layout.addWidget(self.apply_same_transformation_label, 4, 1, 1, 1)
        self.layout.addWidget(self.registration_button, 5, 0, 1, 2)
        
        self.setLayout(self.layout)
        
    def select_sequence_to_register(self):
        path_to_image_to_register = QFileDialog.getOpenFileName(self, "Select image to register", self.bids.root_dir)[0]
        path_to_image = path_to_image_to_register.split('/')
        # find sequence
        all_sequence = path_to_image[-1]
        sequence_no_ext = all_sequence.split('.')[0]
        self.sub_to_register = sequence_no_ext.split('_')[0].split('-')[1]
        self.ses_to_register = sequence_no_ext.split('_')[1].split('-')[1]
        self.sequence_to_register = sequence_no_ext.replace(f'sub-{self.sub_to_register}_ses-{self.ses_to_register}_', '')
        # find path
        self.path_to_register = path_to_image[0:-1]
        self.sequence_to_register_label.setText(self.sequence_to_register)
        
    def select_ref_sequence(self):
        path_to_ref_image = QFileDialog.getOpenFileName(self, "Select reference image", self.bids.root_dir)[0]
        path_to_image = path_to_ref_image.split('/')
        # find sequence
        all_sequence = path_to_image[-1]
        sequence_no_ext = all_sequence.split('.')[0]
        self.ref_sub = sequence_no_ext.split('_')[0].split('-')[1]
        self.ref_ses = sequence_no_ext.split('_')[1].split('-')[1]
        self.ref_sequence = sequence_no_ext.replace(f'sub-{self.ref_sub}_ses-{self.ref_ses}_', '')
        # find path
        self.ref_path = path_to_image[0:-1]
        self.ref_sequence_label.setText(self.ref_sequence)
        
    def apply_same_transformation(self):
        if self.apply_same_transformation_check.isChecked() == True:
            same_transformation_images = QFileDialog.getOpenFileNames(self, "Select images to apply same transformation", self.bids.root_dir)[0]
            self.trans_sequences = []
            self.trans_path_to_register = []
            for image in same_transformation_images:
                path_to_image = image.split('/')
                # find sequence
                all_sequence = path_to_image[-1]
                sequence_no_ext = all_sequence.split('.')[0]
                self.trans_sub = sequence_no_ext.split('_')[0].split('-')[1]
                self.trans_ses = sequence_no_ext.split('_')[1].split('-')[1]
                self.trans_sequences.append(sequence_no_ext.replace(f'sub-{self.trans_sub}_ses-{self.trans_ses}_', ''))
                # find path
                self.trans_path_to_register.append(path_to_image[0:-1])
        else:
            self.trans_sub = ""
            self.trans_ses = ""
            self.trans_sequences = []
            self.trans_path_to_register = []
        trans_sequences_lab = ""
        for seq in self.trans_sequences:
            if seq == self.trans_sequences[-1]:
                trans_sequences_lab = trans_sequences_lab + f'{seq}'
            else:
                trans_sequences_lab = trans_sequences_lab + f'{seq}\n'
        self.apply_same_transformation_label.setText(trans_sequences_lab)
            
    def registration(self):
        subjects = self.subjects_input.text()
        sessions = self.sessions_input.text()
        self.name_reg = self.select_name_reg.text()
        self.subjects = []
        # find subjects
        if subjects == '':
            self.subjects.append(self.sub_to_register)
        elif subjects == 'all':
            all_directories = [x for x in next(os.walk(self.bids.root_dir))[1]]
            for sub in all_directories:
                if sub.find('sub-') == 0:
                    self.subjects.append(sub.split('-')[1])
        else:
            subjects_split = subjects.split(',')
            for sub in subjects_split:
                if '-' in sub:
                    inf_bound = sub.split('-')[0]
                    sup_bound = sub.split('-')[1]
                    fill = len(inf_bound)
                    inf = int(inf_bound)
                    sup = int(sup_bound)
                    for i in range(inf,sup+1):
                        self.subjects.append(str(i).zfill(fill))
                else:
                    self.subjects.append(sub)
                    
        # find sessions
        self.sessions = []
        if sessions == '':
            self.sessions.append(self.ses_to_register)
        elif sessions == 'all':
            self.sessions.append('all')
        else:
            sessions_split = sessions.split(',')
            for ses in sessions_split:
                if '-' in ses:
                    inf_bound = ses.split('-')[0]
                    sup_bound = ses.split('-')[1]
                    fill = len(inf_bound)
                    inf = int(inf_bound)
                    sup = int(sup_bound)
                    for i in range(inf, sup+1):
                        self.sessions.append(str(i).zfill(fill))
                else:
                    self.sessions.append(ses)
                    
        self.subjects_and_sessions = []
        for sub in self.subjects:
            if len(self.sessions) != 0:
                if self.sessions[0] == 'all':
                    all_directories = [x for x in next(os.walk(pjoin(self.bids.root_dir,f'sub-{sub}')))[1]]
                    sub_ses = []
                    for ses in all_directories:
                        if ses.find('ses-') == 0:
                            sub_ses.append(ses.split('-')[1])
                    self.subjects_and_sessions.append((sub,sub_ses))
                else:
                    self.subjects_and_sessions.append((sub,self.sessions))
                    
        # find name reg
        if self.name_reg == "":
            reg = self.ref_sequence.split('_')[-1]
            if self.ses_to_register == self.ref_ses:
                self.name_reg = f'reg-{reg}'
            else:
                self.name_reg = f'reg-{reg}-{self.ref_ses}'
                    
        self.registration_script()                
                    
    def registration_script(self):
        logging.info(self.subjects_and_sessions)            
        logging.info(self.name_reg)
        if self.sub_to_register != self.ref_sub:
            logging.info('Registration must be done between images of the same subject')
            return
        
        same_ses = self.ses_to_register == self.ref_ses
        
        for sub, sess in self.subjects_and_sessions:
            for ses in sess:
                # Create directory
                directories = [pjoin('derivatives','registrations'), pjoin('derivatives','registrations',f'{self.name_reg}'), pjoin('derivatives','registrations',f'{self.name_reg}',f'sub-{self.sub_to_register}'),pjoin('derivatives','registrations',f'{self.name_reg}',f'sub-{self.sub_to_register}',f'ses-{self.ses_to_register}')]
                self.bids.mkdirs_if_not_exist(self.bids.root_dir, directories=directories)
                registered_path = pjoin(self.bids.root_dir,'derivatives','registrations',f'{self.name_reg}')
                # Perform registration
                if same_ses:
                    image_to_register = pjoin(self.rename_path_sub_ses(self.path_to_register,sub,ses),f'sub-{sub}_ses-{ses}_{self.sequence_to_register}.nii.gz')
                    ref_image = pjoin(self.rename_path_sub_ses(self.ref_path,sub,ses),f'sub-{sub}_ses-{ses}_{self.ref_sequence}.nii.gz')
                    registered_image = pjoin(registered_path,f'sub-{sub}',f'ses-{ses}',f'sub-{sub}_ses-{ses}_{self.sequence_to_register}_{self.name_reg}')
                    logging.debug(image_to_register)
                    logging.debug(ref_image)
                    logging.debug(registered_image)
                    logging.debug(pexists(image_to_register) and pexists(ref_image))
                    if pexists(image_to_register) and pexists(ref_image):
                        logging.info(f'Registering {image_to_register} onto {ref_image} ...')
                        
                        subprocess.Popen(f'$ANTs_registration -d 3 -n 4 -f {ref_image} -m {image_to_register} -t r -o {registered_image}',shell=True).wait()                      
                        subprocess.Popen(f'rm {registered_image}InverseWarped.nii.gz',shell=True).wait()                    
                        subprocess.Popen(f'mv {registered_image}Warped.nii.gz {registered_image}.nii.gz',shell=True).wait()
                                         
                        logging.info(f'Registering {image_to_register} onto {ref_image} done')
                        
                        if self.apply_same_transformation_check.isChecked() == True:
                            logging.info(f'Applaying same transformation ...')
                            for trans_seq, trans_path in (self.trans_sequences,self.trans_path_to_register):
                                trans_image_to_register = pjoin(self.rename_path_sub_ses(trans_path,sub,ses),f'sub-{sub}_ses-{ses}_{trans_seq}.nii.gz')
                                trans_registered_image = pjoin(registered_path,f'sub-{sub}',f'ses-{ses}',f'sub-{sub}_ses-{ses}_{trans_seq}_{self.reg_name}')
                                
                                if pexists(trans_image_to_register):
                                    subprocess.Popen('${ANTSPATH}/antsApplyTransforms -d 3 -i {trans_image_to_register} -r {ref_image} -t {registered_image}0GenericAffine.mat -n nearestNeighbor -o {trans_registered_image}.nii.gz',shell=True).wait()
                else:
                    image_to_register = pjoin(self.rename_path_sub_ses(self.path_to_register,sub,ses),f'sub-{sub}_ses-{ses}_{self.sequence_to_register}.nii.gz')
                    ref_image = pjoin(self.rename_path_sub_ses(self.ref_path,sub,self.ref_ses),f'sub-{sub}_ses-{self.ref_ses}_{self.ref_sequence}.nii.gz')
                    registered_image = pjoin(registered_path,f'sub-{sub}',f'ses-{ses}',f'sub-{sub}_ses-{ses}_{self.sequence_to_register}_{self.name_reg}')
                    
                    if pexists(image_to_register) and pexists(ref_image):
                        logging.info(f'Registering {image_to_register} onto {ref_image} ...')
                        
                        subprocess.Popen(f'$ANTs_registration -d 3 -n 4 -f {ref_image} -m {image_to_register} -t r -o {registered_image}',shell=True).wait()                      
                        subprocess.Popen(f'rm {registered_image}InverseWarped.nii.gz',shell=True).wait()                    
                        subprocess.Popen(f'mv {registered_image}Warped.nii.gz {registered_image}.nii.gz',shell=True).wait()
                                         
                        logging.info(f'Registering {image_to_register} onto {ref_image} done')
                        
                        if self.apply_same_transformation_check.isChecked() == True:
                            logging.info(f'Applaying same transformation ...')
                            for trans_seq, trans_path in (self.trans_sequences,self.trans_path_to_register):
                                trans_image_to_register = pjoin(self.rename_path_sub_ses(trans_path,sub,ses),f'sub-{sub}_ses-{ses}_{trans_seq}.nii.gz')
                                trans_registered_image = pjoin(registered_path,f'sub-{sub}',f'ses-{ses}',f'sub-{sub}_ses-{ses}_{trans_seq}_{self.reg_name}')
                                
                                if pexists(trans_image_to_register):
                                    subprocess.Popen('${ANTSPATH}/antsApplyTransforms -d 3 -i {trans_image_to_register} -r {ref_image} -t {registered_image}0GenericAffine.mat -n nearestNeighbor -o {trans_registered_image}.nii.gz',shell=True).wait()

    @staticmethod
    def rename_path_sub_ses(path,sub,ses):
        new_path = []
        for p in path:
            if 'sub-' in p:
                new_path.append(f'sub-{sub}')
            elif 'ses-' in p:
                new_path.append(f'ses-{ses}')
            else:
                new_path.append(p)
        path_name = '/'
        for p in new_path:
            path_name = pjoin(path_name,p)
        return path_name

class TransformationTab(QWidget):
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.bids = self.parent.bids
        self.setMinimumSize(500, 200)
        
        self.sequence_to_register = ""
        self.ref_sequence = ""
        self.subjects = []
        self.sess_to_register = []
        self.ref_ses = ""
        self.name_reg = ""
        self.sub_to_register = ""
        self.trans_sequences = []
        self.trans_sub = ""
        self.trans_ses = ""
        self.ref_path = []
        self.path_to_register = []
        self.trans_path_to_register = []
        self.sub_trans_matrix = ""
        self.ses_trans_matrix = ""
        self.trans_matrix_sequence = ""
        
        self.select_sequence_to_register_button = QPushButton("Select image to register")
        self.select_sequence_to_register_button.clicked.connect(self.select_sequence_to_register)
        self.sequence_to_register_label = QLabel()
        
        self.select_ref_sequence_button = QPushButton("Select reference image")
        self.select_ref_sequence_button.clicked.connect(self.select_ref_sequence)
        self.ref_sequence_label = QLabel()
        
        self.select_transformation_matrix_button = QPushButton("Select transformation matrix")
        self.select_transformation_matrix_button.clicked.connect(self.select_transformation_matrix)
        self.transformation_matrix_label = QLabel()
        
        self.subjects_input = QLineEdit(self)
        self.subjects_input.setPlaceholderText("Select subjects")
        
        self.sessions_input = QLineEdit(self)
        self.sessions_input.setPlaceholderText("Select sessions")
        
        # self.select_name_reg = QLineEdit(self)
        # self.select_name_reg.setPlaceholderText('Name of registration')
        
        # self.script = QCheckBox('Script?')
        # self.script_bool = False
        # self.script.stateChanged.connect(self.check_script)
        
        # self.apply_same_transformation_check = QCheckBox('Apply same transformation ?')
        # self.apply_same_transformation_check.stateChanged.connect(self.apply_same_transformation)
        # self.apply_same_transformation_label = QLabel()
        
        self.transformation_button = QPushButton("Transformation")
        self.transformation_button.clicked.connect(self.transformation)
        
        self.layout = QGridLayout()
        self.layout.addWidget(self.select_sequence_to_register_button, 0, 0, 1, 1)
        self.layout.addWidget(self.sequence_to_register_label, 0, 1, 1, 1)
        self.layout.addWidget(self.select_ref_sequence_button, 1, 0, 1, 1)
        self.layout.addWidget(self.ref_sequence_label, 1, 1, 1, 1)
        self.layout.addWidget(self.select_transformation_matrix_button, 2, 0, 1, 1)
        self.layout.addWidget(self.transformation_matrix_label, 2, 1, 1, 1)
        self.layout.addWidget(self.subjects_input, 3, 0, 1, 1)
        self.layout.addWidget(self.sessions_input, 3, 1, 1, 1)        
        # self.layout.addWidget(self.apply_same_transformation_check, 4, 0, 1, 1)
        # self.layout.addWidget(self.apply_same_transformation_label, 4, 1, 1, 1)
        self.layout.addWidget(self.transformation_button, 4, 0, 1, 2)
        
        self.setLayout(self.layout)
        
    def select_sequence_to_register(self):
        path_to_image_to_register = QFileDialog.getOpenFileName(self, "Select image to register", self.bids.root_dir)[0]
        path_to_image = path_to_image_to_register.split('/')
        # find sequence
        all_sequence = path_to_image[-1]
        sequence_no_ext = all_sequence.split('.')[0]
        self.sub_to_register = sequence_no_ext.split('_')[0].split('-')[1]
        self.ses_to_register = sequence_no_ext.split('_')[1].split('-')[1]
        self.sequence_to_register = sequence_no_ext.replace(f'sub-{self.sub_to_register}_ses-{self.ses_to_register}_', '')
        # find path
        self.path_to_register = path_to_image[0:-1]
        self.sequence_to_register_label.setText(self.sequence_to_register)
        
    def select_ref_sequence(self):
        path_to_ref_image = QFileDialog.getOpenFileName(self, "Select reference image", self.bids.root_dir)[0]
        path_to_image = path_to_ref_image.split('/')
        # find sequence
        all_sequence = path_to_image[-1]
        sequence_no_ext = all_sequence.split('.')[0]
        self.ref_sub = sequence_no_ext.split('_')[0].split('-')[1]
        self.ref_ses = sequence_no_ext.split('_')[1].split('-')[1]
        self.ref_sequence = sequence_no_ext.replace(f'sub-{self.ref_sub}_ses-{self.ref_ses}_', '')
        # find path
        self.ref_path = path_to_image[0:-1]
        self.ref_sequence_label.setText(self.ref_sequence)
        
    def select_transformation_matrix(self):
        path_to_trans_matrix = QFileDialog.getOpenFileName(self, "Select transformation matrix", self.bids.root_dir)[0]
        path_to_image = path_to_trans_matrix.split('/')
        # find sequence
        all_sequence = path_to_image[-1]
        sequence_no_ext = all_sequence.split('.')[0]
        self.sub_trans_matrix = sequence_no_ext.split('_')[0].split('-')[1]
        self.ses_trans_matrix = sequence_no_ext.split('_')[1].split('-')[1]
        self.trans_matrix_sequence = sequence_no_ext.replace(f'sub-{self.sub_trans_matrix}_ses-{self.ses_trans_matrix}_', '')
        # find path
        self.trans_matrix_path = path_to_trans_matrix[0:-1]
        self.transformation_matrix_label.setText(self.trans_matrix_sequence)
        
    # def apply_same_transformation(self):
    #     if self.apply_same_transformation_check.isChecked() == True:
    #         same_transformation_images = QFileDialog.getOpenFileNames(self, "Select images to apply same transformation", self.bids.root_dir)[0]
    #         self.trans_sequences = []
    #         self.trans_path_to_register = []
    #         for image in same_transformation_images:
    #             path_to_image = image.split('/')
    #             # find sequence
    #             all_sequence = path_to_image[-1]
    #             sequence_no_ext = all_sequence.split('.')[0]
    #             self.trans_sub = sequence_no_ext.split('_')[0].split('-')[1]
    #             self.trans_ses = sequence_no_ext.split('_')[1].split('-')[1]
    #             self.trans_sequences.append(sequence_no_ext.replace(f'sub-{self.trans_sub}_ses-{self.trans_ses}_', ''))
    #             # find path
    #             self.trans_path_to_register.append(path_to_image[0:-1])
    #     else:
    #         self.trans_sub = ""
    #         self.trans_ses = ""
    #         self.trans_sequences = []
    #         self.trans_path_to_register = []
    #     trans_sequences_lab = ""
    #     for seq in self.trans_sequences:
    #         if seq == self.trans_sequences[-1]:
    #             trans_sequences_lab = trans_sequences_lab + f'{seq}'
    #         else:
    #             trans_sequences_lab = trans_sequences_lab + f'{seq}\n'
    #     self.apply_same_transformation_label.setText(trans_sequences_lab)
            
    def transformation(self):
        subjects = self.subjects_input.text()
        sessions = self.sessions_input.text()
        # self.name_reg = self.select_name_reg.text()
        self.subjects = []
        # find subjects
        if subjects == '':
            self.subjects.append(self.sub_to_register)
        elif subjects == 'all':
            all_directories = [x for x in next(os.walk(self.bids.root_dir))[1]]
            for sub in all_directories:
                if sub.find('sub-') == 0:
                    self.subjects.append(sub.split('-')[1])
        else:
            subjects_split = subjects.split(',')
            for sub in subjects_split:
                if '-' in sub:
                    inf_bound = sub.split('-')[0]
                    sup_bound = sub.split('-')[1]
                    fill = len(inf_bound)
                    inf = int(inf_bound)
                    sup = int(sup_bound)
                    for i in range(inf,sup+1):
                        self.subjects.append(str(i).zfill(fill))
                else:
                    self.subjects.append(sub)
                    
        # find sessions
        self.sessions = []
        if sessions == '':
            self.sessions.append(self.ses_to_register)
        elif sessions == 'all':
            self.sessions.append('all')
        else:
            sessions_split = sessions.split(',')
            for ses in sessions_split:
                if '-' in ses:
                    inf_bound = ses.split('-')[0]
                    sup_bound = ses.split('-')[1]
                    fill = len(inf_bound)
                    inf = int(inf_bound)
                    sup = int(sup_bound)
                    for i in range(inf, sup+1):
                        self.sessions.append(str(i).zfill(fill))
                else:
                    self.sessions.append(ses)
                    
        self.subjects_and_sessions = []
        for sub in self.subjects:
            if len(self.sessions) != 0:
                if self.sessions[0] == 'all':
                    all_directories = [x for x in next(os.walk(pjoin(self.bids.root_dir,f'sub-{sub}')))[1]]
                    sub_ses = []
                    for ses in all_directories:
                        if ses.find('ses-') == 0:
                            sub_ses.append(ses.split('-')[1])
                    self.subjects_and_sessions.append((sub,sub_ses))
                else:
                    self.subjects_and_sessions.append((sub,self.sessions))
                    
        # find name reg
        self.name_reg = self.trans_matrix_sequence.split('_')[-1]
        self.name_reg = self.name_reg.replace('0GenericAffine','')
                    
        self.registration_script()                
                    
    def transformation_script(self):
        logging.info(self.subjects_and_sessions)            
        logging.info(self.name_reg)
        if self.sub_to_register != self.ref_sub or self.sub_trans_matrix != self.sub_to_register or self.ref_sub != self.sub_trans_matrix:
            logging.info('Transformation must be done between images of the same subject')
            return
        
        same_ses = self.ses_to_register == self.ref_ses
        
        for sub, sess in self.subjects_and_sessions:
            for ses in sess:
                # Create directory
                directories = [pjoin('derivatives','registrations'), pjoin('derivatives','registrations',f'{self.name_reg}'), pjoin('derivatives','registrations',f'{self.name_reg}',f'sub-{self.sub_to_register}'),pjoin('derivatives','registrations',f'{self.name_reg}',f'sub-{self.sub_to_register}',f'ses-{self.ses_to_register}')]
                self.bids.mkdirs_if_not_exist(self.bids.root_dir, directories=directories)
                registered_path = pjoin(self.bids.root_dir,'derivatives','registrations',f'{self.name_reg}')
                # Perform registration
                if same_ses:
                    image_to_register = pjoin(self.rename_path_sub_ses(self.path_to_register,sub,ses),f'sub-{sub}_ses-{ses}_{self.sequence_to_register}.nii.gz')
                    ref_image = pjoin(self.rename_path_sub_ses(self.ref_path,sub,ses),f'sub-{sub}_ses-{ses}_{self.ref_sequence}.nii.gz')
                    registered_image = pjoin(registered_path,f'sub-{sub}',f'ses-{ses}',f'sub-{sub}_ses-{ses}_{self.sequence_to_register}_{self.name_reg}')
                    transformation_matrix = pjoin(self.rename_path_sub_ses(self.trans_matrix_path,sub,ses),f'sub-{sub}_ses-{ses}_{self.trans_matrix_sequence}.mat')
                    logging.debug(image_to_register)
                    logging.debug(ref_image)
                    logging.debug(registered_image)
                    logging.debug(pexists(image_to_register) and pexists(ref_image) and pexists(transformation_matrix))
                    logging.debug(transformation_matrix)
                    if pexists(image_to_register) and pexists(ref_image) and pexists(transformation_matrix):
                        logging.info(f'Transforming {image_to_register} onto {ref_image} using {transformation_matrix} matrix ...')
                        
                        subprocess.Popen('${ANTSPATH}/antsApplyTransforms -d 3 -i {image_to_register} -r {ref_image} -t {transformation_matrix} -n nearestNeighbor -o {registered_image}.nii.gz',shell=True).wait()
                                         
                        logging.info(f'Tranforming {image_to_register} onto {ref_image} done')

                else:
                    image_to_register = pjoin(self.rename_path_sub_ses(self.path_to_register,sub,ses),f'sub-{sub}_ses-{ses}_{self.sequence_to_register}.nii.gz')
                    ref_image = pjoin(self.rename_path_sub_ses(self.ref_path,sub,self.ref_ses),f'sub-{sub}_ses-{self.ref_ses}_{self.ref_sequence}.nii.gz')
                    registered_image = pjoin(registered_path,f'sub-{sub}',f'ses-{ses}',f'sub-{sub}_ses-{ses}_{self.sequence_to_register}_{self.name_reg}')
                    transformation_matrix = pjoin(self.rename_path_sub_ses(self.trans_matrix_path,sub,ses),f'sub-{sub}_ses-{ses}_{self.trans_matrix_sequence}.mat')
                    if pexists(image_to_register) and pexists(ref_image) and pexists(transformation_matrix):
                        logging.info(f'Transforming {image_to_register} onto {ref_image} using {transformation_matrix} matrix ...')
                        
                        subprocess.Popen('${ANTSPATH}/antsApplyTransforms -d 3 -i {image_to_register} -r {ref_image} -t {transformation_matrix} -n nearestNeighbor -o {registered_image}.nii.gz',shell=True).wait()
                                    
                        logging.info(f'Transforming {image_to_register} onto {ref_image} done')
    @staticmethod
    def rename_path_sub_ses(path,sub,ses):
        new_path = []
        for p in path:
            if 'sub-' in p:
                new_path.append(f'sub-{sub}')
            elif 'ses-' in p:
                new_path.append(f'ses-{ses}')
            else:
                new_path.append(p)
        path_name = '/'
        for p in new_path:
            path_name = pjoin(path_name,p)
        return path_name
        
    
    
    