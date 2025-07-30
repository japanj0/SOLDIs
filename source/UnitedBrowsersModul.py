import ctypes
import threading
import time
import os
import uuid
from tkinter import *
from selenium.common.exceptions import WebDriverException
import psutil
import pygetwindow as gw
import process_blocker
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import RAMWORKER
from urllib.parse import *
from tkinter import ttk
import idna
import hashlib
import zipfile
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService


class App:
    def __init__(self, whitelisted_domains, unlock_password, time, browser_type, flag):
        if time != "":
            self.remaining_time = int(time) * 60
        self.flag = flag
        self.whitelisted_domains = whitelisted_domains
        self.unlock_password = unlock_password
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.html_path = os.path.join(self.script_dir, "links.html")
        self.main_window = Tk()
        self.main_window.withdraw()
        self.time = time
        self.browser_type = browser_type
        self.initialize_app_state()
        self.main_window.protocol("WM_DELETE_WINDOW", self.handle_window_close)

    def format_time(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        mins, secs = divmod(remainder, 60)
        return f"{hours:02d}:{mins:02d}:{secs:02d}"

    def update_timer(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            time_str = self.format_time(self.remaining_time)
            self.timer_label.config(fg="black", font=("Arial", 23, "bold"))
            self.timer_label.config(text=f"До принудительного закрытия осталось:\n{time_str}")
            self.main_window.after(1000, self.update_timer)
        else:
            process = {
                "chrome": "chrome.exe",
                "edge": "msedge.exe",
                "firefox": "firefox.exe"
            }[self.browser_type]
            RAMWORKER.kill_process_by_name(process)

    def initialize_app_state(self):
        self.browser_lock_mutex = None
        self.browser_driver = None
        self.is_running = True
        self.setup_browser_environment()

    def setup_browser_environment(self):
        if self.check_browser_process_running():
            return
        self.browser_lock_mutex = self.create_browser_lock_mutex()
        if not self.browser_lock_mutex:
            return
        self.local_page_url = self.generate_allowed_sites_html()
        self.launch_controlled_browser()
        self.main_window = Tk()
        self.main_window.title("soldi")
        self.main_window.iconbitmap(RAMWORKER.get_icon_path("icon.ico"))
        if not self.flag:
            RAMWORKER.write_sldid_file("data", f"{hashlib.sha256(self.unlock_password.encode('utf-8')).hexdigest()}")
        self.main_window.resizable(False, False)
        self.main_window.iconify()
        self.main_window.protocol("WM_DELETE_WINDOW", self.handle_window_close)
        self.first_thread = threading.Thread(target=self.monitor_browser_tabs, daemon=True).start()
        self.second_thread = threading.Thread(target=self.enforce_security_restrictions, daemon=True).start()
        if self.time != "":
            self.timer_label = Label(self.main_window, text=self.format_time(self.remaining_time),
                                     font=("Arial", 20, "bold"), fg="green")
            self.timer_label.pack(pady=10)
            self.update_timer()
        self.button_back = Button(self.main_window,
                                  text="вернутся на главную страницу",
                                  font=("Arial", 20, "bold"),
                                  bg="#666666",
                                  fg="white",
                                  activebackground="#555555",
                                  activeforeground="white",
                                  relief=FLAT,
                                  bd=0,
                                  command=lambda: self.browser_driver.get(self.local_page_url))
        self.button_back.pack()
        self.main_window.mainloop()

    def create_browser_lock_mutex(self):
        mutex_name = {
            "chrome": "Global\\ChromeBrowserLock",
            "edge": "Global\\EdgeBrowserLock",
            "firefox": "Global\\FirefoxBrowserLock"
        }[self.browser_type]
        self.mutex2 = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
        if not self.mutex2:
            return None
        return self.mutex2

    def handle_window_close(self):
        pass

    def check_browser_process_running(self):
        mutex_name = {
            "chrome": f"Global\\ChromeBrowserLock",
            "edge": "Global\\EdgeBrowserLock",
            "firefox": "Global\\FirefoxBrowserLock"
        }[self.browser_type]
        self.mutex = ctypes.windll.kernel32.OpenMutexW(0x00100000, False, mutex_name)
        if self.mutex:
            ctypes.windll.kernel32.CloseHandle(self.mutex)
            return True
        return False

    def generate_allowed_sites_html(self):
        with open(self.html_path, "w", encoding="utf-8") as f:
            f.write("""<!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Каталог разрешённых сайтов</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }

            body {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                min-height: 100vh;
                padding: 40px 20px;
                color: #333;
            }

            .container {
                max-width: 1000px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                padding: 40px;
                position: relative;
                overflow: hidden;
            }

            .container::before {
                content: "";
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 10px;
                background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
            }

            h1 {
                text-align: center;
                margin-bottom: 30px;
                color: #2c3e50;
                font-size: 2.5rem;
                position: relative;
                padding-bottom: 15px;
            }

            h1::after {
                content: "";
                position: absolute;
                bottom: 0;
                left: 50%;
                transform: translateX(-50%);
                width: 100px;
                height: 3px;
                background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
                border-radius: 3px;
            }

            .description {
                text-align: center;
                margin-bottom: 40px;
                font-size: 1.1rem;
                color: #555;
                line-height: 1.6;
            }

            .site-list {
                list-style: none;
                margin-bottom: 40px;
            }

            .site-item {
                margin-bottom: 15px;
                transition: all 0.3s ease;
            }

            .site-item:hover {
                transform: translateX(10px);
            }

            .site-link {
                display: block;
                padding: 15px 20px;
                background: #f8f9fa;
                border-radius: 8px;
                text-decoration: none;
                color: #2c3e50;
                font-size: 1.2rem;
                transition: all 0.3s ease;
                border-left: 4px solid transparent;
            }

            .site-link:hover {
                background: #e9ecef;
                border-left: 4px solid #4b6cb7;
                color: #4b6cb7;
            }

            .footer {
                text-align: center;
                margin-top: 40px;
                color: #777;
                font-size: 0.9rem;
            }

            @media (max-width: 768px) {
                .container {
                    padding: 30px 20px;
                }

                h1 {
                    font-size: 2rem;
                }

                .site-link {
                    font-size: 1rem;
                    padding: 12px 15px;
                }
            }
        </style>
        <script>
            window.open = function() {
                alert("Открытие новых окон запрещено.");
                return null;
            };
        </script>
    </head>
    <body>
        <div class="container">
            <h1>Разрешённые сайты</h1>
            <p class="description">Вы можете посещать только эти веб-сайты. Нажмите на ссылку, чтобы перейти.</p>
            <ul class="site-list">
    """)
            for site in self.whitelisted_domains:
                f.write(
                    f'            <li class="site-item"><a href="https://{site}" target="_self" class="site-link">{site}</a></li>\n')
            f.write("""        </ul>
            <div class="footer">
                <p>Для выхода из программы закройте браузер и введите пароль администратора</p>
            </div>
        </div>
    </body>
    </html>""")
        return "file:///" + self.html_path.replace("\\", "/")

    def launch_controlled_browser(self):
        if self.browser_driver is not None:
            try:
                self.browser_driver.quit()
            except:
                pass
        self.user_data_dir = f"C:\\Temp\\{self.browser_type.capitalize()}PythonProfile_{uuid.uuid4()}"
        os.makedirs(self.user_data_dir, exist_ok=True)
        if self.browser_type == "chrome":
            options = ChromeOptions()
            options.page_load_strategy = "none"
            options.add_argument("--remote-debugging-port=9222")
            options.add_argument("--guest")
            options.add_argument(f"--user-data-dir={self.user_data_dir}")
            options.add_argument("--start-maximized")
            options.add_argument("--no-default-browser-check")
            options.add_argument("--no-first-run")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-popup-blocking")
            options.add_argument("--disable-default-apps")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-session-crashed-bubble")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            self.browser_driver = webdriver.Chrome(options=options)
        elif self.browser_type == "edge":
            options = EdgeOptions()
            options.page_load_strategy = "none"
            options.add_argument("--remote-debugging-port=9222")
            options.add_argument(f"--user-data-dir={self.user_data_dir}")
            options.add_argument("--start-maximized")
            options.add_argument("--no-first-run")
            options.add_argument("--no-remote")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("--disable-infobars")
            options.add_argument("--guest")
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-sync")
            options.add_argument("--disable-cloud-import")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("--app-name=cara")
            self.browser_driver = webdriver.Edge(options=options)
        elif self.browser_type == "firefox":
            def get_latest_geckodriver_url():
                response = requests.get("https://api.github.com/repos/mozilla/geckodriver/releases/latest")
                response.raise_for_status()
                assets = response.json()["assets"]
                for asset in assets:
                    if "win64.zip" in asset["name"]:
                        return asset["browser_download_url"]

            def setup_geckodriver():
                temp_dir = os.path.join(os.environ["TEMP"], "geckodriver")
                os.makedirs(temp_dir, exist_ok=True)
                driver_path = os.path.join(temp_dir, "geckodriver.exe")
                if os.path.exists(driver_path):
                    return driver_path
                download_url = get_latest_geckodriver_url()
                zip_path = os.path.join(temp_dir, "geckodriver.zip")
                with requests.get(download_url, stream=True) as r:
                    r.raise_for_status()
                    with open(zip_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extract("geckodriver.exe", temp_dir)
                os.remove(zip_path)
                return driver_path

            path = setup_geckodriver()
            options = FirefoxOptions()
            options.page_load_strategy = "none"
            options.set_preference("remote-debugging-port", 9222)
            options.add_argument(f"--user-data-dir={self.user_data_dir}")
            options.add_argument("--start-maximized")
            options.add_argument("--no-remote")
            options.add_argument("--new-instance")
            options.add_argument("--ignore-certificate-errors")
            options.set_preference("app.update.auto", False)
            options.set_preference("app.update.enabled", False)
            service = FirefoxService(executable_path=path)
            self.browser_driver = webdriver.Firefox(options=options, service=service)
        self.browser_driver.implicitly_wait(3)
        WebDriverWait(self.browser_driver, 3).until(EC.number_of_windows_to_be(1))
        self.browser_driver.get(self.local_page_url)
        self.browser_driver.implicitly_wait(1)
        self.browser_driver.maximize_window()
        self.browser_driver.execute_script(f"document.title = '{self.browser_type}gi';")
        RAMWORKER.add_to_autostart("Soldi")

    def verify_browser_process_active(self):
        if self.browser_driver is None:
            return False
        try:
            _ = self.browser_driver.window_handles
            return True
        except WebDriverException:
            return False

    def enforce_security_restrictions(self):
        while self.is_running:
            try:
                self.terminate_unauthorized_apps()
                self.terminate_unauthorized_instances()
                if self.verify_browser_process_active():
                    title = f"{self.browser_type}gi"
                    browser_window = gw.getWindowsWithTitle(title)
                    if browser_window:
                        browser_window = browser_window[0]
                        if browser_window.isMinimized:
                            browser_window.restore()
                        if not browser_window.isMaximized:
                            browser_window.maximize()
            except:
                pass
            time.sleep(1)

    def terminate_unauthorized_apps(self):
        forbidden = ["chrome.exe", "msedge.exe", "firefox.exe", "opera.exe", "roblox.exe", "minecraft.exe",
                     "yandex.exe", "tlauncher.exe", "browser.exe", "rulauncher.exe", "java.exe", "javaw.exe",
                     "iexplore.exe", "taskmgr.exe", "powershell.exe", "regedit.exe", "mmc.exe", "control.exe",
                     "discord.exe", "steam.exe", "epicgameslauncher.exe", "battle.net.exe", "telegram.exe",
                     "viber.exe", "cmd.exe", "notepad.exe", "wordpad.exe", "WINWORD.exe"]
        current = {
            "chrome": "chrome.exe",
            "edge": "msedge.exe",
            "firefox": "firefox.exe"
        }[self.browser_type]
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                name = proc.info['name'].lower()
                if name in forbidden and name != current:
                    proc.terminate()
            except:
                continue

    def monitor_browser_tabs(self):
        while self.is_running:
            try:
                if not self.verify_browser_process_active():
                    if self.main_window.winfo_exists():
                        self.main_window.after(0, self.safe_shutdown)
                    break
                self.close_unauthorized_tabs()
                if self.browser_driver:
                    self.browser_driver.switch_to.window(self.browser_driver.window_handles[0])
                    self.validate_current_url()
            except Exception as e:
                print(f"Ошибка мониторинга: {e}")
            time.sleep(0.4)

    def safe_shutdown(self):
        try:
            if self.main_window.winfo_exists():
                self.main_window.destroy()
            ctypes.windll.kernel32.CloseHandle(self.mutex)
            ctypes.windll.kernel32.CloseHandle(self.mutex2)
            if not self.flag:
                password = hashlib.sha256(self.unlock_password.encode('utf-8')).hexdigest()
            else:
                password = RAMWORKER.read_sldid_file("data")
            self.is_running = False
            process_blocker.ProcessBlocker(password=password)
        except Exception as e:
            print(f"Ошибка при закрытии: {e}")

    def close_unauthorized_tabs(self):
        if self.verify_browser_process_active() and len(self.browser_driver.window_handles) > 1:
            for handle in self.browser_driver.window_handles[1:]:
                try:
                    self.browser_driver.switch_to.window(handle)
                    self.browser_driver.execute_script("window.close();")
                except:
                    pass

    def validate_current_url(self):
        try:
            if not self.verify_browser_process_active():
                return
            current_url = self.browser_driver.current_url
            if current_url.startswith("file://"):
                decoded_url = unquote(current_url)
                actual_path = urlparse(decoded_url).path.lstrip('/')
                expected_path = os.path.abspath(self.html_path).replace("\\", "/")
                actual_path_abs = os.path.abspath(actual_path).replace("\\", "/")
                if expected_path == actual_path_abs:
                    return
                else:
                    self.browser_driver.execute_script("window.stop();")
                    self.browser_driver.get(self.local_page_url)
                    return
            parsed_url = urlparse(current_url)
            domain = parsed_url.netloc.split(':')[0]
            normalized_domain = domain[4:] if domain.startswith('www.') else domain
            domain_allowed = any(
                allowed_domain == normalized_domain or
                allowed_domain == domain or
                f"www.{allowed_domain}" == domain or
                idna.encode(allowed_domain).decode('ascii') == normalized_domain
                for allowed_domain in self.whitelisted_domains
            )
            if not domain_allowed:
                self.browser_driver.execute_script("window.stop();")
                self.browser_driver.get(self.local_page_url)
        except:
            self.browser_driver = None

    def terminate_unauthorized_instances(self):
        if self.browser_type == "firefox":
            try:
                controlled_pids = set()
                if self.browser_driver:
                    pid = self.browser_driver.service.process.pid
                    controlled_pids.add(pid)
                    for child in psutil.Process(pid).children(recursive=True):
                        controlled_pids.add(child.pid)
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if proc.info['name'].lower() == 'firefox.exe' and proc.info['pid'] not in controlled_pids:
                            proc.terminate()
                    except:
                        continue
            except:
                pass
        else:
            binary = {
                "chrome": "chrome.exe",
                "edge": "msedge.exe"
            }[self.browser_type]
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if binary in proc.info['name'].lower():
                        cmdline = proc.info['cmdline']
                        if cmdline and any(self.user_data_dir in arg for arg in cmdline):
                            pass
                        else:
                            proc.terminate()
                except:
                    continue


def main(browser_type):

    RAMWORKER.write_sldid_file("browser", browser_type)
    main_window = Tk()
    if not RAMWORKER.read_sldid_file("config"):
        checkbox_var = BooleanVar(value=False)
    main_window.title("soldi")
    main_window.iconbitmap(RAMWORKER.get_icon_path("icon.ico"))
    whitelisted_domains = []
    switch_info = False
    unlock_password = ""

    main_window.configure(bg='#f0f2f5')

    container = Frame(main_window, bg='#ffffff', padx=40, pady=40)
    container.place(relx=0.5, rely=0.5, anchor=CENTER)

    header_frame = Frame(container, bg='#ffffff')
    header_frame.pack(pady=(0, 30))

    domain_label = Label(header_frame,
                         text="Введите допустимые ссылки для посещения",
                         font=("Arial", 18, 'bold'),
                         fg="#2c3e50",
                         bg="#ffffff")
    domain_label.pack()

    input_frame = Frame(container, bg='#ffffff')
    input_frame.pack(pady=(0, 10))

    domain_entry = Entry(input_frame,
                         font=("Arial", 18),
                         bd=2,
                         relief=FLAT,
                         bg="#E0FFFF",
                         fg="#333333",
                         insertbackground="#4b6cb7",
                         width=40,
                         highlightthickness=2,
                         highlightbackground="black")
    domain_entry.pack(ipady=8, padx=10)

    buttons_frame = Frame(container, bg='#ffffff')
    buttons_frame.pack()

    def validate_domain_trustworthiness(url):
        trusted_tlds = {'com', 'org', 'net', 'gov', 'edu', 'io', 'co', 'ai', 'biz', 'ru', 'su', 'us', 'uk', 'de', 'рф',
                        'me', 'mit', 'il', 'by', 'kz', 'eu', 'gb', 'fr', 'it', 'es', 'pt', 'nl', 'pl',
                        'ch', 'se', 'no', 'fi', 'dk', 'ca', 'au', 'nz', 'jp', 'cn', 'in', 'br', 'mx', 'ar', 'cl', 'pe',
                        'co', 've', 'id', 'my', 'th', 'vn', 'ph', 'sg', 'kr', 'tr', 'gr', 'at', 'be', 'cz', 'hu', 'ro',
                        'sk', 'bg', 'hr', 'rs', 'si', 'lt', 'lv', 'ee', 'is', 'ie', 'za'}
        parts = url.strip().split('.')
        if len(parts) < 2 or not parts[-2]:
            return False
        tld = parts[-1].lower()
        return tld in trusted_tlds

    def del_web_site():
        try:
            info_site = whitelisted_domains[-1]

            whitelisted_domains.pop()
            bad_label = Label(input_frame,
                              text=f"Ссылка {info_site} удалена!",
                              fg="#F4A900",
                              bg="#ffffff",
                              font=("Arial", 12))

        except Exception:
            bad_label = Label(input_frame,
                              text=f"Ссылки отсутствуют, удалять нечего!",
                              fg="#F4A900",
                              bg="#ffffff",
                              font=("Arial", 12))
        bad_label.pack()
        reject_button.config(state="disabled")
        main_window.after(1000, lambda: [reject_button.config(state="normal"), bad_label.destroy()])

    def del_all():
        if whitelisted_domains != []:
            for i in range(len(whitelisted_domains)):
                whitelisted_domains.pop()
            bad_label = Label(input_frame,
                              text=f"Список был полностью очищен",
                              fg="#F4A900",
                              bg="#ffffff",
                              font=("Arial", 12))
            bad_label.pack()
            del_all_button.config(state="disabled")
        else:
            bad_label = Label(input_frame,
                              text=f"Список пуст, удалять нечего",
                              fg="#F4A900",
                              bg="#ffffff",
                              font=("Arial", 12))
            bad_label.pack()
            del_all_button.config(state="disabled")
        main_window.after(1000, lambda: [del_all_button.config(state="normal"), bad_label.destroy()])

    def add_allowed_website():
        def des_and_conf():
            bad_label.destroy()
            confirm_button.config(state="normal")

        domain = domain_entry.get().strip()
        if not domain:
            return

        if domain.startswith(('http://', 'https://')):
            domain = domain.split('://')[1]

        domain = domain.split('/')[0]
        normalized_domain = domain[4:] if domain.startswith('www.') else domain

        if validate_domain_trustworthiness(normalized_domain):
            if normalized_domain not in whitelisted_domains:
                whitelisted_domains.append(normalized_domain)
                domain_entry.delete(0, END)
                success_label = Label(input_frame,
                                      text=f"Добавлен: {normalized_domain}",
                                      fg="#4CAF50",
                                      bg="#ffffff",
                                      font=("Arial", 12))
                success_label.pack()
                main_window.after(1000, success_label.destroy)
            else:
                domain_entry.delete(0, END)
                confirm_button.config(state="disabled")
                bad_label = Label(input_frame,
                                  text=f"ВНИМАНИЕ! Вы уже вводили данный сайт",
                                  fg="#F4A900",
                                  bg="#ffffff",
                                  font=("Arial", 12))
                bad_label.pack()
                main_window.after(2000, des_and_conf)
        else:
            domain_entry.delete(0, END)
            confirm_button.config(state="disabled")
            bad_label = Label(input_frame,
                              text=f"ОШИБКА! ВВЕДЕННАЯ ВАМИ СТРОКА - НЕ САЙТ!",
                              fg="red",
                              bg="#ffffff",
                              font=("Arial", 12))
            bad_label.pack()
            main_window.after(2000, des_and_conf)

    def prompt_for_password_setup(flag=False):
        nonlocal switch_info
        if not whitelisted_domains and not flag:
            ctypes.windll.user32.MessageBoxW(0, "Вы не ввели ссылки для посещения", "Ошибка", 0x0000 | 0x0010 | 0x1000)
        else:
            if flag:
                switch_info = True
            session_button.destroy()
            reject_button.destroy()
            del_all_button.destroy()
            confirm_button.destroy()
            next_button.config(text="УСТАНОВИТЬ ПАРОЛЬ",
                               command=set_unlock_password,
                               font=("Arial", 14, 'bold'),
                               bg="#4b6cb7",
                               fg="white",
                               activebackground="#3a5a99",
                               activeforeground="white")
            domain_label.config(text="Придумайте надёжный пароль\nдля отключения программы")
            next_button.pack(pady=(0, 5))

    def write_session(whitelist):
        RAMWORKER.write_sldid_file("session", " ".join(whitelist))

    def restore_session():
        if RAMWORKER.read_sldid_file("session") == "":
            ctypes.windll.user32.MessageBoxW(0, "Файл сессии не найден", "Ошибка", 0x0000 | 0x0010 | 0x1000)
        else:
            prompt_for_password_setup(True)

    def set_unlock_password():
        nonlocal whitelisted_domains, unlock_password, checkbox_var
        if switch_info:
            whitelisted_domains = RAMWORKER.read_sldid_file("session").split()
        time_limit = RAMWORKER.read_sldid_file("config")
        unlock_password = domain_entry.get()
        if not unlock_password:
            ctypes.windll.user32.MessageBoxW(0, "Вы не ввели пароль", "Ошибка", 0x0000 | 0x0010 | 0x1000)
        else:
            main_window.destroy()
            write_session(whitelisted_domains)
            if not RAMWORKER.read_sldid_file("config"):
                RAMWORKER.write_sldid_file("status", str(checkbox_var.get()))
            App(whitelisted_domains, unlock_password, time_limit, browser_type, False)

    if not RAMWORKER.read_sldid_file("config"):
        style = ttk.Style()
        style.theme_use('alt')

        style.configure('TCheckbutton',
                    font=('Arial', 15),
                    indicatorsize=16,
                    padding=5,
                    background='white',
                    foreground='black'
                    )

        checkbox = ttk.Checkbutton(
        buttons_frame,
        text="Разрешить восстанавливать браузер",
        variable=checkbox_var,
        style='TCheckbutton',
        takefocus=0
    )

        checkbox.pack(pady=5, anchor='w')

    confirm_button = Button(buttons_frame,
                            text="ДОБАВИТЬ ССЫЛКУ",
                            font=("Arial", 14, 'bold'),
                            command=add_allowed_website,
                            bg="#4CAF50",
                            fg="white",
                            activebackground="#3e8e41",
                            activeforeground="white",
                            bd=0,
                            relief=FLAT,
                            padx=20,
                            pady=10)
    confirm_button.pack(pady=(0, 15), fill=X)
    reject_button = Button(buttons_frame,
                           text="УДАЛИТЬ ПОСЛЕДНЮЮ ССЫЛКУ",
                           font=("Arial", 14, 'bold'),
                           command=del_web_site,
                           bg="#FF4500",
                           fg="white",
                           activebackground="#FF4500",
                           activeforeground="white",
                           bd=0,
                           relief=FLAT,
                           padx=20,
                           pady=10)
    reject_button.pack(pady=(0, 15), fill=X)
    del_all_button = Button(buttons_frame,
                            text="УДАЛИТЬ ВСЕ ССЫЛКИ",
                            font=("Arial", 14, 'bold'),
                            command=del_all,
                            bg="#8B0000",
                            fg="white",
                            activebackground="#8B0000",
                            activeforeground="white",
                            bd=0,
                            relief=FLAT,
                            padx=20,
                            pady=10)
    del_all_button.pack(pady=(0, 15), fill=X)
    session_button = Button(buttons_frame,
                            text="ВОССТАНОВИТЬ СЕССИЮ",
                            font=("Arial", 14, 'bold'),
                            bg="#9C27B0",
                            fg="white",
                            activebackground="#7B1FA2",
                            activeforeground="white",
                            bd=0,
                            command=restore_session,
                            relief=FLAT,
                            padx=20,
                            pady=10)
    session_button.pack(pady=(0, 15), fill=X)
    next_button = Button(buttons_frame,
                         text="ЗАВЕРШИТЬ ВВОД",
                         font=("Arial", 14, 'bold'),
                         command=prompt_for_password_setup,
                         bg="#FF9800",
                         fg="white",
                         activebackground="#e68a00",
                         activeforeground="white",
                         bd=0,
                         relief=FLAT,
                         padx=20,
                         pady=10)
    next_button.pack(pady=(0, 15), fill=X)
    exit_button = Button(buttons_frame,
                         text="ЗАКРЫТЬ ПРИЛОЖЕНИЕ",
                         font=("Arial", 14, 'bold'),
                         command=lambda: main_window.destroy(),
                         bg="#f44336",
                         fg="white",
                         activebackground="#d32f2f",
                         activeforeground="white",
                         bd=0,
                         relief=FLAT,
                         padx=20,
                         pady=10)
    exit_button.pack(fill=X)
    separator = Frame(container, height=2, bg="#e0e0e0", bd=0)
    separator.pack(fill=X, pady=20)
    footer_label = Label(container,
                         text="Контроль доступа в интернет",
                         font=("Arial", 10),
                         fg="#757575",
                         bg="#ffffff")
    footer_label.pack()
    main_window.attributes('-fullscreen', True)
    main_window.mainloop()
