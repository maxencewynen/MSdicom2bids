#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  9 10:57:14 2021

@author: ColinVDB

Script to transform a list of raw dicoms into a BIDS database 
"""

import os,sys,inspect
from dicom2bids import *
import zipfile

dicom2niix_path = "dcm2niix"

list_dicoms = ["/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/OMBELETS03-11-21.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/Otten_24-Aug-2021.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/OUAAZIZI-08FEB2021.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/QUERTAIN.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/RAMPLOT160421.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/ROSE-L47612W.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/SEMANA05-10-21.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/SOREL04-11-21.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/STAMATOPOULOS-05-mars-2021.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/Tainttinger_19-03-21.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/THYS250521.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/Van-varenberg_23_03_21.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/VENTURI29-10-2021.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/VERBEKE090721.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/Wantier_19-03-21.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/WUYTENS300321.zip"]

bidshandler = BIDSHandler(root_dir=r"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/BIDS_R4", dicom2niix_path=dicom2niix_path)

pat_id = 0

for dicom in list_dicoms:
    
    if ".zip" in dicom:
        directory_to_extract_to = dicom[:-4]
        with zipfile.ZipFile(dicom, 'r') as zip_ref:
            zip_ref.extractall(directory_to_extract_to)
        dicom = directory_to_extract_to
    
    DICOM_FOLDER = dicom
    PATIENT_ID = None
    SESSION = None
    
    try:
        pat_id, session, dicom_series = bidshandler.convert_dicoms_to_bids(dicomfolder = DICOM_FOLDER, 
                                                                        pat_id      = PATIENT_ID,
                                                                        session     = SESSION, 
                                                                        return_dicom_series=True)
        print(f"[INFO] done for patient {pat_id}")
    except:
        print(f'[ERROR] Didom to Bids failed for patient {pat_id}')
print("[INFO] All done.")

