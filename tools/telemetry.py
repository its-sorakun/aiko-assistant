# Grabbing CPU/RAM via psutil is straightforward, but thermal data is restricted in Windows user-space. Attempting to probe ACPI thermal zones natively via WMI here. Be aware that without a Ring-0 kernel driver, most modern desktop motherboards will silently block this read.
import psutil
import subprocess

def get_system_stats() -> str:
    """
    Check the PC's vitals: CPU, RAM, and GPU usage/temps.
    """
    cpu_usage = psutil.cpu_percent(interval=0.1)
    
    ram = psutil.virtual_memory()
    total_ram_gb = round(ram.total / (1024 ** 3), 1)
    used_ram_gb = round(ram.used / (1024 ** 3), 1)
    
    # Attempt to read CPU temp natively via WMI ACPI Thermal Zones (often blocked in user-space)
    cpu_temp = "N/A (Kernel blocked)"
    try:
        cmd = ["powershell", "-NoProfile", "-Command", "Get-CimInstance -Namespace root/wmi -ClassName MSApi_ThermalZoneTemperature -ErrorAction Stop | Select-Object CurrentTemperature"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        if result.stdout.strip():
            dk = int(result.stdout.strip().split()[-1])
            celsius = (dk / 10.0) - 273.15
            cpu_temp = f"{celsius:.1f}C"
    except Exception:
        pass

    # Extract GPU Temp natively via nvidia-smi (if NVIDIA driver is present)
    gpu_temp = "N/A"
    try:
        cmd = ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, creationflags=0x08000000)
        if result.stdout.strip():
            gpu_temp = f"{result.stdout.strip()}C"
    except Exception:
        pass
    
    return f"CPU Usage: {cpu_usage}% (Temp: {cpu_temp}). RAM: {used_ram_gb}GB / {total_ram_gb}GB ({ram.percent}%). GPU Temp: {gpu_temp}"

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
