# Grabbing CPU/RAM via psutil is straightforward, but thermal data is restricted in Windows user-space. Attempting to probe ACPI thermal zones natively via WMI here. Be aware that without a Ring-0 kernel driver, most modern desktop motherboards will silently block this read.
import psutil
import subprocess

def get_system_stats() -> str:
    """
    Check the PC's vitals: CPU and RAM usage.
    Also attempts to probe ACPI thermal zones for temperature, exposing Windows user-space limitations.
    """
    cpu_usage = psutil.cpu_percent(interval=0.1)
    
    ram = psutil.virtual_memory()
    total_ram_gb = round(ram.total / (1024 ** 3), 1)
    used_ram_gb = round(ram.used / (1024 ** 3), 1)
    
    # Attempt to read CPU temp natively via WMI ACPI Thermal Zones
    temp_info = "Temperature read failed."
    try:
        # Most desktop motherboards do not expose thermal diodes to user-space WMI without a Ring-0 driver
        cmd = ["powershell", "-NoProfile", "-Command", "Get-CimInstance -Namespace root/wmi -ClassName MSApi_ThermalZoneTemperature -ErrorAction Stop | Select-Object CurrentTemperature"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        if result.stdout.strip():
            # WMI returns deci-Kelvin
            dk = int(result.stdout.strip().split()[-1])
            celsius = (dk / 10.0) - 273.15
            temp_info = f"{celsius:.1f}C (via WMI ACPI)"
    except Exception:
        temp_info = "Cannot read native thermal diodes. Windows user-space lacks access without a Ring-0 (kernel-level) driver hooking the Super I/O chip."
    
    return f"CPU: {cpu_usage}%. RAM: {used_ram_gb}GB / {total_ram_gb}GB ({ram.percent}%). Thermal: {temp_info}"

def get_hardware_details() -> str:
    """
    Retrieve underlying hardware specifications bypassing high-level wrappers.
    Queries the Common Information Model (CIM) for read-only hardware data.
    """
    try:
        # Request read-only hardware specifications directly from the OS
        cmd = ["powershell", "-NoProfile", "-Command", "Get-CimInstance Win32_BaseBoard | Select-Object Manufacturer, Product | ConvertTo-Json -Compress"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return f"Hardware CIM Data: {result.stdout.strip()}"
    except subprocess.CalledProcessError as e:
        return f"Failed to retrieve hardware details: {e.stderr}"
