# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 12:25:46 2021

@author: Maxence Wynen
"""

import os
from os.path import join as pjoin
from pathlib import Path

basel = r"C:\Users\Cristina\Documents\TFG\3_datasets\BASEL_INSIDER"
chuv = r"C:\Users\Cristina\Documents\TFG\3_datasets\CHUV_RIM"

def parse_filename(filename):
    filename = filename.replace(".nii.gz", "")
    filename = filename.replace(".json", "")
    parsed = {}
    ss = filename.split("_")
    if ss[-1].isnumeric():
        parsed["slicenbr"] = ss.pop(-1)
    
    for substring in ss:
        subsubstring = substring.split('-', 1)
        if len(subsubstring) > 1:
            parsed[subsubstring[0]] = subsubstring[1]
        else:
            parsed[subsubstring[0]] = None
    return parsed

def rename(a,b):
    print(a,b)



all_filenames = []

def strip_filename(filename):
    f = str(Path(filename))
    f = f.replace(str(Path(basel)), '')
    f = f.replace(str(Path(chuv)), '')
    directories = []
    for s in f.split('\\'):
        if 'sub-' in s or 'ses-' in s:
            continue
        directories.append(s)
    
    return '\\'.join(directories)
        
    

for subdir,_,files in os.walk(chuv):
    for file in files:
        stripped = strip_filename(pjoin(subdir, file))
        if not 'sub' in file or not 'ses' in file:
            if 'autosplit' in stripped: continue
            print(stripped)
            continue
        
        filename = file[15:]
        if (stripped, filename) not in all_filenames:
            all_filenames.append((stripped, file[15:]))
        
        
    