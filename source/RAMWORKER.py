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
        key = reg.OpenKey(
            reg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, reg.KEY_SET_VALUE
        )
        reg.SetValueEx(key, app_name, 0, reg.REG_SZ, app_path)
        key.Close()
        return True
    except Exception as e:
        print(f"Ошибка добавления в автозагрузку: {e}")
        return False


def remove_from_autostart(app_name: str) -> bool:
    try:
        key = reg.OpenKey(
            reg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, reg.KEY_SET_VALUE
        )
        reg.DeleteValue(key, app_name)
        key.Close()
        return True
    except FileNotFoundError:
        return True
    except Exception as e:
        print(f"Ошибка удаления из автозагрузки: {e}")
        return False
