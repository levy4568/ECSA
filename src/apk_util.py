from asyncio.windows_events import NULL
import os
import re
import io
import json
import subprocess
import sys
import threading
import codecs
import time
import settings
import utils
from xml.dom import minidom
import rules
# from androguard.core.bytecodes.apk import APK

def unpack(apk_file, out_dir):
    """unpack an apk file and decode src"""
    apktool_path = settings.get_apktool_binary()
    args = [
        utils.find_java_binary(),
        '-jar',
        apktool_path,
        '-f', 'd',
        '-o',
        out_dir,
        apk_file
    ]
    try:
        subprocess.check_call(args)
    except:
        return False
    return True

def get_app_md5(apk_file):
    if not utils.is_file_exists(apk_file):
        return ""
    app_md5 = utils.get_file_md5(apk_file)
    return app_md5

def get_manifest_data(app_decode_dir):
    """read and decode manifest file"""
    manifest_path = os.path.join(app_decode_dir, 'AndroidManifest.xml')
    manifest = NULL
    if not utils.is_file_exists(manifest_path):
        print("get_manifest_file : manifest_path {} not exist".format(manifest_path))
        return NULL
    try:
        manifest = minidom.parse(manifest_path)
        print("handle manifest file")
    except Exception as e:
        print("parse manifest failed : {}".format(e))
    return manifest

def parse_manifest_data(manifest_data):
    """parse manifest data."""
    svc = []
    act = []
    brd = []
    cnp = []
    # perm = []
    package = ''
    targetsdk = ''
    androidversioncode = ''
    androidversionname = ''
    permissions = manifest_data.getElementsByTagName('uses-permission')
    manifest = manifest_data.getElementsByTagName('manifest')
    activities = manifest_data.getElementsByTagName('activity')
    services = manifest_data.getElementsByTagName('service')
    providers = manifest_data.getElementsByTagName('provider')
    receivers = manifest_data.getElementsByTagName('receiver')

    for node in manifest:
        package = node.getAttribute('package')
        androidversioncode = node.getAttribute('android:versionCode')
        androidversionname = node.getAttribute('android:versionName')

    for activity in activities:
        act_2 = activity.getAttribute('android:name')
        if rules.is_component_danger(activity):
            act.append(act_2)

    for service in services:
        service_name = service.getAttribute('android:name')
        if rules.is_component_danger(service):
            svc.append(service_name)

    for provider in providers:
        provider_name = provider.getAttribute('android:name')
        if rules.is_component_danger(provider):
            cnp.append(provider_name)

    for receiver in receivers:
        rec = receiver.getAttribute('android:name')
        if rules.is_component_danger(receiver):
            brd.append(rec)

    # android_permission_tags = ('com.google.', 'android.', 'com.android.')
    # for permission in permissions:
    #     perm.append(permission.getAttribute('android:name'))
    # prm = []
    # for full_perm in perm:
    #     # For general android permissions
    #     prm = full_perm
    #     pos = full_perm.rfind('.')
    #     if pos != -1:
    #         prm = full_perm[pos + 1:]
    #     if not full_perm.startswith(android_permission_tags):
    #         prm = full_perm

    man_data_dic = {
        'services': svc,
        'activities': act,
        'receivers': brd,
        'providers': cnp,
        # 'perm': prm,
        'packagename': package,
        'target_sdk': targetsdk,
        'androver': androidversioncode,
        'androvername': androidversionname,
    }
    
    return man_data_dic
    

def get_manifest_info(app_decode_dir):
    if not utils.is_dir_exists(app_decode_dir):
        print("get_manifest_info : app_decode_dir {} not exist".format(app_decode_dir))
        return NULL
    manifest_data = get_manifest_data(app_decode_dir)
    manifest_info = parse_manifest_data(manifest_data)
    # print(manifest_info)
    return manifest_info


def get_version_info(app_decode_dir):
    if not utils.is_dir_exists(app_decode_dir):
        print("get_version_info : app_decode_dir {} not exist".format(app_decode_dir))
        return NULL
    app_yml = os.path.join(app_decode_dir, 'apktool.yml')
    versionCode = ''
    versionName = ''
    with open(app_yml, 'r') as f:
        for line in f:
            if "versionName" in line :
                versionName = line.split(":")[1].strip()
            elif "versionCode" in line:
                versionCode = line.split(":")[1].strip().replace("\'", "")
        f.close()
    versionInfo = {
        "versionCode" : versionCode,
        "versionName" : versionName
    }
    return versionInfo

def get_app_info(app_decode_dir):
    manifest_info = get_manifest_info(app_decode_dir)
    verInfo = get_version_info(app_decode_dir)
    # print(manifest_info)
    app_info = {
        "packagename" : manifest_info["packagename"],
        "activities" : manifest_info["activities"],
        "services" : manifest_info["services"],
        "receivers" : manifest_info["receivers"],
        "providers" : manifest_info["providers"],
        "versionCode" : verInfo["versionCode"],
        "versionName" : verInfo["versionName"]
    }
    return app_info
