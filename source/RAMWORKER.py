import subprocess
import psutil
import os
import sys
import winreg as reg
def clearing_RAM():
    drivers = ['geckodriver.exe', 'chromedriver.exe', 'msedgedriver.exe','msedge.exe']
    for proc in psutil.process_iter(['name']):
        print(proc)
        if proc.info['name'] in drivers:
            try:
                proc.terminate()
                print(proc.info['name'])
            except Exception as e:
                print(e)
def create_txt_file(filename, default_content="", app_folder="MyApp"):
    appdata_path = os.getenv('LOCALAPPDATA')
    full_dir = os.path.join(appdata_path, app_folder)
    file_path = os.path.join(full_dir, filename)
    os.makedirs(full_dir, exist_ok=True)
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(default_content)
    return file_path

def read_txt_file(filename, app_folder="Soldi"):
    file_path = create_txt_file(filename, "", app_folder)
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def write_txt_file(filename, content, app_folder="Soldi"):
    file_path = create_txt_file(filename, "", app_folder)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return True
def add_to_autostart(app_name: str) -> bool:
    try:
        app_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
        result = subprocess.run([
            "schtasks", "/create", "/tn", app_name,
            "/sc", "onlogon", "/rl", "highest",
            "/tr", f'"{app_path}"', "/f"
        ], capture_output=True, text=True, shell=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Ошибка добавления в планировщик: {e}")
        return False

def remove_from_autostart(app_name: str) -> bool:
    try:
        result = subprocess.run([
            "schtasks", "/delete", "/tn", app_name, "/f"
        ], capture_output=True, text=True, shell=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Ошибка удаления из планировщика: {e}")
        return False
