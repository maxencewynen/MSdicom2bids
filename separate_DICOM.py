#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 21 15:24:32 2021

@author: ColinVDB
"""

# Alex Weston
# Digital Innovation Lab, Mayo Clinic

import os
import pydicom # pydicom is using the gdcm package for decompression

def clean_text(string):
    # clean and standardize text descriptions, which makes searching files easier
    forbidden_symbols = ["*", ".", ",", "\"", "\\", "/", "|", "[", "]", ":", ";", " "]
    for symbol in forbidden_symbols:
        string = string.replace(symbol, "_") # replace everything with an underscore
    return string.lower()  
   
# user specified parameters
src = "/media/maggi/MS-PRL/MS-PRL/MS-PRL_Brussels/DICOM/sub-059/ses-02/DICOM"
dst = src + "/sorted"

print('reading file list...')
unsortedList = []
for root, dirs, files in os.walk(src):
    for file in files: 
        if ".dcm" in file or "." not in file:# exclude non-dicoms, good for messy folders
            unsortedList.append(os.path.join(root, file))

print('%s files found.' % len(unsortedList))
       
for dicom_loc in unsortedList:
    # read the file
    ds = pydicom.read_file(dicom_loc, force=True)
    
    # # get patient, study, and series information
    patientID = clean_text(ds.get("PatientID", "NA"))
    # studyDate = clean_text(ds.get("StudyDate", "NA"))
    # studyDescription = clean_text(ds.get("StudyDescription", "NA"))
    # seriesDescription = clean_text(ds.get("SeriesDescription", "NA"))
   
    # # generate new, standardized file name
    # modality = ds.get("Modality","NA")
    # studyInstanceUID = ds.get("StudyInstanceUID","NA")
    # seriesInstanceUID = ds.get("SeriesInstanceUID","NA")
    instanceNumber = str(ds.get("InstanceNumber","0"))
    # fileName = modality + "." + seriesInstanceUID + "." + instanceNumber + ".dcm"
    
    # get scanning sequence
    scanning_sequence = ds.get("SeriesDescription")
    
    if scanning_sequence == None:
        scanning_sequence = "NoSeriesDescription"
    
    scanning_sequence = scanning_sequence.replace(" ", "_")
    
    scanning_sequence = scanning_sequence.replace("*", "-")
    
    scanning_sequence = scanning_sequence.replace(".", "")
    
    fileName = patientID + "_" + scanning_sequence + "_" + instanceNumber + ".dcm"
       
    # # uncompress files (using the gdcm package)
    # try:
    #     ds.decompress()
    # except:
    #     print('an instance in file %s" could not be decompressed. exiting.' % (patientID))
   
    # save files to a 4-tier nested folder structure
    if not os.path.exists(os.path.join(dst, scanning_sequence)):
        os.makedirs(os.path.join(dst, scanning_sequence))
   
    ds.save_as(os.path.join(dst, scanning_sequence, fileName))

print('done.')