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