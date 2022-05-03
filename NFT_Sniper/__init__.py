import os
from re import L
import time
from collections import Counter
import yaml
import scipy
import json
import pickle
import shutil
import numpy as np
import pandas as pd
from sys import platform
from pprint import pprint
import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime
from functools import reduce
from dateutil.parser import parse

import PIL

matplotlib.use('agg')
getwd = os.getcwd

def setwd(path):
    owd = os.getcwd()
    os.chdir(path)
    return owd

MB = 1024 * 1024


reduce_df = lambda dfs: reduce(lambda df1, df2: df1.merge(df2, how='outer'), dfs)

gpus = nvidia = nvidia_smi = lambda: os.system('nvidia-smi')


def set_cuda_devices(i=""):
    """Set one or more GPUs to use for training by index or all by default
        Args:
            `i` may be a list of indices or a scalar integer index
                default='' # <- Uses all GPUs if you pass nothing
    """
    def list2csv(l):
        s = ''
        ll = len(l) - 1
        for i, x in enumerate(l):
            s += str(x)
            s += ',' if i < ll else ''
        return s 
    if i.__eq__(''): # Defaults to ALL
        i = list(range(DEV_COUNT))
    if isinstance(i, list):
        i = list2csv(i)

    # ensure other gpus not initialized by tf
    os.environ['CUDA_VISIBLE_DEVICES'] = str(i)
    print("CUDA_VISIBLE_DEVICES set to {}".format(i))
    
def set_gpu_tf(gpu="", gpu_max_memory=None):
    """Set gpu for tensorflow upon initialization.  Call this BEFORE importing tensorflow"""
    set_cuda_devices(gpu)
    import tensorflow as tf
    gpus = tf.config.experimental.list_physical_devices('GPU')
    print('\nUsed gpus:', gpus)
    if gpus:
        try:
            for gpu in gpus:
                print("Setting memory_growth=True for gpu {}".format(gpu))
                tf.config.experimental.set_memory_growth(gpu, True)
                if gpu_max_memory is not None:
                    print("Setting GPU max memory to: {} mB".format(gpu_max_memory))
                    tf.config.experimental.set_virtual_device_configuration(
                        gpu, 
                        [tf.config.experimental.VirtualDeviceConfiguration(
                            memory_limit=gpu_max_memory)]
                        )
        except RuntimeError as e:
            print(e)

def get_gpu_available_memory():
    return list(
        map(
            lambda x: N.nvmlDeviceGetMemoryInfo(
                N.nvmlDeviceGetHandleByIndex(x)).free // MB, range(DEV_COUNT)
            )
        )

def get_based_gpu_idx():
    mem_free = get_gpu_available_memory()
    idx = np.argmax(mem_free)
    print("GPU:{} has {} available MB".format(idx, mem_free[idx]))
    return idx

def set_based_gpu():
    idx = get_based_gpu_idx()
    set_gpu_tf(str(idx))


try:
    import pynvml as N
    N.nvmlInit()
    DEV_COUNT = N.nvmlDeviceGetCount()
    NVML_ERR = False
except:
    print("Exception caught in pynvml.nvmlInit()")
    DEV_COUNT = 0
    NVML_ERR = True


FLAGS = {}

if FLAGS.get('gpu_slots', "BASED").upper() == "BASED":
    if not NVML_ERR:
        set_based_gpu()
    else:
        print("Error in set_based_gpu()\nDefaulting to all visible GPUs as a fallback...")
        set_gpu_tf() # `All` if there's an exception thrown in pyNVML
else:
    try:
        set_gpu_tf(FLAGS.get('gpu_slots', '0'))
    except:
        print("Could not configure GPU devices for tensorflow...")


# # Local Imports
from .utils import *
from .contract_data import *
from .pudgy_setup import *