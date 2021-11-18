#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 16:17:00 2021

@author: ColinVDB
BIDS Manager
"""

import tkinter as tk
import tkinter.filedialog

import os,sys,inspect
from dicom2bids import *
import zipfile

dicom2niix_path = "dcm2niix"

# class OpeningWindow(tk.Toplevel):
    
#     def __init__(self, master=None):
#         super().__init__(master=master)
#         self.title("Opening Window")
#         label = tk.Label(self, text="Select or Create your BIDS directory")
#         label.pack()
#         button = tk.Button(self, text="Browse", command=self.browse)
#         button.pack()
        
#     def browse(self):
#         self.bids_dir = tk.filedialog.askdirectory(initialdir='/home', title='Select or create your BIDS directory')
#         print(self.bids_dir)

class MainWindow:
    
    def __init__(self):
        
        self.root = tk.Tk()
        self.root.title("BIDS Manager")
        
        self.center()
        
        self.bids_dir = tk.filedialog.askdirectory(initialdir='/', title='Select or create your BIDS directory')
            
        while self.bids_dir == ():
            self.bids_dir = tk.filedialog.askdirectory(initialdir='/', title='Please, select or create your BIDS directory')
        
        self.bids = BIDSHandler(root_dir=self.bids_dir, dicom2niix_path=dicom2niix_path)
        
        self.main_tab()
        
        self.root.mainloop()
        
    def center(self):
        windowWidth = self.root.winfo_reqwidth()
        windowHeight = self.root.winfo_reqheight()
        positionRight = int(self.root.winfo_screenwidth()/2 - windowWidth/2)
        positionDown = int(self.root.winfo_screenheight()/2 - windowHeight/2)
        self.root.geometry("+{}+{}".format(positionRight, positionDown))
        
    def main_tab(self):
        # =====================================================================
        # Main Tab    
        # =====================================================================
        bids_dir_split = self.bids_dir.split('/')
        Bids_name = bids_dir_split[len(bids_dir_split)-1]
        label_bids = tk.Label(self.root, text=Bids_name, font=('Calibri', 25))
        label_bids.grid(row=0, column=1)
        label_subjects = tk.Label(self.root, text='Number of subjects: ', font=('Calibri',15))
        label_subjects.grid(row=1, column=0)
        label_num_subjects = tk.Label(self.root, text=self.bids.number_of_subjects, font=('Calibri',15), anchor='w')
        label_num_subjects.grid(row=1, column=1, sticky='w')
        
launch = MainWindow()

