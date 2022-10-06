from xml.dom import minidom


def is_component_danger(component):
    is_exported = component.getAttribute('android:exported')
    has_permission = component.getAttribute('android:permission')
    # print("is_component_danger ==> is_exported:{}, has_permission:{}".format(is_exported, has_permission))
    if is_exported == 'true' and has_permission == '':
        return True
    else:
        return False

danger_code = [
    'Landroid/content/Context;->sendBroadcast(Landroid/content/Intent;)V',
    ';->registerReceiver(Landroid/content/BroadcastReceiver;Landroid/content/IntentFilter;)Landroid/content/Intent;'
]

def is_code_line_danger(code_line):
    # https://developer.android.com/guide/components/broadcasts
    for c in danger_code:
        if c in code_line:
            return True
    return False

def is_danger_send_broadcast(code_lines):
    if 'Landroid/content/Context;->sendBroadcast(Landroid/content/Intent;)V' in code_lines:
        return True
    else:
        return False

def is_danger_register_receiver(code_lines):
    if ';->registerReceiver(Landroid/content/BroadcastReceiver;Landroid/content/IntentFilter;)Landroid/content/Intent;' in code_lines:
        return True
    else:
        return False