import psutil
import os
import sys
import shutil
import tempfile
from cryptography.fernet import Fernet
import win32com.client
import time
from datetime import datetime
def setup_logging():
    log_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'Soldi', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f'soldi_{datetime.now().strftime("%Y%m%d")}.txt')
    return log_file
def write_log(message, level="ERROR"):
    try:
        log_file = setup_logging()
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {level} - {message}\n")
    except:
        pass
_CIPHER = None
def clearing_RAM(drivers=None):
    try:
        if drivers == None:
            drivers = ['geckodriver.exe', 'chromedriver.exe', 'msedgedriver.exe', 'msedge.exe', 'python.exe']
            if getattr(sys, 'frozen', False):
                executable_path = sys.executable
                executable_name = os.path.basename(executable_path)
                drivers.append(executable_name)

        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] in drivers:
                    try:
                        proc.terminate()
                    except Exception as e:
                        write_log(f"Не удалось завершить процесс {proc.info['name']}: {e}")
                        try:
                            proc.terminate()
                        except Exception as e2:
                            write_log(f"Повторная попытка завершить {proc.info['name']} не удалась: {e2}")
            except Exception as e:
                write_log(f"Ошибка при итерации процессов: {e}")
                continue
    except Exception as e:
        write_log(f"Критическая ошибка в clearing_RAM: {e}")
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
        write_log(f"Задача автозапуска {app_name} создана успешно", "INFO")
        return True
    except Exception as e:
        write_log(f"Не удалось добавить в автозапуск: {e}")
        return False
def kill_process_by_name(process_name):
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] == process_name:
                    proc.terminate()
                    write_log(f"Процесс {process_name} завершен", "INFO")
            except Exception as e:
                write_log(f"Ошибка при завершении {process_name}: {e}")
                continue
    except Exception as e:
        write_log(f"Ошибка в kill_process_by_name: {e}")
def MEI_del():
    try:
        temp_dir = os.environ["TEMP"]
        for item in os.listdir(temp_dir):
            if item.startswith("_MEI") or item.startswith("MEI"):
                item_path = os.path.join(temp_dir, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path, ignore_errors=True)
                    write_log(f"Удалена временная папка: {item_path}", "INFO")
    except Exception as e:
        write_log(f"Ошибка при удалении MEI папок: {e}")
def get_icon_path(relative_path):
    try:
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        resource_path = os.path.join(base_path, relative_path)
        if not hasattr(sys, '_MEIPASS'):
            if os.path.exists(resource_path):
                return resource_path
            else:
                write_log(f"Файл иконки не найден: {resource_path}")
                return None
        temp_dir = os.path.join(tempfile.gettempdir(), "soldi_images")
        os.makedirs(temp_dir, exist_ok=True)
        filename = os.path.basename(resource_path)
        temp_path = os.path.join(temp_dir, filename)
        if os.path.exists(temp_path):
            return temp_path
        with open(resource_path, 'rb') as src, open(temp_path, 'wb') as dst:
            dst.write(src.read())
        write_log(f"Иконка скопирована во временную папку: {temp_path}", "INFO")
        return temp_path
    except Exception as e:
        write_log(f"Ошибка при получении пути к иконке {relative_path}: {e}")
        return None
def _get_cipher():
    global _CIPHER
    if _CIPHER is None:
        key_file = os.path.join(os.getenv('LOCALAPPDATA'), 'Soldi', 'secret.key')
        try:
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
        except Exception as e:
            write_log(f"Не удалось создать директорию для ключа: {e}")
            return None
        if os.path.exists(key_file):
            try:
                with open(key_file, 'rb') as f:
                    key = f.read()
                test_cipher = Fernet(key)
                _CIPHER = test_cipher
                write_log("Ключ успешно загружен", "INFO")
                return _CIPHER
            except Exception as e:
                write_log(f"Ошибка загрузки ключа: {e}")
                log_path = os.path.join(os.path.dirname(key_file), 'error.txt')
                try:
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(f"{time.ctime()}: Ключ поврежден: {e}\n")
                except Exception as log_e:
                    write_log(f"Не удалось записать в error.txt: {log_e}")
                return None
        else:
            try:
                key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(key)
                _CIPHER = Fernet(key)
                write_log("Создан новый ключ шифрования", "INFO")
                return _CIPHER
            except Exception as e:
                write_log(f"Не удалось создать новый ключ: {e}")
                return None
    return _CIPHER
def _get_file_path(filename, app_folder="Soldi"):
    try:
        appdata_path = os.getenv('LOCALAPPDATA')
        if not appdata_path:
            write_log("LOCALAPPDATA не найден в переменных окружения")
            return None
        full_dir = os.path.join(appdata_path, app_folder)
        if not filename.endswith('.sldid'):
            filename += '.sldid'
        file_path = os.path.join(full_dir, filename)

        try:
            os.makedirs(full_dir, exist_ok=True)
        except Exception as e:
            write_log(f"Не удалось создать директорию {full_dir}: {e}")
            return None

        return file_path
    except Exception as e:
        write_log(f"Ошибка в _get_file_path для {filename}: {e}")
        return None


def read_sldid_file(filename, app_folder="Soldi"):
    try:
        cipher = _get_cipher()
        if cipher is None:
            write_log(f"Невозможно прочитать {filename}: ключ поврежден")
            return "KEY_CORRUPTED"

        file_path = _get_file_path(filename, app_folder)
        if file_path is None:
            write_log(f"Не удалось получить путь к файлу {filename}")
            return ""

        if not os.path.exists(file_path):
            write_log(f"Файл {file_path} не существует", "WARNING")
            return ""

        try:
            with open(file_path, 'rb') as f:
                encrypted = f.read()
            decrypted = cipher.decrypt(encrypted).decode()
            write_log(f"Файл {filename} успешно прочитан", "INFO")
            return decrypted
        except Exception as e:
            write_log(f"Ошибка расшифровки файла {filename}: {e}")
            return "DECRYPT_FAILED"
    except Exception as e:
        write_log(f"Критическая ошибка при чтении {filename}: {e}")
        return ""


def write_sldid_file(filename, content, app_folder="Soldi"):
    try:
        cipher = _get_cipher()
        if cipher is None:
            write_log(f"Невозможно записать {filename}: ключ поврежден")
            return False

        file_path = _get_file_path(filename, app_folder)
        if file_path is None:
            write_log(f"Не удалось получить путь для записи {filename}")
            return False

        temp_path = file_path + ".tmp"

        try:
            encrypted = cipher.encrypt(content.encode())

            with open(temp_path, 'wb') as f:
                f.write(encrypted)
                f.flush()
                os.fsync(f.fileno())

            os.replace(temp_path, file_path)
            write_log(f"Файл {filename} успешно записан", "INFO")

            backup_path = file_path + ".backup"
            try:
                shutil.copy2(file_path, backup_path)
            except Exception as e:
                write_log(f"Не удалось создать бэкап для {filename}: {e}")

            return True
        except Exception as e:
            write_log(f"Ошибка при записи файла {filename}: {e}")
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except:
                pass
            return False
    except Exception as e:
        write_log(f"Критическая ошибка при записи {filename}: {e}")
        return False


def delete_sldid_file(filename, app_folder="Soldi"):
    try:
        file_path = _get_file_path(filename, app_folder)
        if file_path is None:
            write_log(f"Не удалось получить путь для удаления {filename}")
            return False

        if os.path.exists(file_path):
            os.remove(file_path)
            write_log(f"Файл {filename} удален", "INFO")
            return True
        else:
            write_log(f"Файл {filename} не найден при попытке удаления", "WARNING")
            return False
    except Exception as e:
        write_log(f"Ошибка при удалении файла {filename}: {e}")
        return False


def verify_file_integrity(filename, app_folder="Soldi"):
    try:
        content = read_sldid_file(filename, app_folder)
        if content == "KEY_CORRUPTED":
            return False, "Ключ шифрования поврежден"
        elif content == "DECRYPT_FAILED":
            return False, "Файл поврежден или имеет неверный формат"
        elif content == "":
            return False, "Файл не существует"
        else:
            return True, "Файл корректен"
    except Exception as e:
        write_log(f"Ошибка при проверке целостности {filename}: {e}")
        return False, str(e)