#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 21 09:54:15 2022

@author: ColinVDB
"""

import os
from os.path import join as pjoin
from os.path import exists as pexists
from pydicom import dcmread
import pandas as pd
from dicom2bids import *

root_dir = '/media/stluc/ColinVDB/DISSECT_MS/BIDS_R4'
sourcedata = root_dir + '/sourcedata'
participants = root_dir + '/participants.tsv'

bids = BIDSHandler(root_dir)

#%% All subject and sessions
all_directories = [x for x in next(os.walk(root_dir))[1]]
all_sub_dir = []
for d in all_directories:
    if d.find('sub-') == 0:
        all_sub_dir.append(d)

all_sub_dir = sorted(all_sub_dir)
subject_and_sessions = []
for sub in all_sub_dir: 
    print(sub)
    sessions = [x for x in next(os.walk(f'{root_dir}/{sub}'))[1]]
    sessions = [d for (d, remove) in zip(sessions, [x and 'ses' in x for x in sessions]) if remove]
    print(sessions)
    sessions = sorted(sessions)
    sessions = [x.split('-')[1] for x in sessions]
    print(sessions)
    subject_and_sessions.append((sub.split('-')[1], sessions))
    
print(subject_and_sessions)

#%%
wrong_extensions = ['.jsn', '.bval', '.bvec', '.nii', '.gz', '.jpg']

participants_df = pd.read_csv(participants, sep='\t')
participants_df.insert(2, 'patient_id', None)

for sub, sess in subject_and_sessions:
    for ses in sess:
        print(sub,ses)
        patient_id = None
        index = participants_df[participants_df['participant_id']==f'sub-{sub}'].index.values.astype(int)[0]
        for path,_,files in os.walk(pjoin(sourcedata, f'sub-{sub}', f'ses-{ses}')):
            for file in files:
                if "." not in file[0] or not any([ext in file for ext in wrong_extensions]):# exclude non-dicoms, good for messy folders
                    # read the file
                    try:
                        ds = dcmread(pjoin(path,file), force=True)
                        
                        patient_id = ds.get('PatientID')
                        
                        if patient_id != None:
                            participants_df.at[index, 'patient_id'] = patient_id
                            break
                    except Exception:
                        continue

#%%
subject_and_sessions = [('057',['01']),
                        ('058',['01']),
                        ('059',['01']),
                        ('060',['01']),
                        ('061',['01']),
                        ('062',['01']),
                        ('063',['01']),
                        ('064',['01'])
                        ]

#%%
for sub, sess in subject_and_sessions:
    for ses in sess:
        print(sub,ses)
        bids.anonymisation(sub, ses)