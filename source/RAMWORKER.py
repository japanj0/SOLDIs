import psutil

def clearing_RAM():
    drivers = ['geckodriver.exe', 'chromedriver.exe', 'msedgedriver.exe']
    for proc in psutil.process_iter(['name']):
        print(proc)
        if proc.info['name'] in drivers:
            try:
                proc.terminate()
            except Exception as e:
                print(e)
