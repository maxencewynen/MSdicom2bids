#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 27 09:46:21 2022

@author: stluc
"""

from tqdm.auto import tqdm
import logging
from my_logging import setup_logging
import time


def long_procedure():

    setup_logging('long_procedure')
    __logger = logging.getLogger('long_procedure')
    __logger.setLevel(logging.DEBUG)
    tqdm_obect = tqdm(range(10), unit_scale=True, dynamic_ncols=True)
    tqdm_obect.set_description("My progress bar description")
    for i in tqdm_obect:
        time.sleep(.1)
        __logger.info('foo {}'.format(i))