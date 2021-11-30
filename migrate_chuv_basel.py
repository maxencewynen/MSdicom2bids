# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 12:25:46 2021

@author: Maxence Wynen
"""

import os
from os.path import join as pjoin
from pathlib import Path
from dicom2bids import BIDSHandler
import os
from os.path import join as pjoin
from os.path import exists as pexists
from shutil import copy as shcopy
from chuv_basel_infos import CHUV, BASEL
import logging
import json

basel = BIDSHandler(r"C:\Users\Cristina\Documents\TFG\3_datasets\BASEL_INSIDER")
chuv = BIDSHandler(r"C:\Users\Cristina\Documents\TFG\3_datasets\CHUV_RIM")

dataset_description = { 
	"Name": "", 
	"BIDSVersion":  "1.2.2", 
	"PipelineDescription": {
		"Name": ""
	}
}

def strip_filename(filename):
    f = str(Path(filename))
    f = f.replace(str(Path(basel.root_dir)), '')
    f = f.replace(str(Path(chuv.root_dir)), '')
    directories = []
    for s in f.split('\\'):
        if 'sub-' in s or 'ses-' in s:
            continue
        directories.append(s)
    
    return '\\'.join(directories)
      

def copy(source, dest):
    logging.info(f"Copying {source} to {dest}")
    dirname = os.path.dirname(dest)
    if not pexists(dirname):
        os.makedirs(dirname)
        
    shcopy(source, dest)
    
def migrate(old, new, infos):
    for subdir,_,files in os.walk(old.root_dir):
        for file in files:
            stripped = strip_filename(pjoin(subdir, file))
            if not 'sub' in file or not 'ses' in file:
                continue
            
            subses = file[:15]
            if len(subses.split('_')) == 3: sub, ses, _ = subses.split('_')
            elif len(subses.split('_')) == 2 : sub, ses = subses.split('_')
            
            extension = file[file.find('.'):]
            filename = file[15:]
            info = (stripped, filename)
            
            if infos[info] is None:
                continue
            
            def make_new_name(loc, dest):
                if loc['new_name'] is None:
                    new_name = file
                else:
                    new_name = subses + loc['new_name'] + extension
                return pjoin(dest, new_name)
                
            
            for loc in infos[info]:
                if loc['registration'] is None:
                    if loc['derivatives'] is None:
                        dest = pjoin(new.root_dir, sub, ses, 'anat')
                        dest = make_new_name(loc, dest)
                    else:
                        dest = pjoin(new.root_dir, 'derivatives', loc['derivatives'], sub, ses)
                        dest = make_new_name(loc, dest)
                else:
                    if loc['derivatives'] is None:
                        dest = pjoin(new.root_dir, 'derivatives', 'registrations', 
                                     f"registrations_to_{loc['registration']}", sub, ses, 'anat')
                        dest = make_new_name(loc, dest)
                    else:
                        dest = pjoin(new.root_dir, 'derivatives', 'registrations', 
                                     f"registrations_to_{loc['registration']}", 
                                     'derivatives', loc['derivatives'], sub, ses)
                        dest = make_new_name(loc, dest)
                copy(pjoin(subdir, file), pjoin(new.root_dir, dest))
            
            
    # Add metadata files
    for filename in os.listdir(old.root_dir):
        file = pjoin(old.root_dir, filename)
        if os.path.isfile(file):
            shcopy(file, pjoin(new.root_dir, filename))
    
    # Add dataset_description.json files in derivatives
    for subdir,_,_ in os.walk(new.root_dir):
        if subdir.endswith('derivatives'):
            for d in os.listdir(subdir):
                if os.path.isdir(pjoin(subdir,d)):
                    dataset_description["Name"] = d
                    dataset_description["PipelineDescription"]["Name"] = d
                    with open(pjoin(subdir, d, 'dataset_description.json'), 'w') as fp:
                        json.dump(dataset_description, fp)
        



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, filename="logfile", filemode="a+",
                        format="%(asctime)-15s %(levelname)-8s %(message)s")
    
    chuv_new = BIDSHandler(r'C:\Users\Cristina\Desktop\DATA_MIAL\CHUV_BOK')
    basel_new = BIDSHandler(r'C:\Users\Cristina\Desktop\DATA_MIAL\BASEL_BOK')
    
    
    
    migrate(chuv, chuv_new, CHUV)
    migrate(basel, basel_new, BASEL)
    logging.shutdown()