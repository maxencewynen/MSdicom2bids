# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 13:15:41 2021

@author: Maxence Wynen
"""


CHUV = \
    {('\\derivatives\\autosplit_lesions_morpho_v01',        'splitmask.csv'):                           None,
     ('\\derivatives\\autosplit_lesions_morpho_v01',        'splitmask.nii.gz'):                        None,
     ('\\derivatives\\autosplit_lesions_morpho_v01',        'splitmask_result.nii.gz'):                 None,
     ('\\derivatives\\autosplit_lesions_morpho_v01',        'splitmask_rimpos.nii.gz'):                 None,
     ('\\derivatives\\autosplit_lesions_morpho_v02',        'splitmask.csv'):                           None,
     ('\\derivatives\\autosplit_lesions_morpho_v02',        'splitmask.nii.gz'):                        None,
     ('\\derivatives\\autosplit_lesions_morpho_v02',        'splitmask_result.nii.gz'):                 None,
     ('\\derivatives\\autosplit_lesions_morpho_v02',        'splitmask_rimpos.nii.gz'):                 None,
     ('\\derivatives\\autosplit_lesions_morpho_v02_maxDA',  'splitmask.csv'):                           None,
     ('\\derivatives\\autosplit_lesions_morpho_v02_maxDA',  'splitmask.nii.gz'):                        None,
     ('\\derivatives\\autosplit_lesions_morpho_v02_maxDA',  'splitmask_result.nii.gz'):                 None,
     ('\\derivatives\\autosplit_lesions_morpho_v02_maxDA',  'splitmask_rimpos.nii.gz'):                 None,
     
     ('\\derivatives\\expert_annotations',                  'expertsannotations.nii.gz'):               [{'derivatives': 'lesionmasks', 'registration': 'T2star', 'new_name': "prl-2d_lesions"}],
     
     ('\\derivatives\\freesurfer_segmentation',             'segmentation.nii.gz'):                     [{'derivatives': 'freesurfer_segmentation', 'registration': 'MPRAGE', 'new_name': 'brain-labeled'}],
     ('\\derivatives\\freesurfer_segmentation',             'segmentationFS.mgz'):                      None,
     ('\\derivatives\\freesurfer_segmentation',             'segmentationREG.nii.gz'):                  [{'derivatives': 'freesurfer_segmentation', 'registration': 'T2star', 'new_name': 'brain-labeled'}],
     ('\\derivatives\\freesurfer_segmentation',             'segmentationREG_MS.nii.gz'):               [{'derivatives': 'freesurfer_segmentation', 'registration': 'T2star', 'new_name': 'brain-labeled_dilated'}],
     ('\\derivatives\\freesurfer_segmentation',             'segmentation_fixed.nii.gz'):               None,
     
     ('\\derivatives\\lesions_34_34_34',                    'json'):                                    [{'derivatives': 'lesions_34_34_34', 'registration': 'T2star', 'new_name': None}],
     ('\\derivatives\\lesions_34_34_34',                    'acq-mag_T2star.dat'):                      [{'derivatives': 'lesions_34_34_34', 'registration': 'T2star', 'new_name': None}],
     ('\\derivatives\\lesions_34_34_34',                    'acq-phase_T2star.dat'):                    [{'derivatives': 'lesions_34_34_34', 'registration': 'T2star', 'new_name': None}],
     ('\\derivatives\\lesions_34_34_34',                    'acq-star_FLAIR.dat'):                      [{'derivatives': 'lesions_34_34_34', 'registration': 'T2star', 'new_name': None}],
     ('\\derivatives\\lesions_34_34_34',                    'FLAIR.dat'):                               [{'derivatives': 'lesions_34_34_34', 'registration': 'T2star', 'new_name': None}],
     ('\\derivatives\\lesions_34_34_34',                    'mask.dat'):                                [{'derivatives': 'lesions_34_34_34', 'registration': 'T2star', 'new_name': None}],
     
     ('\\derivatives\\mask_predictions_rimnet_v1',          'mask-predictions_rimnet-v1.nii.gz'):       [{'derivatives': 'mask_predictions_rimnet_v1', 'registration': 'T2star', 'new_name': None}],
     
     ('\\derivatives\\registrations_to_T2star',             'acq-MPRAGE_T1map.nii.gz'):                 [{'derivatives': None, 'registration': 'T2star', 'new_name': 'acq-MPRAGE_T1w'}],
     ('\\derivatives\\registrations_to_T2star',             'FLAIR.nii.gz'):                            [{'derivatives': None, 'registration': 'T2star', 'new_name': None}],
     
     ('\\derivatives\\rims_annotations',                    'mask.nii.gz'):                             [{'derivatives': 'lesionmasks', 'registration': 'T2star', 'new_name': 'labeled_lesions'}],
     
     ('\\derivatives\\segmentations',                       'segmentation.nii.gz'):                     [{'derivatives': 'lesionmasks', 'registration': 'T2star', 'new_name': "binary_lesions"}],
     
     ('\\derivatives\\skull_stripped',                      'acq-MP2RAGEsynthetic_T1map.nii.gz'):       None,
     ('\\derivatives\\skull_stripped',                      'acq-MPRAGE_T1map.nii.gz'):                 None,
     
     ('\\derivatives\\synthetic_mp2rage',                   'acq-MP2RAGEsynthetic_T1map.nii.gz'):       [{'derivatives': 'synthetic_mp2rage', 'registration': 'MPRAGE', 'new_name': 'UNIT1-syn'}], # skullstripped and normalized
     ('\\derivatives\\synthetic_mp2rage',                   'acq-MPRAGE_T1map.nii.gz'):                 None,
     ('\\derivatives\\synthetic_mp2rage',                   'brainmask.nii.gz'):                        None,
     ('\\derivatives\\synthetic_mp2rage',                   'brainmaskREG.nii.gz'):                     None,
     ('\\derivatives\\synthetic_mp2rage',                   'acq-MP2RAGEsynthetic_T1map_OLD.nii.gz'):   None,
     ('\\derivatives\\synthetic_mp2rage',                   'acq-MPRAGE_T1map_OLD.nii.gz'):             None,
     ('\\derivatives\\synthetic_mp2rage',                   'brainmask_OLD.nii.gz'):                    None,
     
     ('\\anat',                                             'acq-mag_T2star.nii.gz'):                   [{'derivatives': None, 'registration': None, 'new_name': None},
                                                                                                         {'derivatives': None, 'registration': 'T2star', 'new_name': None}],
     ('\\anat',                                             'acq-MPRAGE_T1map.nii.gz'):                 [{'derivatives': None, 'registration': None, 'new_name': 'acq-MPRAGE_T1w'}, 
                                                                                                         {'derivatives': None, 'registration': 'MPRAGE', 'new_name': 'acq-MPRAGE_T1w'}],
     ('\\anat',                                             'acq-phase_T2star.nii.gz'):                 [{'derivatives': None, 'registration': None, 'new_name': None},
                                                                                                         {'derivatives': None, 'registration': 'T2star', 'new_name': None}],
     ('\\anat',                                             'acq-star_FLAIR.nii.gz'):                   [{'derivatives': 'acq-star_FLAIR', 'registration': None, 'new_name': None},
                                                                                                         {'derivatives': 'acq-star_FLAIR', 'registration': 'T2star', 'new_name': None}],
     ('\\anat',                                             'FLAIR.json'):                              [{'derivatives': None, 'registration': None, 'new_name': None},
                                                                                                         {'derivatives': None, 'registration': 'FLAIR', 'new_name': None}],
     ('\\anat',                                             'FLAIR.nii.gz'):                            [{'derivatives': None, 'registration': None, 'new_name': None},
                                                                                                         {'derivatives': None, 'registration': 'FLAIR', 'new_name': None}],
     ('\\anat',                                             'acq-MPRAGE_T1map_OLD.nii.gz'):             None
     }
    
    
    
    
BASEL = \
    {('\\derivatives\\autosplit_lesions_morpho_v01',        'splitmask.csv'):                           None,
     ('\\derivatives\\autosplit_lesions_morpho_v01',        'splitmask.nii.gz'):                        None,
     ('\\derivatives\\autosplit_lesions_morpho_v01',        'splitmask_result.nii.gz'):                 None,
     ('\\derivatives\\autosplit_lesions_morpho_v01',        'splitmask_rimpos.nii.gz'):                 None,
     ('\\derivatives\\autosplit_lesions_morpho_v02',        'splitmask.csv'):                           None,
     ('\\derivatives\\autosplit_lesions_morpho_v02',        'splitmask.nii.gz'):                        None,
     ('\\derivatives\\autosplit_lesions_morpho_v02',        'splitmask_result.nii.gz'):                 None,
     ('\\derivatives\\autosplit_lesions_morpho_v02',        'splitmask_rimpos.nii.gz'):                 None,
     ('\\derivatives\\autosplit_lesions_morpho_v02_maxDA',  'splitmask.csv'):                           None,
     ('\\derivatives\\autosplit_lesions_morpho_v02_maxDA',  'splitmask.nii.gz'):                        None,
     ('\\derivatives\\autosplit_lesions_morpho_v02_maxDA',  'splitmask_result.nii.gz'):                 None,
     ('\\derivatives\\autosplit_lesions_morpho_v02_maxDA',  'splitmask_rimpos.nii.gz'):                 None,
     ('\\derivatives\\autosplit_lesions_v02',               'splitmask.csv'):                           None,
     ('\\derivatives\\autosplit_lesions_v02',               'splitmask.nii.gz'):                        None,
     ('\\derivatives\\autosplit_lesions_v02',               'splitmaskprobblurred.nii.gz'):             None,
     ('\\derivatives\\autosplit_lesions_v02',               'splitmask_result.nii.gz'):                 None,
     ('\\derivatives\\autosplit_lesions_v02',               'splitmask_rimpos.nii.gz'):                 None,
     ('\\derivatives\\autosplit_lesions_v03',               'splitmask.csv'):                           None,
     ('\\derivatives\\autosplit_lesions_v03',               'splitmask.nii.gz'):                        None,
     ('\\derivatives\\autosplit_lesions_v03',               'splitmaskprobblurred.nii.gz'):             None,
     ('\\derivatives\\autosplit_lesions_v03',               'splitmask_result.nii.gz'):                 None,
     ('\\derivatives\\autosplit_lesions_v03',               'splitmask_rimpos.nii.gz'):                 None,
     ('\\derivatives\\autosplit_lesions_v04',               'splitmask.csv'):                           None,
     ('\\derivatives\\autosplit_lesions_v04',               'splitmask.nii.gz'):                        None,
     ('\\derivatives\\autosplit_lesions_v04',               'splitmaskprobblurred.nii.gz'):             None,
     ('\\derivatives\\autosplit_lesions_v04',               'splitmask_result.nii.gz'):                 None,
     ('\\derivatives\\autosplit_lesions_v04',               'splitmask_rimpos.nii.gz'):                 None,
     ('\\derivatives\\autosplit_lesions_v05',               'splitmask.csv'):                           None,
     ('\\derivatives\\autosplit_lesions_v05',               'splitmask.nii.gz'):                        None,
     ('\\derivatives\\autosplit_lesions_v05',               'splitmaskprobblurred.nii.gz'):             None,
     ('\\derivatives\\autosplit_lesions_v05',               'splitmask_result.nii.gz'):                 None,
     ('\\derivatives\\autosplit_lesions_v05',               'splitmask_rimpos.nii.gz'):                 None,
     #
     ('\\derivatives\\expert_annotations',                  'expertsannotations.nii.gz'):               [{'derivatives': 'lesionmasks', 'registration': 'T2star', 'new_name': "prl-2d_lesions"}],
     
     ('\\derivatives\\freesurfer_segmentation',             'segmentation.nii.gz'):                     [{'derivatives': 'freesurfer_segmentation', 'registration': 'MP2RAGE', 'new_name': 'brain-labeled'}],
     ('\\derivatives\\freesurfer_segmentation',             'segmentationFS.mgz'):                      None,
     ('\\derivatives\\freesurfer_segmentation',             'segmentationREG.nii.gz'):                  [{'derivatives': 'freesurfer_segmentation', 'registration': 'T2star', 'new_name': 'brain-labeled'}],
     ('\\derivatives\\freesurfer_segmentation',             'segmentationREG_MS.nii.gz'):               [{'derivatives': 'freesurfer_segmentation', 'registration': 'T2star', 'new_name': 'brain-labeled_dilated'}],
     
     ('\\derivatives\\lesions_34_34_34',                    'json'):                                    [{'derivatives': 'lesions_34_34_34', 'registration': 'T2star', 'new_name': None}],
     ('\\derivatives\\lesions_34_34_34',                    'acq-mag_T2star.dat'):                      [{'derivatives': 'lesions_34_34_34', 'registration': 'T2star', 'new_name': None}],
     ('\\derivatives\\lesions_34_34_34',                    'acq-MP2RAGEuni_T1map.dat'):                [{'derivatives': 'lesions_34_34_34', 'registration': 'T2star', 'new_name': None}],
     ('\\derivatives\\lesions_34_34_34',                    'acq-MP2RAGE_T1map.dat'):                   [{'derivatives': 'lesions_34_34_34', 'registration': 'T2star', 'new_name': None}],
     ('\\derivatives\\lesions_34_34_34',                    'acq-phase_T2star.dat'):                    [{'derivatives': 'lesions_34_34_34', 'registration': 'T2star', 'new_name': None}],
     ('\\derivatives\\lesions_34_34_34',                    'acq-star_FLAIR.dat'):                      [{'derivatives': 'lesions_34_34_34', 'registration': 'T2star', 'new_name': None}],
     ('\\derivatives\\lesions_34_34_34',                    'FLAIR.dat'):                               [{'derivatives': 'lesions_34_34_34', 'registration': 'T2star', 'new_name': None}],
     ('\\derivatives\\lesions_34_34_34',                    'mask.dat'):                                [{'derivatives': 'lesions_34_34_34', 'registration': 'T2star', 'new_name': None}],
     
     ('\\derivatives\\registrations_to_T2star',             'acq-MP2RAGEuni_T1map.nii.gz'):             [{'derivatives': 'MP2RAGE', 'registration': 'MP2RAGE', 'new_name': 'UNIT1'}],
     ('\\derivatives\\registrations_to_T2star',             'acq-MP2RAGE_T1map.nii.gz'):                [{'derivatives': 'MP2RAGE', 'registration': 'MP2RAGE', 'new_name': 'T1map'}],
     ('\\derivatives\\registrations_to_T2star',             'FLAIR.nii.gz'):                            [{'derivatives': None, 'registration': 'FLAIR', 'new_name': None}],
     
     ('\\derivatives\\rims_annotations',                    'mask.nii.gz'):                             [{'derivatives': 'lesionmasks', 'registration': 'T2star', 'new_name': 'labeled_lesions'}],
     
     ('\\derivatives\\segmentations',                       'segmentation.nii.gz'):                     [{'derivatives': 'lesionmasks', 'registration': 'T2star', 'new_name': "binary_lesions"}],
     # lesion probability maps
     ('\\derivatives\\segmentation_probability_maps',       'probabilitiesmap.nii.gz'):                 [{'derivatives': 'lesionmasks', 'registration': 'MP2RAGE', 'new_name': "probability_lesions"}],
     ('\\derivatives\\segmentation_probability_maps',       'probabilitiesmapREG.nii.gz'):              [{'derivatives': 'lesionmasks', 'registration': 'T2star', 'new_name': "probability_lesions"}],
     
     ('\\derivatives\\synthetic_mp2rage',                   'brainmaskREG.nii.gz'):                     None,
     
     ('\\anat',                                             'acq-mag_T2star.nii.gz'):                   [{'derivatives': None, 'registration': None, 'new_name': None},
                                                                                                         {'derivatives': None, 'registration': 'T2star', 'new_name': None}],
     ('\\anat',                                             'acq-MP2RAGEuni_T1map.nii.gz'):             [{'derivatives': 'MP2RAGE', 'registration': None, 'new_name': 'UNIT1'},
                                                                                                         {'derivatives': 'MP2RAGE', 'registration': 'MP2RAGE', 'new_name': 'UNIT1'}],
     ('\\anat',                                             'acq-MP2RAGE_T1map.nii.gz'):                [{'derivatives': 'MP2RAGE', 'registration': None, 'new_name': 'T1map'},
                                                                                                         {'derivatives': 'MP2RAGE', 'registration': 'MP2RAGE', 'new_name': 'T1map'}],
     ('\\anat',                                             'acq-phase_T2star.nii.gz'):                 [{'derivatives': None, 'registration': None, 'new_name': None},
                                                                                                         {'derivatives': None, 'registration': 'T2star', 'new_name': None}],
     ('\\anat',                                             'acq-star_FLAIR.nii.gz'):                   [{'derivatives': 'acq-star_FLAIR', 'registration': None, 'new_name': None},
                                                                                                         {'derivatives': 'acq-star_FLAIR', 'registration': 'T2star', 'new_name': None}],
     ('\\anat',                                             'FLAIR.nii.gz'):                            [{'derivatives': None, 'registration': None, 'new_name': None},
                                                                                                         {'derivatives': None, 'registration': 'FLAIR', 'new_name': None}]
     }