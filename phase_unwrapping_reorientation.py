#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 14:10:35 2021

@author: colinVDB
Phase unwrappping and reorientation
"""
import os
from change_orientation import *
from reorient_phase_unwrapped import *

def phase_unwrapping_reorientation(subject, session):
    MAIN_DIR = '/media/maggi/MS-PRL/MS-PRL/MS-PRL_NIH/DATA'
    # =============================================================================
    # phase unwrapping
    # =============================================================================
    os.system(f'docker run --rm -v {MAIN_DIR}/sub-{subject}/ses-{session}/anat:/data blakedewey/phase_unwrap -p sub-{subject}_ses-{session}_phase-WRAPPED.nii.gz -o sub-{subject}_ses-{session}_acq-phase_T2star')
    
    replace_affine_or_header(f'{MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_acq-phase_T2star_UNWRAPPED.nii.gz', f'{MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_acq-mag_T2star.nii.gz', affine=True, header=False)
    
    reorient_phase_unwrapped_2(f'{MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_acq-phase_T2star_UNWRAPPED_corr-aff.nii.gz')
    
    os.system(f'mv {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_acq-phase_T2star_UNWRAPPED_corr-aff_reoriented_2.nii.gz {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_acq-phase_T2star.nii.gz')
    
    os.system(f'rm {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_acq-phase_T2star_UNWRAPPED_corr-aff.nii.gz')
    
    if session != '01':
        # =============================================================================
        # registration of acq-mag_T2star_matlab to ses-01
        # =============================================================================
        print("Registration of acq-mag_T2star_matlab to T2star_ses-01 for", subject, session)
        os.system(f'$ANTs_registration -d 3 -n 4 -f {MAIN_DIR}/sub-{subject}/ses-01/anat/sub-{subject}_ses-01_acq-mag_T2star.nii.gz -m {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_acq-mag_T2star.nii.gz -t r -o {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_acq-mag_T2star_reg-ses-01')
    
        os.system(f'rm {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_acq-mag_T2star_reg-ses-01InverseWarped.nii.gz')
        
        os.system(f'mv {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_acq-mag_T2star_reg-ses-01Warped.nii.gz {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_acq-mag_T2star_reg-ses-01.nii.gz')
        
        # =============================================================================
        # transformation du QSM to ses-01
        # =============================================================================
        print("Transformation of QSM to T2star_ses-01 for", subject, session)
        os.system('${ANTSPATH}/antsApplyTransforms -d 3 -i ' + f'{MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_acq-phase_T2star.nii.gz -r {MAIN_DIR}/sub-{subject}/ses-01/anat/sub-{subject}_ses-01_acq-mag_T2star.nii.gz -t {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_acq-mag_T2star_reg-ses-010GenericAffine.mat -n nearestNeighbor -o {MAIN_DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_acq-phase_T2star_reg-ses-01.nii.gz')

    
if __name__ == '__main__':
    
    sub_sess_list = [('030',['03']),
                     ('032',['03','04','05']),
                     ('034',['03']),
                     ('035',['03','04','05']),
                     ('036',['03','04']),
                     ('040',['03','04','05']),
                     ('043',['03','04'])
                     ]
    
    for sub, sess in sub_sess_list:
        for ses in sess:
            print(f'Sub-{sub}: Ses-{ses}: Phase unwrapping !')
            phase_unwrapping_reorientation(sub, ses)