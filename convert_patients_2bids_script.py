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

list_dicoms = ["/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/ABBOUD-22feb2021",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/ADDAMO280521",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/AL-MOMANI",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/ANANOUCH290521",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/BEN-ABOUD-09-MAR-2021",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/benslimane090421",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/BOULAICH",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/Bourgignon080621",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/BOUTON07-10-21",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/BRICE290521",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/BRIJJAK_09091996",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/CASERA250521",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/Christ15062021",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/COLLA_20051994",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/COLLARD-080621",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/CORSO17-08-21",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/DABACHI060421",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/DeFilippo_20210914",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/DeFrance300321",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/DEGREVE_22062021",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/DEHIN_03SEPT2021",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/DE-Laminne-22feb2021",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/DE-MEYER_12-march-2021",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/detilleux130421",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/drappier130421",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/dupont14-10-21",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/DUPONT02112021",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/DUPONT_27aug2021",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/DURANT_22062021",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/Dzelili",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/EL-AKEL-27072021",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/ELBOUTZSAKHTI_19feb2021",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/Elghalbzouri020421",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/FRAIOLI_16061965",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/FRIZ07-10-21",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/GARCIAGONZALEZ290521",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/HEYNINCK-26-mars-2021",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/HOCINE-2-mars-2021",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/IRM-delaminne",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/IRM-ROSE",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/KHATIB-Sarah_15042021",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/LECOMPTE_14111996",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/LHOIR16-09-21",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/LONCKE29062021",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/MARESCAUX",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/MASSIMIANO-2-mars-2021",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/MATTHYS29062021",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/NYA26-10-21",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/OMBELETS03-11-21",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/Otten_24-Aug-2021",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/ouaazizi-l10508z",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/QUERTAIN",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/RAMPLOT160421",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/ROSE-L47612W",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/SEMANA05-10-21",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/SOREL04-11-21",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/STAMATOPOULOS-05-mars-2021",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/Tainttinger_19-03-21",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/THYS250521",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/Van-varenberg_23_03_21",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/VENTURI29-10-2021",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/VERBEKE090721",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/Wantier_19-03-21",
"/media/stluc/Colin Vanden Bulcke Drive/DISSECT_MS/DB_DICOM_R4/WUYTENS300321"]

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

