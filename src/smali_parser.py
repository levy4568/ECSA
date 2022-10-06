from atexit import register
import sys
import os
import subprocess
import rules
import shutil

def parse_smali_file(filename):
        """Parse specific smali file
        """
        # print("parse_smali_file : {}".format(filename))
        source = ""
        cls_info = {}
        cls_info['methods'] = []

        send_broadcast_cnt = 0
        register_receiver_cnt = 0

        with open(filename, 'r', encoding='utf8') as f:
            # Read line by line
            for l in f:
                if l.startswith('.class'):
                    cls_name = l.split(' ')[-1].strip()
                    cls_info['cls_name'] = cls_name

                elif l.startswith('.super'):
                    super_cls = l.split(' ')[-1].strip()
                    cls_info['super_cls'] = super_cls

                elif l.startswith('.source'):
                    source = l.split(' ')[-1].strip()
                    cls_info['src'] = source

                elif l.startswith('.method'):
                    # Todos: name, line number, is_danger, method content
                    method_info = {}
                    method_info["name"] = l.split(' ', 1)[-1].strip()
                    code = []
                    is_danger = False
                    l = f.readline()
                    code.append(l)

                    while not l.startswith('.end method'):
                        if rules.is_danger_send_broadcast(l):
                            send_broadcast_cnt += 1
                            is_danger = True
                        elif rules.is_danger_register_receiver(l):
                            register_receiver_cnt += 1
                            is_danger = True
                        l = f.readline()
                        code.append(l)
                    method_info["code"] = code
                    method_info["is_danger"] = is_danger
                
                    if is_danger:                      
                        # print(method_info)
                        cls_info['methods'].append(method_info)
        # Close fd
        f.close()
        cls_info['send_broadcast_cnt'] = send_broadcast_cnt
        cls_info['register_receiver_cnt'] = register_receiver_cnt
        return cls_info


def scan_all_smali(app_dir):
    danger_cls_list = []

    for dirname, _, files in os.walk(app_dir):
        for app_file in files:
            file_path = os.path.join(dirname, app_file)
            if app_file.endswith(".smali"):
                app_path = os.path.join(dirname, app_file)
                cls_info = parse_smali_file(app_path)
                if len(cls_info['methods']) > 0:
                    danger_cls_list.append(cls_info)
                # print(" danger_cls_list cnt:{} ".format(len(danger_cls_list)))
                # if len(danger_cls_list) > 5:
                #     break
            os.remove(file_path)
    # print(danger_cls_list)
    print("parse smali finish")
    return danger_cls_list
