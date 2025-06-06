import sys
from tkinter import *
from PIL import Image, ImageTk
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FireOptions
from selenium.webdriver.edge.service import Service as Edgeservice
from selenium.webdriver.edge.options import Options as Edgeoptions
import ctypes
import Edge_control
import Firefox_control
def require_admin():
    try:
        if ctypes.windll.shell32.IsUserAnAdmin():
            return True
        else:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, None, 1)
            sys.exit()
    except Exception as e:
        print(f"Ошибка при запросе прав администратора: {e}")
        sys.exit()
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
        ctypes.windll.user32.MessageBoxW(
            0,
            "Данный браузер не установлен на вашем компьютере",
            "Ошибка",
            0x0000 | 0x0010 | 0x1000
        )
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
        ctypes.windll.user32.MessageBoxW(
            0,
            "Данный браузер не установлен на вашем компьютере",
            "Ошибка",
            0x0000 | 0x0010 | 0x1000
        )


require_admin()
win = Tk()
win.attributes("-fullscreen", True)
win.configure(background="white")

img = Image.open("logoedge.png")
ed_im = ImageTk.PhotoImage(img)

img2 = Image.open("fox_im.png")
fox_im = ImageTk.PhotoImage(img2)

img3 = Image.open("chromelogo.png")
chrome_im = ImageTk.PhotoImage(img3)

label_f_u = Label(win, text="выберите браузер который вам удобен", font=("arial",24),background="white")
label_f_u.pack()
label_f_u.place(x=1440//2-250, y=100)

button_edge=Button(win, text="Edge", image=ed_im, compound='left', background="white", font=("arial",24), command=Edge,relief=RAISED)
button_edge.pack()
button_edge.place(x=1440//2-100, y=400)

button_chrome = Button(win, text="Chrome", compound='left', background="white", font=("arial",29), image=chrome_im,relief=RAISED)
button_chrome.pack()
button_chrome.place(x=1440//2+300, y=400)

button_firefox=Button(win, text="Firefox", compound='left', background="white", font=("arial",29), image=fox_im, command=Firefox,relief=RAISED)
button_firefox.pack()
button_firefox.place(x=1440//2-500, y=400)
win.mainloop()
