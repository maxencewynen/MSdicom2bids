#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 15:59:19 2021

@author: colinVDB
FLAIR registration
"""

import os

def FLAIR_registration(subject, session):
    MAIN_DIR = '/media/maggi/MS-PRL/MS-PRL/MS-PRL_NIH/DATA'
    # =============================================================================
    # registration of acq-mag_T2star_matlab
    # =============================================================================
    print("Registration of FLAIR to T2star for", subject, session)
    os.system(f'$ANTs_registration -d 3 -n 4 -f {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_acq-mag_T2star.nii.gz -m {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_FLAIR.nii.gz -t r -o {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_FLAIR_regstar')

    os.system(f'rm {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_FLAIR_regstarInverseWarped.nii.gz')
    
    os.system(f'mv {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_FLAIR_regstarWarped.nii.gz {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_FLAIR_regstar.nii.gz')
   
    if session != '01':
        # =============================================================================
        # registration of acq-mag_T2star_matlab to ses-01
        # =============================================================================
        print("Registration of FLAIR to T2star_ses-01 for", subject, session)
        os.system(f'$ANTs_registration -d 3 -n 4 -f {MAIN_DIR}/sub-{subject}/ses-01/anat/sub-{subject}_ses-01_acq-mag_T2star.nii.gz -m {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_FLAIR.nii.gz -t r -o {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_FLAIR_reg-ses-01')
    
        os.system(f'rm {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_FLAIR_reg-ses-01InverseWarped.nii.gz')
        
        os.system(f'mv {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_FLAIR_reg-ses-01Warped.nii.gz {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_FLAIR_reg-ses-01.nii.gz')
        

if __name__ == '__main__':
    sub_sess_list = [('007',['03']),
                     ('026',['03']),
                     ('030',['03']),
                     ('032',['03','04','05']),
                     ('034',['03']),
                     ('035',['03','04','05']),
                     ('036',['03','04']),
                     ('040',['03','04','05']),
                     ('043',['03','04'])
                     ]
    
    for sub, sess in sub_sess_list:
        for ses in sess:
            print(f'Sub-{sub}: Ses-{ses}: FLAIR registration !')
            FLAIR_registration(sub, ses)
            
    