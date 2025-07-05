import os
import shutil
a=os.environ["TEMP"]
for i in os.listdir(a):
    if i.startswith("MEI"):
        shutil.rmtree(i,ignore_errors=True)