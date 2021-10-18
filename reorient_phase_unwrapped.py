#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 11 16:08:39 2021

@author: maggi
"""
import nibabel as nib
import numpy as np
# import matplotlib.pyplot as plt

"""
function reorient_phase_unwrapped: 
    used to reorient the unwrapped phase image that is returned by the 
    phase_unwrap docker function. 
    args: *phase_filename: filename of the unwrapped phase image to reorient 
                          with its path
          *t2star_filename: filename of the reference t2star image with its 
                          path
    output: save the reoriented image in the same directory
"""
def reorient_phase_unwrapped(phase_filename, t2star_filename):
    
    # loading of the 2 images
    phase = nib.load(phase_filename)
    t2star = t2star = nib.load(t2star_filename)
    
    # transform the phase image into a numpy array
    phase_img = phase.get_fdata()
    
    # different rotations perform on the phase image
    phase_img_r = np.rot90(phase_img, k=1, axes=(0,2))
    
    phase_img_r = np.rot90(phase_img_r, k=1, axes=(0,1))
    
    phase_img_r = np.rot90(phase_img_r, k=2)
    
    # flip of the image
    phase_img_r_flip = np.flip(phase_img_r, axis=2)
    
    # correction of the affine with the t2star reference image to have the 2 image in the same origin axes
    phase_nifti = nib.Nifti1Image(phase_img_r_flip, t2star.affine)
    
    # get the path to the directory
    phase_name = phase_filename.split('.')
    
    # creation of the output name for the output file
    output_name = phase_name[0]+'_reoriented.nii.gz'
    
    # save the file in the correct directory
    nib.save(phase_nifti, output_name)
    
    print("[INFO] Phase Reoriented !")
    

"""
function reorient_phase_unwrapped_2: 
    used to reorient the unwrapped phase image that is returned by the 
    phase_unwrap docker function. 
    args: *phase_filename: filename of the unwrapped phase image to reorient 
                          with its path
    output: save the reoriented image in the same directory
"""    
def reorient_phase_unwrapped_2(phase_filename):

    mri = nib.load(phase_filename)
    
    mri_data = mri.get_fdata()
    
    mri_r = np.rot90(mri_data, k=2, axes=(0,1))
    
    mri_nifti = nib.Nifti1Image(mri_r, mri.affine)
        
    # get the path to the directory
    phase_name = phase_filename.split('.')
    
    # creation of the output name for the output file
    output_name = phase_name+"_reoriented_2.nii.gz"
    
    # save the file in the correct directory
    nib.save(mri_nifti, output_name)
    
    print("[INFO] Phase Reoriented !")