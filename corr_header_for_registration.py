#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 22 11:45:32 2021

@author: ColinVSB
"""

import nibabel as nib

"""
function corr_header_for_registration: 
    used to correct the header of the nifti file when there is the "No 
    orhtonormal definition found" error from ANTs registration. 
    args: *filename: filename of the nifti image with the header to be corrected
    output: save the corrected image in the same directory
"""
def corr_header_for_registration(filename):
    mri = nib.load(filename)
    
    # correction of the header
    mri.header['qform_code'] = 1
    
    # get the path to the directory
    name = filename.split('.')
    
    # creation of the output name for the output file
    output_name = name[0]+'_corr-reg.nii.gz'
    
    nib.save(mri, output_name)