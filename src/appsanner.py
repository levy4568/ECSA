# -*- coding: utf-8 -*-

import os
import re
import io
import json
import subprocess
import sys
import threading
import codecs
import time
import argparse
import traceback
import apk_util
import settings
import smali_parser
import utils
import settings

def scan_all_app_in_dir(app_dir, output_dir, scan_func):
    # print("scan all app in {}".format(app_dir))
    if not os.path.exists(app_dir):
        print("app dir not exist : {}".format(app_dir))
        return
    for dirname, _, files in os.walk(app_dir):
        for app_file in files:
            if not app_file.endswith(".apk"):
                continue
            app_path = os.path.join(dirname, app_file)
            scan_func(app_path, output_dir)

def scan_an_app(app_path, output_dir="data"):
    print("scan app : {}".format(app_path))
    try:
        apk_name = os.path.basename(app_path)
        file_name = os.path.splitext(apk_name)[0]
        
        decompile_dir = os.path.join(os.getcwd(), settings.TMP_DIR, file_name)
        utils.ensure_dir_exist(decompile_dir)
        apk_md5 = apk_util.get_app_md5(app_path)
        
        apk_util.unpack(app_path, decompile_dir)

        app_info = apk_util.get_app_info(decompile_dir)

        # print("app info :{}".format(app_info))

        danger_cls_list = smali_parser.scan_all_smali(decompile_dir)
        app_data = {
            "apk_md5": apk_md5,
            "file_name": file_name,
            "app_info": app_info,
            "danger_cls_list": danger_cls_list
        }

        # Asynchronously delete directories and temporary files in tmp
        utils.delete_tmp_dir_in_thread(decompile_dir)

        smali_output_file = os.path.join(output_dir, "app_risk_in_smali.csv")
        utils.dump_smali_data_to_csv(app_data, smali_output_file)
        manifest_output_file = os.path.join(output_dir, "app_risk_in_manifest.csv")
        utils.dump_manifest_data_to_csv(app_data, manifest_output_file)
    except Exception as e:
        msg = traceback.format_exc()
        print("scan app failed : {}".format(msg))

def scan_all_app_in_file(input_file, app_dir, output_dir, scan_func):
    if not os.path.exists(input_file):
        print("input file not exist : {}".format(input_file))
        return

    with open(input_file, "r") as f:
        for file_name in f:
            app_path = os.path.join(app_dir, file_name.strip())
            if not os.path.exists(app_path):
                print("app not exist : {}".format(app_path))
                continue
            # print("scan app : {}".format(app_path))
            scan_func(app_path, output_dir)
    

def start(input_file, app_dir, output="data"):
    print("input_file:{}".format(input_file))
    if input_file and input_file != "":
        scan_all_app_in_file(input_file, app_dir, output, scan_an_app)
    else:
        scan_all_app_in_dir(app_dir, output, scan_an_app)


def main():
    # how to use PRSA
    parser = argparse.ArgumentParser(description="Android app potential risk scan tools",
                    usage="\n\npython appsanner.py -d apk_dir [-i input_apk_name_file(can be null)] [-o out_path]")
    parser.add_argument('-i','--input', help='input apk name file,it can be null', required=False)
    parser.add_argument('-d','--dir', help='<Required> apk directory', required=True)
    parser.add_argument('-o','--output',help='<Required> output file',required=False)
    args = parser.parse_args()
    start(args.input, args.dir, args.output)

if __name__ == "__main__":
    main()