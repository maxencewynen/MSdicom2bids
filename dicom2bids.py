# -*- coding: utf-8 -*-
"""
Created on Wed Mar  3 13:16:48 2021

@author: maxen
"""


import os
import warnings
import subprocess
from pathlib import Path
from shutil import rmtree
import json
import shutil
from os.path import join as pjoin
from os.path import exists as pexists
import pandas as pd

from pydicom import dcmread

class BIDSHandler:
    def __init__(self, root_dir, dicom2niix_path="dcm2niix"):
        self.root_dir = root_dir

        self.IGNORED_SERIES = ['3Plane_Loc_SSFSE',
                               'Ax T2 Propeller',
                               'AX REFORMAT',
                               'Opt_DTI_corr',
                               "COR REFORMAT"]
        self.dicom2niix_path = dicom2niix_path

        all_directories = [x for x in next(os.walk(root_dir))[1]]
        all_subj_dir = []
        for d in all_directories:
            if d.find('sub-') == 0:
                all_subj_dir.append(d)
        self.number_of_subjects = len(all_subj_dir)

    @staticmethod
    def rename(series, filenames, path):
        if 'MPRAGE' in series or '3DT1' in series:
            return ["MPRAGE"]
        if 'FLAIR' in series.upper(): # ORIG ???
            return ["FLAIR"]
        if 'phase' in series or ("SWI_EPI" in series and "_ph" in series):
            return ["acq-phase_T2star"]
        if '3D EPI' in series or "SWI_EPI" in series:
            return ["acq-mag_T2star"]
        if 'Opt_DTI' in series or 'DWI' in series:
            if len(filenames)>1:
                new_filenames = []
                for filename in filenames:
                    new_filenames.append('DWI')
                return new_filenames
            else:
                return ["DWI"]
        if "T1map" in series:
            return ["T1map"]
        if "DIR" in series:
            return ['DIR']
        if "T2opt" in series:
            return ['T2']
        if "T1W" in series and "gd" in series:
            return ['T1w_Gd']
        if "MP2RAGE" in series:
            if len(filenames)>1:
                new_filenames = []
                for filename in filenames:
                    try:
                        with open(f'{path}/{filename}.json') as json_file:
                            df = json.load(json_file)
                            new_filenames.append(f"inv-{df['EchoNumber']}_part-mag_MP2RAGE")
                    except:
                        pass
                return new_filenames
            else:
                return ['UNIT1']

    @staticmethod
    def bold(string):
        return "\033[1m" + string + "\033[0m"

    @staticmethod
    def mkdir_if_not_exists(dirpath):
        if not pexists(dirpath):
            os.mkdir(dirpath)

    def convert_all_dicoms(self, directory, convert=True):
        """
        Converts all dicom files of a particular patient into multiple
        compressed nifti (.nii.gz) files.

        Parameters
        ----------
        directory : <str>
            Path to patient's DICOM directory.
        dicom2niix_path : <str>
            ONLY FOR WINDOWS USERS. Path to dcm2niix.exe file.

        Returns
        -------
        all_sequences : <list> of <tuple>
            List of tuples (Path to specific dicom series directory,
                            Series description).

        """
        directory = pjoin(directory)
        print("[INFO] Starting to convert ...")

        all_sequences = []
        for subdir, dirs, files in os.walk(directory):
            if len(dirs) !=0 or len(files)< 10:
                continue
            print(f"SUBDIR: {subdir}\tDIRS: {dirs}")#\nFILES: {files}\n")
            path = os.path.normpath(subdir)
            if convert:
                # print("\n\n>>> CALLED <<<")
                # print(' '.join(["dicom2niix", '-f', "\"%f_%p_%t_%s\"", "-p",
                #                  "y", "-z", "y", path]))
                subprocess.call([self.dicom2niix_path, '-f', "\"%f_%p_%t_%s\"",
                                  "-p", "y", "-z", "y", path])
            descr = dcmread(f"{path}/{files[0]}").SeriesDescription
            all_sequences.append((path, descr))
        all_sequences = [(x[0].replace('\\', '/'),x[1]) for x in all_sequences]

        print("[INFO] Converted dicom files to", end =" ")
        print(f"{BIDSHandler.bold(str(len(all_sequences)))} compressed nifti")
        return all_sequences

    @staticmethod
    def mkdirs_if_not_exist(root_dir, directories=["sourcedata",
                                                   "derivatives"]):

        assert pexists(root_dir), f"Root directory {root_dir} does not exist."

        for dirname in directories:
            BIDSHandler.mkdir_if_not_exists(pjoin(root_dir, dirname))


    def make_directories(self, pat_id=None, session=None,
                         derivatives = ['samseg',
                                           'stats',
                                           'segmentations',
                                           'QSM',
                                           'MP2RAGE',
                                           'acq-star_FLAIR',
                                           'acq-phase_T2star',
                                           'skullstripped'],
                        registrations = ['T2star',
                                         'FLAIR',
                                         'MPRAGE',
                                         'MP2RAGE',
                                         'dwi',
                                         'T1',
                                         'T2',
                                         'ce-gado_T1w']):
        return self.make_directories_from(self.root_dir,
                                          pat_id,
                                          session,
                                          derivatives,
                                          registrations)

    @staticmethod
    def make_directories_from(bids_dir,
                            pat_id=None,
                            session=None,
                            derivatives = ['samseg',
                                           'stats',
                                           'segmentations',
                                           'QSM',
                                           'MP2RAGE',
                                           'acq-star_FLAIR',
                                           'skullstripped'],
                            registrations = ['T2star',
                                             'FLAIR',
                                             'MPRAGE',
                                             'MP2RAGE',
                                             'dwi',
                                             'T1',
                                             'T2',
                                             'ce-gado_T1w']):

        if registrations is None:
            BIDSHandler.mkdirs_if_not_exist(bids_dir,
                                            directories=["derivatives"])
        else:
            BIDSHandler.mkdirs_if_not_exist(bids_dir,
                                            directories=["sourcedata",
                                                         "derivatives"])

        define_pat_id = pat_id is None

        # Assign a database ID to the patient
        if define_pat_id:
            all_directories = [x for x in next(os.walk(bids_dir))[1]]
            all_subj_dir = []
            for d in all_directories:
                if d.find('sub-') == 0:
                    all_subj_dir.append(d)

            if all_subj_dir == []:
                pat_id = "001"
            else:
                subjects = [int(x.split('-')[1]) for x in all_subj_dir]
                pat_id = str((max(subjects) + 1)).zfill(3)

        subj_dir = pjoin(bids_dir,f"sub-{pat_id}")
        BIDSHandler.mkdir_if_not_exists(subj_dir)

        if session is None:
            all_directories = [x for x in next(os.walk(subj_dir))[1]]
            all_ses_dir = []
            for d in all_directories:
                if d.find('ses-') == 0:
                    all_ses_dir.append(d)
            if define_pat_id:
                session = "01"
            else:
                sessions = [int(x.split('-')[1]) for x in all_ses_dir]
                if len(sessions) == 0:
                    session = '01'
                else:
                    session = str(max(sessions) + 1).zfill(2)

        if registrations is not None:
            BIDSHandler.mkdir_if_not_exists(pjoin(bids_dir, 'sourcedata',
                                                  f'sub-{pat_id}'))
            BIDSHandler.mkdir_if_not_exists(pjoin(bids_dir, 'sourcedata',
                                                  f'sub-{pat_id}',
                                                  f'ses-{session}'))

        BIDSHandler.mkdir_if_not_exists(pjoin(subj_dir, f'ses-{session}'))
        BIDSHandler.mkdir_if_not_exists(pjoin(subj_dir, f'ses-{session}', 'anat'))
        BIDSHandler.mkdir_if_not_exists(pjoin(subj_dir, f'ses-{session}', 'dwi'))

        deriv = pjoin(bids_dir, 'derivatives')

        def add_derivatives_dirs(derivative):
            BIDSHandler.mkdir_if_not_exists(pjoin(deriv, derivative, f'sub-{pat_id}'))
            BIDSHandler.mkdir_if_not_exists(pjoin(deriv, derivative,
                                                  f'sub-{pat_id}', f'ses-{session}'))


        all_derivatives = [x for x in next(os.walk(deriv))[1]]

        if derivatives is None:
            derivatives = []

        if registrations is None:
            all_derivatives.append("transformation_matrices")
            all_derivatives.append("lesionmasks")

        all_derivatives = list(set().union(all_derivatives, derivatives))

        BIDSHandler.mkdirs_if_not_exist(deriv, all_derivatives)
        if registrations is not None:
            BIDSHandler.mkdir_if_not_exists(pjoin(deriv, 'registrations'))

        if "registrations" in all_derivatives:
            all_derivatives.remove("registrations")

        for derivative in all_derivatives:
            add_derivatives_dirs(derivative)


        if not registrations is None:
            for registration in registrations:
                reg_path = pjoin(deriv, 'registrations',
                                 "registrations_to_" + registration)
                BIDSHandler.mkdir_if_not_exists(reg_path)

                BIDSHandler.make_directories_from(reg_path,
                                                  pat_id=pat_id,
                                                  session=session,
                                                  derivatives = all_derivatives,
                                                  registrations = None)


                if registration != 'T2star': continue

                reg_path = pjoin(deriv, 'registrations',
                             f"registrations_to_{registration}_ses-01")
                BIDSHandler.mkdir_if_not_exists(reg_path)

                BIDSHandler.make_directories_from(reg_path,
                                                  pat_id=pat_id,
                                                  session=session,
                                                  derivatives = all_derivatives,
                                                  registrations = None)

        return pat_id, session

    @staticmethod
    def delete_if_exists(dirpath):
        if pexists(dirpath):
            rmtree(dirpath)
        else:
            print("[Exception] Cannot remove directory that does not exists:")
            print(f"\t{dirpath}")

    def delete_subject(self, pat_id, delete_sourcedata=False):
        bids_dir = self.root_dir
        subject_dirs = [dirpath for dirpath, subdirs, _ in os.walk(bids_dir)
                        if dirpath.endswith(f"sub-{pat_id}")]

        for s in subject_dirs:
            if "sourcedata" in s:
                if delete_sourcedata: rmtree(s)
            else:
                rmtree(s)

    def delete_session(self, pat_id, session, delete_sourcedata=False):
        bids_dir = self.root_dir
        dirs = [dirpath for dirpath, subdirs, _ in os.walk(bids_dir)
                    if f"sub-{pat_id}" in dirpath and
                        dirpath.endswith(f"ses-{session}")]

        for s in dirs:
            if "sourcedata" in s:
                if delete_sourcedata: rmtree(s)
            else:
                rmtree(s)


    def rename_and_move_nifti(self, dicom_series, pat_id, session='01'):

        def move_all(path, filename, file_extensions, dest_dir, new_filename):
            print(filename)
            for file_extension in file_extensions:
                if pexists(pjoin(path, f"{filename}.{file_extension}")):
                    if pexists(pjoin(dest_dir, f"{new_filename}.{file_extension}")):
                        print('File already existing in dest dir', pjoin(dest_dir, f"{new_filename}.{file_extension}"))
                        ext = 'a'
                        for i in range(26):
                            if not pexists(pjoin(dest_dir, f"{new_filename}_{ext}.{file_extension}")):
                                shutil.move(pjoin(path, f"{filename}.{file_extension}"),
                                        pjoin(dest_dir, f"{new_filename}_{ext}.{file_extension}"))
                                break
                            else:
                                ext = chr(ord(ext)+1)
                    else:
                        shutil.move(pjoin(path, f"{filename}.{file_extension}"),
                            pjoin(dest_dir, f"{new_filename}.{file_extension}"))

        bids_dir = self.root_dir

        if len(dicom_series) == 1:
            path, series = dicom_series[0]
            moved = []
            for file in os.listdir(path):
                if not file.endswith(".nii.gz") \
                    or file.replace(".nii.gz", "") in moved:
                    continue

                if file in self.IGNORED_SERIES or 'Survey' in file:
                    os.remove(pjoin(path, file))
                    os.remove(pjoin(path, file.replace('.nii.gz', '.json')))
                    moved.append(file.replace(".nii.gz", ""))
                    continue

                new_names = self.rename(file.replace(".nii.gz", ""),
                                        [file.replace(".nii.gz", "")],
                                        path)
                print(new_names)
                if new_names is None:
                    print(f"DICOM series not recognized: {file.replace('.nii.gz','')}")
                    print(f"Path: {path}")
                    new_names = [file.replace(".nii.gz", "")]

                for filename, new_name in zip([file.replace(".nii.gz", "")],
                                              new_names):
                    dos = 'dwi' if new_name == 'DWI' else 'anat'
                    if new_name == "DWI":
                        move_all(path,
                                 filename,
                                 ["nii.gz", "json", "bval", "bvec"],
                                 pjoin(bids_dir, f"sub-{pat_id}",
                                       f"ses-{session}", dos),
                                 f"sub-{pat_id}_ses-{session}_{new_name}")
                    elif new_name == "T1map" or new_name == "UNIT1":
                        move_all(path,
                                 filename,
                                 ["nii.gz", "json"],
                                 pjoin(bids_dir, "derivatives", "MP2RAGE",
                                       f"sub-{pat_id}", f"ses-{session}"),
                                 f"sub-{pat_id}_ses-{session}_{new_name}")
                    else:
                        move_all(path, filename, ["nii.gz", "json"],
                                pjoin(bids_dir, f"sub-{pat_id}",
                                      f"ses-{session}", dos),
                                f"sub-{pat_id}_ses-{session}_{new_name}")

                moved.append(file.replace(".nii.gz", ""))


        for path, series in dicom_series:
            if series in self.IGNORED_SERIES or 'ORIG' in series \
                                            or 'PSIR' in series \
                                            or 'Survey' in series:
                for file in os.listdir(path):
                    if file.endswith(".nii.gz") or file.endswith(".json"):
                        os.remove(pjoin(path, file))
                continue
            nifti_filenames = []
            for obj in list(os.walk(path))[0][2]:
                if obj.find('.nii.gz') <= 0:
                    continue
                nifti_filenames.append( obj.replace('.nii.gz', '') )


            new_names = BIDSHandler.rename(series, nifti_filenames, path)
            if new_names is None:
                print(f"DICOM series not recognized: {series}\nPath: {path}")
                new_names = nifti_filenames
            for filename, new_name in zip(nifti_filenames, new_names):
                dos = 'dwi' if new_name == 'DWI' else 'anat'
                if new_name == "DWI":
                    move_all(path,
                             filename,
                             ["nii.gz", "json", "bval", "bvec"],
                             pjoin(bids_dir, f"sub-{pat_id}",
                                   f"ses-{session}", dos),
                             f"sub-{pat_id}_ses-{session}_{new_name}")
                elif new_name == "T1map" or new_name == "UNIT1":
                    move_all(path,
                             filename,
                             ["nii.gz", "json"],
                             pjoin(bids_dir, "derivatives", "MP2RAGE",
                                   f"sub-{pat_id}", f"ses-{session}"),
                             f"sub-{pat_id}_ses-{session}_{new_name}")
                else:
                    move_all(path, filename, ["nii.gz", "json"],
                            pjoin(bids_dir, f"sub-{pat_id}",
                                  f"ses-{session}", dos),
                            f"sub-{pat_id}_ses-{session}_{new_name}")

            print(f"SERIES: {series}\n   Filenames: {nifti_filenames}\n", end = "")
            print(f"   RENAME: {BIDSHandler.rename(series, nifti_filenames, path)}\n\n")



    @staticmethod
    def delete_nii_json_in_dicomdir(dicom_series):
        for path, series in dicom_series:
            for file in os.listdir(path):
                if file.endswith(".nii.gz") or file.endswith(".json"):
                    os.remove(pjoin(path, file))


    def rename_subject(self, old_id, new_id):
        bids_dir = self.root_dir
        # Replaces all paths with "sub-old_id" by the same path with "sub-new_id"
        if pexists(pjoin(bids_dir, f'sub-{new_id}')):
            msg = f"Subject {new_id} already exists in the database. "
            msg += "Delete the subject first or choose another subject id."
            raise FileExistsError(msg)
        if not pexists(pjoin(bids_dir, f'sub-{old_id}')):
            raise FileNotFoundError(f"Subject {old_id} is not in the database.")

        for dirpath, _, files in os.walk(bids_dir):

            if "sourcedata" in dirpath: continue

            for filename in files:
                if filename.startswith(f'sub-{old_id}'):
                    shutil.move(pjoin(dirpath, filename),
                                pjoin(dirpath, filename.replace(f"sub-{old_id}",
                                                                f"sub-{new_id}")))

        for dirpath, _, _ in os.walk(bids_dir):
            if dirpath.endswith(f"sub-{old_id}"):
                shutil.move(dirpath, dirpath.replace(f"sub-{old_id}",
                                                     f"sub-{new_id}"))


    def copy_dicomfolder_to_sourcedata(self, dicomfolder, pat_id, session):
        sourcedata = pjoin(self.root_dir, "sourcedata")
        if pexists(pjoin(sourcedata, f"sub-{pat_id}",
                                       f"ses-{session}")) and \
            len(os.listdir(pjoin(sourcedata, f"sub-{pat_id}",
                                       f"ses-{session}"))) > 0:

            print("[ERROR] Error while trying to copy the dicom folder into")
            print(f"sourcedata folder: sourcedata/sub-{pat_id}/ses-{session}")
            print("already exists and is not empty.")
            print(" Please remove this directory and try again.")
            return


        self.mkdir_if_not_exists(sourcedata)
        self.mkdir_if_not_exists(pjoin(sourcedata, f"sub-{pat_id}"))
        self.mkdir_if_not_exists(pjoin(sourcedata, f"sub-{pat_id}",
                                       f"ses-{session}"))

        print("[INFO] Copying dicom folder to sourcedata ...")
        shutil.copytree(dicomfolder, pjoin(sourcedata, f"sub-{pat_id}",
                                       f"ses-{session}", "DICOM"))


    def convert_dicoms_to_bids(self, dicomfolder, pat_id=None, session=None,
                               return_dicom_series=False):

        pat_id = None if pat_id is None else str(int(pat_id)).zfill(3)
        session = None if session is None else str(int(session)).zfill(2)

        # Convert all DICOMs
        dicom_series = self.convert_all_dicoms(dicomfolder)

        # Create directories in the BIDS file structure by giving an incremental id
        # pat_id, session = make_directories(bids_dir,pat_id=None,session=None)
        # To specify the patient id:
        pat_id, session = self.make_directories(pat_id=pat_id,session=session)
        # To specify the patient id and session:
        # pat_id, session = make_directories(bids_dir,pat_id='ID_TO_SPECIFY',session='SESSION_TO_SPECIFY')

        # Rename and move all (interesting) converted files into the bids directory
        self.rename_and_move_nifti(dicom_series, pat_id, session)

        self.copy_dicomfolder_to_sourcedata(dicomfolder, pat_id, session)

        pat_name, pat_date = self.separate_dicoms(dicomfolder, pat_id, session)

        self.anonymisation(pat_name, pat_date, pat_id, session)

        if return_dicom_series:
            return pat_id, session, dicom_series
        return pat_id, session


    def separate_dicoms(self, src, sub, ses):
        print('[INFO] Sorting dicoms ...')
        def clean_text(string):
            # clean and standardize text descriptions, which makes searching files easier
            forbidden_symbols = ["*", ".", ",", "\"", "\\", "/", "|", "[", "]", ":", ";", " "]
            for symbol in forbidden_symbols:
                string = string.replace(symbol, "_") # replace everything with an underscore
            return string.lower()

        wrong_extensions = ['.jsn', '.bval', '.bvec', '.nii', '.gz', '.jpg']

        dst = f"{self.root_dir}/sourcedata/sub-{sub}/ses-{ses}/DICOM/sorted"

        print('reading file list...')
        unsortedList = []
        corresponding_root = []
        for root, dirs, files in os.walk(src):
            for file in files:
                if "." not in file[0] or not any([ext in file for ext in wrong_extensions]):# exclude non-dicoms, good for messy folders
                    unsortedList.append(os.path.join(root, file))
                    corresponding_root.append(root)

        print('%s files found.' % len(unsortedList))

        pat_name = None
        pat_date = None

        for dicom_loc in unsortedList:
            # read the file
            ds = dcmread(dicom_loc, force=True)

            if pat_name == None:
                pat_name = ds.get('PatientName')
            if pat_name == None:
                pat_name = ds.get('Name')
            if pat_date == None:
                pat_date = ds.get('ContentDate')
            if pat_date == None:
                pat_date = ds.get('Date')
            if pat_date == None:
                pat_date = ds.get('AcquisitionDate')

            # find folder_name
            path = dicom_loc.split('/')
            folder = path[len(path)-2]

            # get patient, study, and series information
            patientID = clean_text(ds.get("PatientID", "NA"))

            # generate new, standardized file name
            instanceNumber = str(ds.get("InstanceNumber","0"))

            # get scanning sequence
            scanning_sequence = ds.get("SeriesDescription")

            if scanning_sequence == None:
                scanning_sequence = ds.get("SequenceName")

            if scanning_sequence == None:
                scanning_sequence = "NoScanningSequence"

            scanning_sequence = folder + '_' + scanning_sequence

            scanning_sequence = clean_text(scanning_sequence)

            fileName = patientID + "_" + scanning_sequence + "_" + instanceNumber + ".dcm"

            # save files to a 4-tier nested folder structure
            if not os.path.exists(os.path.join(dst, scanning_sequence)):
                os.makedirs(os.path.join(dst, scanning_sequence))

            ds.save_as(os.path.join(dst, scanning_sequence, fileName))

        print('done.')

        return pat_name, pat_date

    def anonymisation(self, pat_name, pat_date, pat_id, pat_ses):

        if pexists(pjoin(self.root_dir, "anonymisation.csv")):
            anonym = pd.read_csv(pjoin(self.root_dir, "anonymisation.csv")).to_dict()
        else:
            anonym = {'PatientName':{}, 'Bids_ID':{}, 'Date ses-01':{}}

        # check if new patient
        if pat_ses != '01':
            key_num = list(anonym['Bids_ID'].values()).index(int(pat_id))
            if f'Date ses-{pat_ses}' not in anonym.keys():
                anonym[f'Date ses-{pat_ses}'] = {}
            # update dicionary with the date of the new session
            anonym[f'Date ses-{pat_ses}'][key_num] = pat_date
        else:
            # add new patient
            key_num = len(anonym['Bids_ID'])
            anonym['PatientName'][key_num] = pat_name
            anonym['Bids_ID'][key_num] = pat_id
            anonym['Date ses-01'][key_num] = pat_date

        # Save anonym dic to csv
        anonym_df = pd.DataFrame(anonym)
        anonym_df.to_csv(pjoin(self.root_dir, "anonymisation.csv"), index=False)

        print('[INFO] Anonymisation done')


if __name__ == '__main__':
    pass
    # dicom2niix_path = r"C:\Users\Cristina\Downloads\dcm2niix.exe"
    # bidshandler = BIDSHandler(root_dir=r"C:\Users\Cristina\Documents\deleteme\BIDS_EXAMPLE\BIDS_ROOT",#r"/media/maggi/MS-PRL/MS-PRL/MS-PRL_Brussels",
    #                       dicom2niix_path = dicom2niix_path)

    # DICOM_FOLDER = r"C:\Users\Cristina\Documents\deleteme\BIDS_EXAMPLE\131-DICOM"
    # PATIENT_ID = None
    # SESSION = None

    # pat_id, session, dicom_series = bidshandler.convert_dicoms_to_bids(dicomfolder = DICOM_FOLDER,
    #                                                                    pat_id      = PATIENT_ID,
    #                                                                    session     = SESSION,
    #                                                                    return_dicom_series=True)

    # print("[INFO] Done")


