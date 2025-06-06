import sys
import os
from tkinter import *
from PIL import Image, ImageTk
import tempfile
import atexit
import ctypes
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FireOptions
from selenium.webdriver.edge.service import Service as Edgeservice
from selenium.webdriver.edge.options import Options as Edgeoptions
from selenium.webdriver.chrome.service import Service as Chromeservice
from selenium.webdriver.chrome.options import Options as Chromeoptions
import Edge_control
import Firefox_control
import Chrome_control


def require_admin():
    try:
        if ctypes.windll.shell32.IsUserAnAdmin():
            return True
        else:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, None, 1)
            sys.exit()
    except Exception as e:
        print(f"Ошибка при запросе прав администратора: {e}")
        sys.exit()


def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def extract_temp_image(resource_path):
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


def cleanup_temp_files():
    temp_dir = os.path.join(tempfile.gettempdir(), "soldi_images")
    if os.path.exists(temp_dir):
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Ошибка при удалении временного файла {file_path}: {e}")


atexit.register(cleanup_temp_files)


def Edge():
    try:
        options = Edgeoptions()
        service = Edgeservice(timeout=3)
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        browser_driver = webdriver.Edge(options=options, service=service)
        browser_driver.quit()
        win.destroy()
        Edge_control.main()
    except Exception as e:
        print(e)
        win.focus_force()
        ctypes.windll.user32.MessageBoxW(0, "Данный браузер не установлен на вашем компьютере", "Ошибка",
                                         0x0000 | 0x0010 | 0x1000)


def Firefox():
    try:
        options = FireOptions()
        service = FirefoxService(timeout=3)
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        browser_driver = webdriver.Firefox(options=options, service=service)
        browser_driver.quit()
        win.destroy()
        Firefox_control.main()
    except Exception as e:
        print(e)
        win.focus_force()
        ctypes.windll.user32.MessageBoxW(0, "Данный браузер не установлен на вашем компьютере", "Ошибка",
                                         0x0000 | 0x0010 | 0x1000)


def Chrome():
    try:
        options = Chromeoptions()
        service = Chromeservice(timeout=3)
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        browser_driver = webdriver.Chrome(options=options, service=service)
        browser_driver.quit()
        win.destroy()
        Chrome_control.main()
    except Exception as e:
        print(e)
        win.focus_force()
        ctypes.windll.user32.MessageBoxW(0, "Данный браузер не установлен на вашем компьютере", "Ошибка",
                                         0x0000 | 0x0010 | 0x1000)


require_admin()
win = Tk()
win.attributes("-fullscreen", True)
win.configure(background="white")

try:
    edge_path = get_resource_path("logoedge.png")
    fox_path = get_resource_path("fox_im.png")
    chrome_path = get_resource_path("chromelogo.png")

    edge_temp = extract_temp_image(edge_path)
    fox_temp = extract_temp_image(fox_path)
    chrome_temp = extract_temp_image(chrome_path)

    ed_im = ImageTk.PhotoImage(Image.open(edge_temp)) if edge_temp else None
    fox_im = ImageTk.PhotoImage(Image.open(fox_temp)) if fox_temp else None
    chrome_im = ImageTk.PhotoImage(Image.open(chrome_temp)) if chrome_temp else None
except Exception as e:
    print(f"Ошибка при загрузке изображений: {e}")
    ed_im = ImageTk.PhotoImage(Image.new('RGB', (100, 100), 'white'))
    fox_im = ImageTk.PhotoImage(Image.new('RGB', (100, 100), 'white'))
    chrome_im = ImageTk.PhotoImage(Image.new('RGB', (100, 100), 'white'))

label_f_u = Label(win, text="выберите браузер который вам удобен", font=("arial", 34), background="white")
label_f_u.pack()
label_f_u.place(x=1440 // 2 - 350, y=100)

button_edge = Button(win, text="Edge", image=ed_im, compound='left', background="white", font=("arial", 24),
                     command=Edge, relief=RAISED)
button_edge.pack()
button_edge.place(x=1440 // 2 - 100, y=400)

button_chrome = Button(win, text="Chrome", compound='left', background="white", font=("arial", 29), image=chrome_im,
                       relief=RAISED, command=Chrome)
button_chrome.pack()
button_chrome.place(x=1440 // 2 + 300, y=400)

button_firefox = Button(win, text="Firefox", compound='left', background="white", font=("arial", 29), image=fox_im,
                        command=Firefox, relief=RAISED)
button_firefox.pack()
button_firefox.place(x=1440 // 2 - 500, y=400)

exit_button = Button(win, text="покинуть приложение", background="white", font=("arial", 29),
                     command=lambda: sys.exit())
exit_button.pack()
exit_button.place(x=1440 // 2 - 200, y=650)

win.mainloop()
