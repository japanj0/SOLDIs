import sys
import os
import threading
import time
import psutil
import win32gui
import win32con
import hashlib
import multiprocessing
from urllib.parse import urlparse, unquote
import idna
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEnginePage
from PyQt6.QtCore import QUrl, Qt, QTimer, QCoreApplication
import RAMWORKER
import process_blocker

QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)

class BrowserPage(QWebEnginePage):
    def acceptNavigationRequest(self, url, navigation_type, is_main_frame):
        return True

class ArcadeBrowser(QMainWindow):
    def __init__(self, whitelisted_domains, unlock_password, time_limit, browser_type, flag):
        super().__init__()
        self.whitelisted_domains = whitelisted_domains
        self.unlock_password = unlock_password
        self.browser_type = browser_type
        self.flag = flag
        self.is_running = True
        self.is_shutting_down = False
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.showFullScreen()
        if not self.flag:
            self.hashed = hashlib.sha256(self.unlock_password.encode('utf-8')).hexdigest()
            RAMWORKER.write_sldid_file("data", self.hashed)

        if time_limit and time_limit != "":
            self.remaining_time = int(time_limit) * 60
        else:
            self.remaining_time = 0
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.html_path = os.path.join(self.script_dir, "links.html")
        self.local_page_url = self.generate_allowed_sites_html()
        RAMWORKER.add_to_autostart("Soldi")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.control_panel = QWidget()
        self.control_panel.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border-bottom: 2px solid #ccc;
            }
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: green;
                padding: 5px 10px;
            }
            QPushButton {
                font-size: 12px;
                font-weight: bold;
                background-color: #666666;
                color: white;
                border: none;
                padding: 4px 10px;
                border-radius: 3px;
                max-width: 150px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)

        panel_layout = QHBoxLayout(self.control_panel)
        panel_layout.setContentsMargins(10, 5, 10, 5)
        self.control_panel.setFixedHeight(40)
        if self.remaining_time > 0:
            self.timer_label = QLabel(f"Осталось: {self.format_time(self.remaining_time)}")
            self.timer_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            panel_layout.addWidget(self.timer_label, alignment=Qt.AlignmentFlag.AlignLeft)
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_timer)
            self.timer.start(1000)
        else:
            panel_layout.addStretch()
        panel_layout.addStretch()
        self.back_button = QPushButton("вернуться на главную")
        self.back_button.setFixedSize(130, 25)
        self.back_button.clicked.connect(self.return_to_main_page)
        panel_layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.control_panel)
        self.browser = QWebEngineView()
        self.browser.setPage(BrowserPage(self.browser))
        settings = self.browser.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.ErrorPageEnabled, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, False)
        self.browser.urlChanged.connect(self.check_url)
        layout.addWidget(self.browser)
        self.browser.setUrl(QUrl(self.local_page_url))
        self.setWindowTitle("Браузер с белым списком")
        self.security_thread = threading.Thread(target=self.enforce_security_restrictions, daemon=True)
        self.security_thread.start()

    def format_time(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        mins, secs = divmod(remainder, 60)
        return f"{hours:02d}:{mins:02d}:{secs:02d}"

    def update_timer(self):
        if not self.is_running or self.is_shutting_down:
            return
        if self.remaining_time > 0:
            self.remaining_time -= 1
            time_str = self.format_time(self.remaining_time)
            self.timer_label.setText(f"Осталось: {time_str}")
        else:
            self.safe_shutdown()

    def return_to_main_page(self):
        self.browser.setUrl(QUrl(self.local_page_url))

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

    def check_url(self, url):
        url_str = url.toString()
        if url_str.startswith("file://"):
            decoded_url = unquote(url_str)
            actual_path = urlparse(decoded_url).path.lstrip('/')
            expected_path = os.path.abspath(self.html_path).replace("\\", "/")
            actual_path_abs = os.path.abspath(actual_path).replace("\\", "/")
            if expected_path == actual_path_abs:
                return
            else:
                self.browser.setUrl(QUrl(self.local_page_url))
                return
        parsed_url = urlparse(url_str)
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
            self.browser.setUrl(QUrl(self.local_page_url))

    def terminate_explorer_safelly(self):
        try:
            def callback(hwnd, _):
                if win32gui.GetClassName(hwnd) == "CabinetWClass":
                    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

            win32gui.EnumWindows(callback, None)
        except Exception:
            pass

    def enforce_security_restrictions(self):
        forbidden = [
            "chrome.exe", "msedge.exe", "firefox.exe", "opera.exe", "roblox.exe", "minecraft.exe",
            "yandex.exe", "tlauncher.exe", "browser.exe", "rulauncher.exe", "java.exe", "javaw.exe",
            "iexplore.exe", "taskmgr.exe", "powershell.exe", "regedit.exe", "mmc.exe", "control.exe",
            "discord.exe", "steam.exe", "epicgameslauncher.exe", "battle.net.exe", "telegram.exe",
            "viber.exe", "cmd.exe", "notepad.exe", "wordpad.exe", "WinStore.App.exe",
            "ida.exe", "ida64.exe", "x64dbg.exe", "x32dbg.exe", "ollydbg.exe", "windbg.exe",
            "windbgx.exe", "ghidra.exe", "radare2.exe", "cheatengine.exe", "immunitydebugger.exe",
            "procexp.exe", "procexp64.exe", "processhacker.exe", "processhacker2.exe", "procmon.exe",
            "procmon64.exe", "vmmap.exe", "rammap.exe", "handle.exe", "listdlls.exe",
            "pwsh.exe", "wsl.exe", "bash.exe", "ubuntu.exe", "debian.exe", "kali.exe", "ssh.exe",
            "putty.exe", "kitty.exe", "cygwin.exe", "mingw.exe", "msys2.exe",
            "wireshark.exe", "tshark.exe", "nmap.exe", "netcat.exe", "nc.exe", "tcpdump.exe",
            "msconfig.exe", "regedt32.exe", "autoruns.exe", "autorunsc.exe", "services.exe",
            "tasklist.exe", "systeminfo.exe", "whoami.exe", "net.exe", "ipconfig.exe",
            "hxd.exe", "hexedit.exe", "010editor.exe", "winhex.exe", "resourcehacker.exe",
            "dnspy.exe", "ilspy.exe", "peid.exe", "cffexplorer.exe", "dependencywalker.exe",
            "SystemSettings.exe", "resmon.exe"
        ]
        while self.is_running:
            try:
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        name = proc.info['name'].lower()
                        if name in [f.lower() for f in forbidden]:
                            try:
                                proc.terminate()
                            except:
                                continue
                    except:
                        continue
                self.terminate_explorer_safelly()
            except:
                pass
            time.sleep(0.4)

    def safe_shutdown(self):
        if self.is_shutting_down:
            return
        self.is_shutting_down = True
        self.is_running = False
        if hasattr(self, 'timer') and self.timer:
            self.timer.stop()
        if not self.flag:
            password = self.hashed
        else:
            password = self.unlock_password
        p = multiprocessing.Process(
            target=process_blocker.ProcessBlocker,
            args=(password,),
            kwargs={'is_notrestarted': True}
        )
        p.start()
        QTimer.singleShot(0, QApplication.quit)

    def closeEvent(self, event):
        if self.is_shutting_down:
            event.accept()
            return
        self.is_shutting_down = True
        self.is_running = False
        if hasattr(self, 'timer') and self.timer:
            self.timer.stop()
        if not self.flag:
            password = self.hashed
        else:
            password = self.unlock_password
        p = multiprocessing.Process(
            target=process_blocker.ProcessBlocker,
            args=(password,),
            kwargs={'is_notrestarted': True}
        )
        p.start()
        event.accept()
        QTimer.singleShot(0, QApplication.quit)

def run_arcade(whitelist, password, time_limit, browser_type, flag):
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    window = ArcadeBrowser(whitelist, password, time_limit, browser_type, flag)
    window.show()
    app.exec()

def run_arcade_process(whitelist, password, time_limit, browser):
    app = QApplication(sys.argv)
    window = ArcadeBrowser(whitelist, password, time_limit, browser, True)
    window.show()
    app.exec()