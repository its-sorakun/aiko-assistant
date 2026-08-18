import os
import psutil

# Aiko's hands and eyes in the OS.
# We're hooking directly into Windows to do things the native way.

def launch_program(app_name: str) -> str:
    """
    Launch a program by its executable name or command. 
    This tries to use the Windows shell to fire it up.
    """
    try:
        # Using the start command to let Windows figure out the path if it's in the environment
        os.system(f'start "" "{app_name}"')
        return f"Successfully asked Windows to launch {app_name}."
    except Exception as e:
        return f"Hmm, I had some trouble launching {app_name}. Error: {e}"

def get_system_stats() -> str:
    """
    Check the PC's vitals: CPU and RAM usage.
    """
    # Checking CPU load over a quick 0.1-second interval to avoid hanging
    cpu_usage = psutil.cpu_percent(interval=0.1)
    
    # Grab memory info and convert bytes to gigabytes for readability
    ram = psutil.virtual_memory()
    total_ram_gb = round(ram.total / (1024 ** 3), 1)
    used_ram_gb = round(ram.used / (1024 ** 3), 1)
    
    return f"CPU is currently at {cpu_usage}%. RAM usage is {used_ram_gb}GB out of {total_ram_gb}GB ({ram.percent}%)."

def open_directory(folder_path: str) -> str:
    """
    Open a specific folder using the native Windows Explorer.
    """
    # Quick sanity check to make sure the folder actually exists
    if os.path.exists(folder_path):
        os.startfile(folder_path)
        return f"Opened folder: {folder_path}"
    else:
        return f"Senpai, that folder doesn't seem to exist: {folder_path}"
