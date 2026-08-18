import os
import psutil
import ctypes
import subprocess
import winreg
import shutil

# hooking directly into Windows to do things the native way.

def launch_program(app_name: str) -> str:
    """
    Attempt to launch a program natively without relying on the shell 'start' command,
    which triggers ugly GUI error dialogs if the binary is missing.
    Resolves execution via PATH, Uninstall registries, and App Paths directly.
    """
    # 1. Native PATH resolution
    executable = shutil.which(app_name)
    if executable:
        try:
            subprocess.Popen([executable], creationflags=0x00000008, close_fds=True)
            return f"Launched {app_name} natively from PATH: {executable}"
        except Exception as e:
            return f"Failed to execute {executable}: {e}"

    # 2. Deep Registry Crawl for physical executable
    search_hives = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
    ]
    
    found_path = None
    for hive, key_path in search_hives:
        if found_path: break
        try:
            with winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as parent_key:
                num_subkeys = winreg.QueryInfoKey(parent_key)[0]
                for i in range(num_subkeys):
                    try:
                        subkey_name = winreg.EnumKey(parent_key, i)
                        with winreg.OpenKey(parent_key, subkey_name, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as subkey:
                            display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                            if app_name.lower() in display_name.lower():
                                # Match found! Extract the executable path from DisplayIcon
                                try:
                                    icon_path, _ = winreg.QueryValueEx(subkey, "DisplayIcon")
                                    found_path = icon_path.split(',')[0].strip('"')
                                    break
                                except FileNotFoundError:
                                    pass
                    except OSError:
                        continue
        except OSError:
            continue
            
    if found_path and os.path.exists(found_path):
        try:
            # Launch detached GUI process cleanly
            subprocess.Popen([found_path], creationflags=0x00000008, close_fds=True)
            return f"Located and launched {app_name} via Registry: {found_path}"
        except Exception as e:
            return f"Found {app_name} at {found_path} but kernel execution failed: {e}"
            
    # 3. Direct App Paths Registry fallback (mimics 'start' behavior without the error dialog)
    app_exe = app_name if app_name.lower().endswith(".exe") else f"{app_name}.exe"
    for hive in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
        try:
            with winreg.OpenKey(hive, rf"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{app_exe}", 0, winreg.KEY_READ) as key:
                app_path, _ = winreg.QueryValueEx(key, "")
                if os.path.exists(app_path):
                    subprocess.Popen([app_path], creationflags=0x00000008, close_fds=True)
                    return f"Launched via App Paths: {app_path}"
        except OSError:
            continue
            
    return f"Failed to locate {app_name} in PATH, Uninstall Registries, or App Paths."

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

def open_directory(folder_path: str) -> str:
    """
    Open a specific folder using the native Windows Explorer.
    """
    # Quick sanity check to make sure the folder actually exists
    if os.path.exists(folder_path):
        os.startfile(folder_path)
        return f"Opened folder: {folder_path}"
    else:
        return f"Target directory does not exist: {folder_path}"

def get_active_window() -> str:
    """
    Traverse the Desktop Window Manager Z-order stack to find the active application window.
    Bypasses the command prompt window itself if executed from a terminal.
    """
    user32 = ctypes.windll.user32
    
    # 2 corresponds to GW_HWNDNEXT (the window below the specified window)
    GW_HWNDNEXT = 2 
    
    # Fetch the window currently holding focus (likely the terminal running this script)
    hwnd = user32.GetForegroundWindow()
    
    # Determine the process ID of the current foreground window
    pid = ctypes.c_ulong()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    
    current_pid = os.getpid()
    
    # Fallback in case the terminal wrapper has a different PID (like Windows Terminal)
    # Check if window is visible and has a title to find a legitimate background app
    if pid.value == current_pid or "cmd.exe" in psutil.Process(pid.value).name().lower() or "windowsterminal.exe" in psutil.Process(pid.value).name().lower():
        # Crawl down the DWM Z-order stack
        while hwnd:
            hwnd = user32.GetWindow(hwnd, GW_HWNDNEXT)
            if user32.IsWindowVisible(hwnd):
                
                # If we hit the bare desktop shell, they are looking at the desktop!
                cls_buf = ctypes.create_unicode_buffer(256)
                user32.GetClassNameW(hwnd, cls_buf, 256)
                if cls_buf.value in ("WorkerW", "Progman"):
                    return "The Windows Desktop (No active applications)"
                
                # Otherwise, look for a non-minimized window with a title
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0 and not user32.IsIconic(hwnd):
                    break

    if not hwnd:
        return "Could not determine the active background window."

    # Extract the title of the target window
    length = user32.GetWindowTextLengthW(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buff, length + 1)
    
    return f"The underlying active window is: {buff.value}"

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

def query_registry_value(hive: str, key_path: str, value_name: str) -> str:
    """
    Read a specific value directly from the Windows Registry.
    Example hive parameters: HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE
    """
    hives = {
        "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
        "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
        "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
        "HKEY_USERS": winreg.HKEY_USERS
    }
    
    target_hive = hives.get(hive.upper())
    if not target_hive:
        return f"Invalid registry hive: {hive}"
        
    try:
        # Access the registry key strictly in read-only mode (KEY_READ)
        with winreg.OpenKey(target_hive, key_path, 0, winreg.KEY_READ) as key:
            value, reg_type = winreg.QueryValueEx(key, value_name)
            return f"Registry query successful. Value: {value}"
    except FileNotFoundError:
        return f"Registry path or value not found: {key_path}\\\\{value_name}"
    except PermissionError:
        return "Insufficient permissions to read that registry key."
    except Exception as e:
        return f"Registry query failed: {e}"

def force_kill_process(process_name: str) -> str:
    """
    Drop a kernel-level termination signal to forcefully wipe a process from memory.
    Useful for hung or unresponsive applications.
    """
    try:
        # /F denotes force, /IM specifies image name
        subprocess.run(["taskkill", "/F", "/IM", process_name], capture_output=True, text=True, check=True)
        return f"Termination signal sent. {process_name} has been forcefully killed."
    except subprocess.CalledProcessError as e:
        return f"Failed to kill {process_name}. Process may not be running or execution requires elevated privileges."
