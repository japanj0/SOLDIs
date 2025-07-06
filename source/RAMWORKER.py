import subprocess
import psutil
import os
import sys
import shutil
import tempfile
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


def add_to_autostart(app_name: str) -> str:
    try:
        if getattr(sys, 'frozen', False):
            app_path = sys.executable
        else:
            app_path = os.path.abspath(__file__)

        result = subprocess.run(
            [
                "schtasks", "/create", "/tn", app_name,
                "/sc", "onlogon", "/rl", "highest",
                "/tr", app_path, "/f"
            ],
            capture_output=True,
            encoding='utf-8',
            errors='replace',
            shell=True
        )

        return f"{result.returncode == 0, result.stderr, result.stdout}"

    except Exception:
        return "False"
def remove_from_autostart(app_name: str) -> bool:
    try:
        result = subprocess.run(
            ["schtasks", "/delete", "/tn", app_name, "/f"],
            capture_output=True,
            encoding='utf-8',
            errors='replace',
            shell=True
        )
        return result.returncode == 0

    except Exception:
        return False
def kill_process_by_name(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            proc.kill()
def MEI_del():
    temp_dir = os.environ["TEMP"]
    for item in os.listdir(temp_dir):
        if item.startswith("MEI"):
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