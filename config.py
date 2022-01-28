#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 16:30:16 2022

@author: ColinVDB
"""

IS_SETUP_DONE = 'is_setup_done'

TQDM_WRITE_STREAM_CONFIG = 'TQDM_WRITE_STREAM_CONFIG'
STDOUT_WRITE_STREAM_CONFIG = 'STDOUT_WRITE_STREAM_CONFIG'
IS_STREAMS_REDIRECTION_SETUP_DONE = 'IS_STREAMS_REDIRECTION_SETUP_DONE'

STREAM_CONFIG_KEY_QUEUE = 'queue'
STREAM_CONFIG_KEY_STREAM = 'write_stream'
STREAM_CONFIG_KEY_QT_QUEUE_RECEIVER = 'qt_queue_receiver'

default_config_dict = {
    IS_SETUP_DONE: False,
    IS_STREAMS_REDIRECTION_SETUP_DONE: False,
    TQDM_WRITE_STREAM_CONFIG: None,
    STDOUT_WRITE_STREAM_CONFIG: None,
}

config_dict = default_config_dict