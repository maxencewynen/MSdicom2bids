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

list_dicoms = ["/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/DUPONT_27aug2021",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/DURANT_22062021.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/Dzelili.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/EL-AKEL-27072021.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/ELBOUTZSAKHTI_19feb2021.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/Elghalbzouri020421.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/FRAIOLI_16061965.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/FRIZ07-10-21.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/GARCIAGONZALEZ290521.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/HEYNINCK-26-mars-2021.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/HOCINE-2-mars-2021.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/IRM-delaminne.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/IRM-ROSE.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/KHATIB-Sarah_15042021.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/LECOMPTE_14111996.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/LHOIR16-09-21.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/LONCKE29062021.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/MARESCAUX.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/MASSIMIANO-2-mars-2021.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/MATTHYS29062021.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/NYA26-10-21.zip",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/OMBELETS03-11-21.zip",
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

