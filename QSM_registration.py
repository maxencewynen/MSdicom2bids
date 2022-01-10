#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 11:55:48 2021

@author: colinVDB
registration of QSM
"""
import os
from change_orientation import *

def QSM_registration(subject, session):
    MAIN_DIR = '/media/maggi/MS-PRL/MS-PRL/MS-PRL_NIH/DATA'
    # =============================================================================
    # flip z    
    # =============================================================================
    reorient(subject, session, 'acq-mag_T2star_matlab', 'z', DIR=MAIN_DIR)
    
    os.system(f'rm {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_acq-mag_T2star_matlab.nii.gz')
    os.system(f'mv {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_acq-mag_T2star_matlab_z.nii.gz {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_acq-mag_T2star_matlab.nii.gz')
    
    reorient(subject, session, 'QSM_matlab', 'z', DIR='/media/maggi/MS-PRL/MS-PRL/MS-PRL_NIH/DATA')
    
    os.system(f'rm {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_QSM_matlab.nii.gz')
    os.system(f'mv {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_QSM_matlab_z.nii.gz {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_QSM_matlab.nii.gz')
    
    # =============================================================================
    # registration of acq-mag_T2star_matlab
    # =============================================================================
    print("Registration of acq-mag_T2star_matlab to T2star for", subject, session)
    os.system(f'$ANTs_registration -d 3 -n 4 -f {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_acq-mag_T2star.nii.gz -m {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_acq-mag_T2star_matlab.nii.gz -t r -o {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_acq-mag_T2star_matlab_regstar')

    os.system(f'rm {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_acq-mag_T2star_matlab_regstarInverseWarped.nii.gz')
    
    os.system(f'mv {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_acq-mag_T2star_matlab_regstarWarped.nii.gz {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_acq-mag_T2star_matlab_regstar.nii.gz')
    
    # =============================================================================
    # transformation du QSM
    # =============================================================================
    print("Transformation of QSM to T2star for", subject, session)
    os.system('${ANTSPATH}/antsApplyTransforms -d 3 -i ' + f'{MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_QSM_matlab.nii.gz -r {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_acq-mag_T2star.nii.gz -t {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_acq-mag_T2star_matlab_regstar0GenericAffine.mat -n nearestNeighbor -o {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_QSM.nii.gz')
    
    if session != '01':
        # =============================================================================
        # registration of acq-mag_T2star_matlab to ses-01
        # =============================================================================
        print("Registration of acq-mag_T2star_matlab to T2star_ses-01 for", subject, session)
        os.system(f'$ANTs_registration -d 3 -n 4 -f {MAIN_DIR}/sub-{subject}/ses-01/anat/sub-{subject}_ses-01_acq-mag_T2star.nii.gz -m {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_acq-mag_T2star_matlab_regstar.nii.gz -t r -o {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_acq-mag_T2star_matlab_reg-ses-01')
    
        os.system(f'rm {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_acq-mag_T2star_matlab_reg-ses-01InverseWarped.nii.gz')
        
        os.system(f'mv {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_acq-mag_T2star_matlab_reg-ses-01Warped.nii.gz {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_acq-mag_T2star_matlab_reg-ses-01.nii.gz')
        
        # =============================================================================
        # transformation du QSM to ses-01
        # =============================================================================
        print("Transformation of QSM to T2star_ses-01 for", subject, session)
        os.system('${ANTSPATH}/antsApplyTransforms -d 3 -i ' + f'{MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_QSM.nii.gz -r {MAIN_DIR}/sub-{subject}/ses-01/anat/sub-{subject}_ses-01_acq-mag_T2star.nii.gz -t {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_acq-mag_T2star_matlab_reg-ses-010GenericAffine.mat -n nearestNeighbor -o {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_QSM_reg-ses-01.nii.gz')


if __name__ == '__main__':
    sub_sess_list = [('043',['04'])
                    ]
    
    for sub, sess in sub_sess_list:
        for ses in sess:
            print(f'Sub-{sub}: Ses-{ses}: QSM registration !')
            QSM_registration(sub, ses)
            
    