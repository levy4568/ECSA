import ast
import hashlib
import io
import logging
import ntpath
import os
import platform
import re
import sys
import shutil
import signal
import string
import subprocess
import stat
import csv
import sqlite3
import unicodedata
import threading
import requests
import settings
import threading

def get_file_md5(file_name):
    hash_md5 = hashlib.md5()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def is_file_exists(file_path):
    if os.path.isfile(file_path):
        return True
    # This fix situation where a user just typed "adb" or another executable
    # inside settings.py/config.py
    if shutil.which(file_path):
        return True
    else:
        return False


def is_dir_exists(dir_path):
    if os.path.isdir(dir_path):
        return True
    else:
        return False

def file_size(app_path):
    """Return the size of the file."""
    return round(float(os.path.getsize(app_path)) / (1024 * 1024), 2)

def find_java_binary():
    """Find Java."""
    # Respect user settings
    if platform.system() == 'Windows':
        jbin = 'java.exe'
    else:
        jbin = 'java'

    if os.getenv('JAVA_HOME'):
        java = os.path.join(
            os.getenv('JAVA_HOME'),
            'bin',
            jbin)
        if is_file_exists(java):
            return java
    return 'java'

def ensure_dir_exist(dir_path):
    if not is_dir_exists(dir_path):
        os.makedirs(dir_path)

def delete_tmp_dir(dir_path):
    if not is_dir_exists(dir_path):
        return

    if settings.TMP_DIR in dir_path:
        print("delete dir: {}".format(dir_path))
        try:
            shutil.rmtree(dir_path, ignore_errors=False)
            print("\n")
        except Exception as e:
            delete_tmp_dir(dir_path)


def dump_smali_data_to_csv(app_data, file_path):
    out_dir = os.path.dirname(file_path)
    if not is_dir_exists(out_dir):
        os.makedirs(out_dir)
    is_first_write = True
    if os.access(file_path, os.W_OK):
        is_first_write = False

    with open(file_path, 'a+', encoding="utf-8-sig", newline="") as f:
        csv_writer = csv.writer(f)
        if is_first_write:
            csv_writer.writerow(['MD5', 'filename', 'packageName', 'verNum', 'classLocation', 'riskF', 'broadcastcnt', 'receivercnt'])

        app_info = app_data["app_info"]
        apk_md5 = app_data["apk_md5"]
        file_name = app_data["file_name"]
        package_name = app_info["packagename"]
        versionCode = app_info["versionCode"]
        danger_cls_list = app_data["danger_cls_list"]
        for cls in danger_cls_list:
            csv_writer.writerow([apk_md5, file_name, package_name, versionCode, cls["cls_name"], cls["methods"], cls["send_broadcast_cnt"], cls["register_receiver_cnt"]])
        f.close()

def dump_manifest_data_to_csv(app_data, file_path):
    out_dir = os.path.dirname(file_path)
    ensure_dir_exist(out_dir)
    is_first_write = True
    if os.access(file_path, os.W_OK):
        is_first_write = False
    with open(file_path, 'a+', encoding="utf-8-sig", newline="") as f:
        csv_writer = csv.writer(f)
        if is_first_write:
            csv_writer.writerow(['MD5', 'filename', 'packageName', 'verNum', 'ActivityRisk', 'ActivityCnt', 'ServiceRisk', 'ServiceCnt', 'ReceiverRisk', 'ReceiverCnt', 'ProviderRisk', 'ProviderCnt'])

        app_info = app_data["app_info"]
        apk_md5 = app_data["apk_md5"]
        file_name = app_data["file_name"]
        package_name = app_info["packagename"]
        versionCode = app_info["versionCode"]
        activity_risk = app_info["activities"]
        activity_risk_cnt = len(app_info["activities"])
        service_risk = app_info["services"]
        service_risk_cnt = len(app_info["services"])
        receiver_risk = app_info["receivers"]
        receiver_risk_cnt = len(app_info["receivers"])
        provider_risk = app_info["providers"]
        provider_risk_cnt = len(app_info["providers"])
        csv_writer.writerow([apk_md5, file_name, package_name, versionCode, activity_risk, activity_risk_cnt, service_risk, service_risk_cnt, receiver_risk, receiver_risk_cnt, provider_risk, provider_risk_cnt])
        f.close()


def delete_tmp_dir_in_thread(dir_path):
    threading.Thread(target=delete_tmp_dir, args=(dir_path,)).start()

