# -*- coding: utf-8 -*-
"""
Created on Mon Mar 15 15:16:43 2021

@author: maxen
"""
import nibabel as nib
# import os
import numpy as np
# from scipy.ndimage.measurements import label
# import sys


def reorient(subject, session, sequence_name, axis, DIR="/media/stluc/Elements/DISSECT_MS_DATABASE"):
    sub = subject
    ses = session
    axis = axis
    seq = sequence_name

    AXES = {'x':0,'y':1,'z':2}

    file = f"{DIR}/sub-{sub}/ses-{ses}/anat/sub-{sub}_ses-{ses}_{seq}.nii.gz"
    output = f"{DIR}/sub-{sub}/ses-{ses}/anat/sub-{sub}_ses-{ses}_{seq}_{axis}.nii.gz"

    image = nib.load(file)

    new_data = np.flip(image.get_fdata(), AXES[axis])
    new_image = nib.Nifti1Image(new_data, image.affine, image.header)
    nib.save(new_image, output)



def separate_epi(subject, session, DIR="/media/stluc/Elements/DISSECT_MS_DATABASE"):
    img = nib.load(f"{DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_EPI.nii.gz")
    epi4d = img.get_fdata()
    dim1 = epi4d[:,:,:,0]
    dim2 = epi4d[:,:,:,1]
    img1 = nib.Nifti1Image(dim1, img.affine)
    img2 = nib.Nifti1Image(dim2, img.affine)
    img1.to_filename(f"{DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_EPI-1.nii.gz")
    img2.to_filename(f"{DIR}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_EPI-2.nii.gz")



def replace_affine_or_header(path_to_img, path_to_target, affine=True, header=False):
    img = nib.load(path_to_img)
    target = nib.load(path_to_target)
    
    fdata = img.get_fdata()
    if affine and header:
        new_image = nib.Nifti1Image(fdata, target.affine, target.header)
        
        nib.save(new_image, path_to_img.replace('.nii.gz', 
                                                '_corr-aff-head.nii.gz'))
    elif affine and not header:
        new_image = nib.Nifti1Image(fdata, target.affine, img.header)
        nib.save(new_image, path_to_img.replace('.nii.gz', 
                                                '_corr-aff.nii.gz'))
    elif not affine and header:
        new_image = nib.Nifti1Image(fdata, img.affine, target.header)
        nib.save(new_image, path_to_img.replace('.nii.gz', 
                                                '_corr-head.nii.gz'))
    
    


if __name__ == '__main__':
    EPI_magnitude = 'acq-mag_T2star'
    EPI_phase = 'acq-phase_T2star'
    phase_wrapped = 'phase_WRAPPED'
    T2 = 'T2'
    T1 = 'T1'
    T1_Gd = 'T1w_Gd'
    FLAIRstar = 'acq-star_FLAIR'


    # reorient('027','01', EPI_phase, 'y',DIR='E:\DISSECT_MS_DATABASE')

    # separate_epi('017','01',DIR='E:\DISSECT_MS_DATABASE')





