#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 09:57:38 2022

@author: ColinVDB
get_part_of_bids_directory
"""

from dicom2bids import *
import os
from os.path import join as pjoin
from os.path import exists as pexists
import pandas as pd
import shutil


bids_dir = '/media/stluc/ColinVDB/DISSECT_MS/BIDS_R4'
output_dir = '/media/stluc/ColinVDB/share_R4'
bids = BIDSHandler(bids_dir)
sequences_to_get = [('anat','part-mag_T2starw'),
                    ('anat','FLAIR'),
                    ('anat','acq-MPRAGE_T1w'),
                    ('anat','acq-ax_T2w')
                    ]

#%%
subject_and_sessions = [('057',['01']),
                        ('058',['01']),
                        ('059',['01']),
                        ('060',['01']),
                        ('061',['01']),
                        ('062',['01']),
                        ('063',['01']),
                        ('064',['01']), 
                        ('003',['01']),
                        ('030',['01']),
                        ('032',['01']),
                        ('040',['01']),
                        ('022',['01']),
                        ('001',['01']),
                        ('046',['01']),
                        ('038',['01']),
                        ('056',['01']),
                        ('005',['01']),
                        ('017',['01']),
                        ('024',['01']),
                        ('036',['01']),
                        ('008',['01']),
                        ('029',['01']),
                        ('047',['01']),
                        ('031',['01']),
                        ('034',['01']),
                        ('055',['01']),
                        ('035',['01'])
                        ]

#%%
for sub, sess in subject_and_sessions:
    for ses in sess:
        print(sub, ses)
        for folder, seq in sequences_to_get:
            print(folder, seq)
            files_to_copy = []
            source_folder = pjoin(bids_dir, f'sub-{sub}', f'ses-{ses}', f'{folder}')
            for path,_,files in os.walk(source_folder):
                for file in files:
                    if f'sub-{sub}_ses-{ses}_{seq}' in file:
                        files_to_copy.append(pjoin(path, file))
            print('files found')
            directories = [pjoin(f'sub-{sub}'), pjoin(f'sub-{sub}', f'ses-{ses}'), pjoin(f'sub-{sub}', f'ses-{ses}', f'{folder}')]
            bids.mkdirs_if_not_exist(output_dir, directories=directories)
            dest = pjoin(output_dir, f'sub-{sub}', f'ses-{ses}', f'{folder}')
            for file in files_to_copy:
                shutil.copy(file, dest)
    
                