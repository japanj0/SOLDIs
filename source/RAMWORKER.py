import psutil
import os
import sys
import shutil
import tempfile
from cryptography.fernet import Fernet
import win32com.client

_CIPHER = None


def clearing_RAM(drivers=None):
    if drivers == None:
        drivers = ['geckodriver.exe', 'chromedriver.exe', 'msedgedriver.exe', 'msedge.exe', 'python.exe']
        if getattr(sys, 'frozen', False):
            executable_path = sys.executable
            executable_name = os.path.basename(executable_path)
            drivers.append(executable_name)

    for proc in psutil.process_iter(['name']):
        if proc.info['name'] in drivers:
            try:
                proc.terminate()
            except Exception:
                try:
                    proc.terminate()
                except Exception:
                    pass


def add_to_autostart(app_name: str) -> bool:
    try:
        if getattr(sys, 'frozen', False):
            app_path = sys.executable
        else:
            app_path = os.path.abspath(__file__)

        scheduler = win32com.client.Dispatch("Schedule.Service")
        scheduler.Connect()
        root_folder = scheduler.GetFolder("\\")

        task_def = scheduler.NewTask(0)

        reg_info = task_def.RegistrationInfo
        reg_info.Description = f"Auto start {app_name}"

        triggers = task_def.Triggers
        trigger = triggers.Create(9)
        trigger.Enabled = True

        action = task_def.Actions.Create(0)
        action.Path = app_path
        action.Arguments = "--scheduled"

        settings = task_def.Settings
        settings.Enabled = True
        settings.StartWhenAvailable = True
        settings.Hidden = False

        principal = task_def.Principal
        principal.RunLevel = 1

        root_folder.RegisterTaskDefinition(
            app_name,
            task_def,
            6,
            "",
            "",
            3
        )
        return True
    except Exception:
        return False


def kill_process_by_name(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            proc.terminate()


def MEI_del():
    temp_dir = os.environ["TEMP"]
    for item in os.listdir(temp_dir):
        if item.startswith("_MEI") or item.startswith("MEI"):
            item_path = os.path.join(temp_dir, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path, ignore_errors=True)


def get_icon_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    resource_path = os.path.join(base_path, relative_path)
    if not hasattr(sys, '_MEIPASS'):
        return resource_path
    temp_dir = os.path.join(tempfile.gettempdir(), "soldi_images")
    os.makedirs(temp_dir, exist_ok=True)
    filename = os.path.basename(resource_path)
    temp_path = os.path.join(temp_dir, filename)
    if os.path.exists(temp_path):
        return temp_path
    try:
        with open(resource_path, 'rb') as src, open(temp_path, 'wb') as dst:
            dst.write(src.read())
        return temp_path
    except Exception as e:
        print(f"Ошибка при извлечении изображения: {e}")
        return None


def _get_cipher():
    global _CIPHER
    if _CIPHER is None:
        key_file = os.path.join(os.getenv('LOCALAPPDATA'), 'Soldi', 'secret.key')
        os.makedirs(os.path.dirname(key_file), exist_ok=True)

        if os.path.exists(key_file):
            try:
                with open(key_file, 'rb') as f:
                    key = f.read()
                _CIPHER = Fernet(key)
            except:
                key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(key)
                _CIPHER = Fernet(key)
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            _CIPHER = Fernet(key)
    return _CIPHER


def _get_file_path(filename, app_folder="Soldi"):
    appdata_path = os.getenv('LOCALAPPDATA')
    full_dir = os.path.join(appdata_path, app_folder)
    if not filename.endswith('.sldid'):
        filename += '.sldid'
    file_path = os.path.join(full_dir, filename)
    os.makedirs(full_dir, exist_ok=True)
    return file_path


def read_sldid_file(filename, app_folder="Soldi"):
    cipher = _get_cipher()
    file_path = _get_file_path(filename, app_folder)

    if not os.path.exists(file_path):
        return ""

    try:
        with open(file_path, 'rb') as f:
            encrypted = f.read()
        return cipher.decrypt(encrypted).decode()
    except Exception:
        return ""


def write_sldid_file(filename, content, app_folder="Soldi"):
    cipher = _get_cipher()
    file_path = _get_file_path(filename, app_folder)

    encrypted = cipher.encrypt(content.encode())
    with open(file_path, 'wb') as f:
        f.write(encrypted)
    return True


def delete_sldid_file(filename, app_folder="Soldi"):
    file_path = _get_file_path(filename, app_folder)
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False
