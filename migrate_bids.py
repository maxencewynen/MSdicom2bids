# -*- coding: utf-8 -*-
"""
Created on Tue Nov  2 16:40:19 2021

@author: Maxence Wynen
"""
from dicom2bids import BIDSHandler
import os
from os.path import join as pjoin
from os.path import exists as pexists
from shutil import copy


chuv = BIDSHandler(root_dir=r"/home/stluc/Data/MS-ALL")
chuv_ok = BIDSHandler(root_dir=r"/home/stluc/Data/MS-ALL_corr")

# basel = BIDSHandler(root_dir=r"C:\Users\Cristina\Desktop\2DFA\data\raw\BASEL_INSIDER")
# basel_ok = BIDSHandler(root_dir=r"C:\Users\Cristina\Desktop\2DFA\data\raw\BASEL_INSIDER_OK")


bids = chuv
bids_ok = chuv_ok
def migrate(bids, bids_ok):
    patients_l =  [x for x in next(os.walk(bids.root_dir))[1] if 'sub-' in x]
    
    patients = {pat:[x for x in next(os.walk(pjoin(bids.root_dir, pat)))[1] 
                     if 'ses-' in x] 
                for pat in patients_l}
    
    for pat, sessions in patients.items():
        pat_id = pat.split('-')[1]
        for ses in sessions:
            ses_id = ses.split('-')[1]
            bids_ok.make_directories(pat_id=pat_id, session=ses_id)
            
            dos = "anat"
            folder = pjoin(bids.root_dir, pat, ses, dos)
            
            for filename in os.listdir(folder):
                
                if ("T1map" in filename or "UNIT1" in filename or "MP2RAGE" in filename):
                    dest = pjoin(bids_ok.root_dir, "derivatives", "MP2RAGE",
                                 pat, ses, filename)
                    
                elif ("acq-star_FLAIR" in filename):
                    dest = pjoin(bids_ok.root_dir, "derivatives", 
                                 "acq-star_FLAIR", pat, ses, filename)
                    
                elif ("QSM" in filename):
                    dest = pjoin(bids_ok.root_dir, "derivatives", 
                                 "QSM", pat, ses, filename)
                    
                elif ("acq-phase_T2star" in filename):
                    dest = pjoin(bids_ok.root_dir, "derivatives", 
                                 "acq-phase_T2star", pat, ses, filename)
                    
                else:
                    dest = pjoin(bids_ok.root_dir, pat, ses, dos, filename)
                    
                copy(pjoin(folder,filename), dest)
                
#old_derivative: (new_folder_location, suffix, new_name)
dc = {"synthetic_mp2rage" : ("skullstripped", "MP2RAGE", None),
      "segmentations": (pjoin("registrations", 
                              "registrations_to_T2star",
                              "derivatives",
                              "lesionmasks"), 
                        None, 
                        "binary_lesions"),
      "expert_annotations": (pjoin("registrations", 
                                  "registrations_to_T2star",
                                  "derivatives",
                                  "lesionmasks"),
                           None,
                           "prl-2d_lesions"),
      "rims_annotations": (pjoin("registrations", 
                                  "registrations_to_T2star",
                                  "derivatives",
                                  "lesionmasks"),
                           None,
                           "labeled_lesions")}


def migrate_derivatives(bids, bids_ok, derivatives_correspondance):
    dv = pjoin(bids.root_dir, "derivatives")
    dv_ok = pjoin(bids_ok.root_dir, "derivatives")
    
    for old_dv, (new_dv, suffix, new_name) in derivatives_correspondance.items():
        patients_l =  [x for x in next(os.walk(bids.root_dir))[1] if 'sub-' in x]
    
        patients = {pat:[x for x in next(os.walk(pjoin(bids.root_dir, pat)))[1] 
                         if 'ses-' in x] 
                    for pat in patients_l}
        
        for pat, sessions in patients.items():
            pat_id = pat.split('-')[1]
            for ses in sessions:
                ses_id = ses.split('-')[1]
                
                
                old_fdr = pjoin(dv, old_dv, pat, ses)
                new_fdr = pjoin(dv_ok, new_dv, pat, ses)
                
                for filename in os.listdir(old_fdr):
                    if new_name is not None:
                        new_filename = f"{pat}_{ses}_{new_name}"
                        extension = filename.split(".", 1)[1]
                        new_filename += "." + extension
                    else:
                        new_filename = filename
                    if suffix is not None:
                        new_filename = new_filename.replace(".", f"_{suffix}.", 1)
                    
                    copy(pjoin(old_fdr, filename),
                         pjoin(new_fdr, new_filename))




def migrate_registrations(bids, bids_ok):
    REGISTRATION_INFOS          = {"T2star": (["acq-mag_T2star", 
                                            "acq-phase_T2star",
                                            "acq-star_FLAIR"]),
                               "FLAIR": ["FLAIR"],
                               "MPRAGE": ["MPRAGE"]}
    # anat : FLAIR, acq-mag_T2star, acq-phase_T2star
    patients_l =  [x for x in next(os.walk(bids.root_dir))[1] if 'sub-' in x]
    
    patients = {pat:[x for x in next(os.walk(pjoin(bids.root_dir, pat)))[1] 
                     if 'ses-' in x] 
                for pat in patients_l}
    
    for pat, sessions in patients.items():
        pat_id = pat.split('-')[1]
        for ses in sessions:
            ses_id = ses.split('-')[1]
            
            #anat
            folder = pjoin(bids.root_dir, pat, ses, "anat")
            
            for filename in os.listdir(folder):
                dest = pjoin(bids_ok.root_dir, "derivatives", "registrations", 
                             "registrations_to_T2star", pat, ses, "anat")
                if "acq-star_FLAIR" in filename:
                    dest = pjoin(bids_ok.root_dir, "derivatives", "registrations", 
                            "registrations_to_T2star", "derivatives", 
                            "acq-star_FLAIR", pat, ses) 
                    
                elif "FLAIR" in filename and "acq-star" not in filename:
                    dest = pjoin(bids_ok.root_dir, "derivatives", "registrations", 
                                 "registrations_to_FLAIR", pat, ses, "anat")
                
                elif "T1map" in filename or "MP2RAGE" in filename:
                    continue
                
                copy(pjoin(folder, filename), pjoin(dest, filename))
            
            #derivatives
            # registrations
            folder = pjoin(bids.root_dir, "derivatives", 
                           "registrations_to_T2star", pat, ses)
            
            for filename in os.listdir(folder):
                if "FLAIR" in filename and "acq-star" not in filename:
                    dest = pjoin(bids_ok.root_dir, "derivatives", "registrations", 
                                 "registrations_to_T2star", pat, ses, "anat")
                
                elif "T1map" in filename or "MP2RAGE" in filename:
                    dest = pjoin(bids_ok.root_dir, "derivatives", "registrations", 
                                 "registrations_to_T2star", "derivatives",
                                 "MP2RAGE", pat, ses)
                else: 
                    print(f"Weird file: {filename}")
                    print("Copying into anat T2star")
                    dest = pjoin(bids_ok.root_dir, "derivatives", "registrations", 
                                 "registrations_to_T2star", pat, ses, "anat")
                
                copy(pjoin(folder, filename), pjoin(dest, filename))
            
            
    


if __name__ == "__main__":
    migrate(chuv, chuv_ok)
    # migrate_derivatives(chuv, chuv_ok, dc)
    # migrate_registrations(chuv, chuv_ok)
    
    # migrate(basel, basel_ok)
    # migrate_derivatives(basel, basel_ok, dc)
    # migrate_registrations(basel, basel_ok)
                    
                    
                

                




    
    