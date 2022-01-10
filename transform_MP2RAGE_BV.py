#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 19 14:51:03 2021

@author: ColinVDB
MP2RAGE BV reorientation
"""

import nibabel as nib 
import numpy as np
import matplotlib.pyplot as plt

MP2RAGE = nib.load('/media/maggi/MS-PRL/MS-PRL/MS-PRL_NIH/DATA/sub-006/ses-01/anat/sub-006_ses-01_MP2RAGE.nii.gz')
MP2RAGE_d = MP2RAGE.get_fdata()

MP2RAGE_BV = nib.load('/media/maggi/MS-PRL/MS-PRL/MS-PRL_NIH/DATA/sub-006/ses-01/anat/006.nii.gz')
MP2RAGE_BV_d = MP2RAGE_BV.get_fdata()

#%% Visualisation of normal data
plt.figure(1)
plt.subplot(221)
plt.imshow(MP2RAGE_d[88,:,:], cmap='gray')
plt.subplot(222)
plt.imshow(MP2RAGE_d[:,120,:], cmap='gray')
plt.show()
plt.subplot(223)
plt.imshow(MP2RAGE_d[:,:,128], cmap='gray')
plt.show()

plt.figure(2)
plt.subplot(221)
plt.imshow(MP2RAGE_BV_d[88,:,:], cmap='gray')
plt.subplot(222)
plt.imshow(MP2RAGE_BV_d[:,120,:], cmap='gray')
plt.show()
plt.subplot(223)
plt.imshow(MP2RAGE_BV_d[:,:,128], cmap='gray')
plt.show()
#%% Operations
MP2RAGE_BV_rot = np.rot90(MP2RAGE_BV_d, axes=(0,2))
plt.figure(3)
plt.subplot(221)
plt.imshow(MP2RAGE_BV_rot[88,:,:], cmap='gray')
plt.subplot(222)
plt.imshow(MP2RAGE_BV_rot[:,120,:], cmap='gray')
plt.show()
plt.subplot(223)
plt.imshow(MP2RAGE_BV_rot[:,:,128], cmap='gray')
plt.show()

#%%
MP2RAGE_BV_rot_2 = np.rot90(MP2RAGE_BV_rot, axes=(1,2))
plt.figure(4)
plt.subplot(221)
plt.imshow(MP2RAGE_BV_rot_2[88,:,:], cmap='gray')
plt.subplot(222)
plt.imshow(MP2RAGE_BV_rot_2[:,120,:], cmap='gray')
plt.show()
plt.subplot(223)
plt.imshow(MP2RAGE_BV_rot_2[:,:,128], cmap='gray')
plt.show()

#%%
MP2RAGE_BV_rot_3 = np.rot90(MP2RAGE_BV_rot_2, axes=(0,1))
plt.figure(5)
plt.subplot(221)
plt.imshow(MP2RAGE_BV_rot_3[120,:,:], cmap='gray')
plt.subplot(222)
plt.imshow(MP2RAGE_BV_rot_3[:,128,:], cmap='gray')
plt.show()
plt.subplot(223)
plt.imshow(MP2RAGE_BV_rot_3[:,:,88], cmap='gray')
plt.show()

#%%
MP2RAGE_BV_rot_4 = np.rot90(MP2RAGE_BV_rot_3, axes=(1,2))
plt.figure(6)
plt.subplot(221)
plt.imshow(MP2RAGE_BV_rot_4[120,:,:], cmap='gray')
plt.subplot(222)
plt.imshow(MP2RAGE_BV_rot_4[:,128,:], cmap='gray')
plt.show()
plt.subplot(223)
plt.imshow(MP2RAGE_BV_rot_4[:,:,88], cmap='gray')
plt.show()

#%%
MP2RAGE_BV_rot_2_1 = np.flip(MP2RAGE_BV_rot_2, axis=(0,2))
plt.figure(7)
plt.subplot(221)
plt.imshow(MP2RAGE_BV_rot_2_1[88,:,:], cmap='gray')
plt.subplot(222)
plt.imshow(MP2RAGE_BV_rot_2_1[:,120,:], cmap='gray')
plt.show()
plt.subplot(223)
plt.imshow(MP2RAGE_BV_rot_2_1[:,:,128], cmap='gray')
plt.show()

#%%
MP2RAGE_BV_rot_2_2 = np.flip(MP2RAGE_BV_rot_2_1, axis=0)
plt.figure(8)
plt.subplot(221)
plt.imshow(MP2RAGE_BV_rot_2_2[88,:,:], cmap='gray')
plt.subplot(222)
plt.imshow(MP2RAGE_BV_rot_2_2[:,120,:], cmap='gray')
plt.show()
plt.subplot(223)
plt.imshow(MP2RAGE_BV_rot_2_2[:,:,128], cmap='gray')
plt.show()
#%% Compilation
def transform_MP2RAGE_BV(MP2RAGE_BV_filename):
    MP2RAGE_BV = nib.load('/media/maggi/MS-PRL/MS-PRL/MS-PRL_NIH/DATA/sub-006/ses-01/anat/006.nii.gz')
    MP2RAGE_BV_d = MP2RAGE_BV.get_fdata()
    # Operations
    MP2RAGE_BV_d = np.rot90(MP2RAGE_BV_d, axes=(0,2))
    MP2RAGE_BV_d = np.rot90(MP2RAGE_BV_d, axes=(1,2))
    MP2RAGE_BV_d = np.flip(MP2RAGE_BV_d, axis=(0,2))
    MP2RAGE_BV_d = np.flip(MP2RAGE_BV_d, axis=0)
    MP2RAGE_BV_o = nib.Nifti1Image(MP2RAGE_BV_d, MP2RAGE.affine)
    MP2RAGE_BV_name = MP2RAGE_BV_filename.split('.')
    # creation of the output name for the output file
    output_name = MP2RAGE_BV_name[0]+'_BVreoriented.nii.gz'
    nib.save(MP2RAGE_BV_o, output_name)
    print("[INFO] MP2RAGE_BV Reoriented !")

 