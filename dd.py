from tkinter import *
from PIL import Image, ImageTk
from selenium.webdriver.edge.options import Options
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import ctypes
options = Options()

browser_driver = webdriver.Safari(options=options)

