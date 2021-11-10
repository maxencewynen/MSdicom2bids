#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  9 10:57:14 2021

@author: ColinVDB

Script to transform a list of raw dicoms into a BIDS database 
"""

from dicom2bids import BIDSHandler

dicom2niix_path = r"C:\Users\Cristina\Downloads\dcm2niix.exe"

list_dicoms = ['',
               ''
               ]

bidshandler = BIDSHandler(root_dir=r'', dicom2niix_path=dicom2niix_path)

pat_id = 0

for dicom in list_dicoms:
    
    DICOM_FOLDER = dicom
    PATIENT_ID = None
    SESSION = None
    
    try:
        pat_id, session, dicom_series = bidshandler.convert_dicoms_to_bids(dicomfolder = DICOM_FOLDER, 
                                                                        pat_id      = PATIENT_ID,
                                                                        session     = SESSION, 
                                                                        return_dicom_series=True)
    except:
        print(f'[ERROR] Didom to Bids failed for patient {pat_id+1}')
    print(f"[INFO] done for patient {pat_id}")
print("[INFO] All done.")

