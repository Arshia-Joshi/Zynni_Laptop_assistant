import os
import psutil
import platform

def get_battery():
    battery = psutil.sensors_battery()
    return f"Battery: {battery.percent}%"

def get_system_info():
    return f"""
System: {platform.system()}
Processor: {platform.processor()}
"""


def open_path(path):
    try:
        os.startfile(path)

        return True, ""
    except Exception as e:
        return False, str(e)