import logging
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print("base_dir: {}".format(BASE_DIR))
APKTOOL_BINARY = os.path.join('bin', 'apktool_2.6.1.jar')
DUMP_DATA_DIR = './data/'
TMP_DIR = 'tmp'

def get_apktool_binary():
    apktool_bin_path = os.path.join(BASE_DIR, APKTOOL_BINARY)
    return apktool_bin_path