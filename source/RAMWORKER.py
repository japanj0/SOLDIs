import psutil

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
