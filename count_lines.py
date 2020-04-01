import os
import numpy as np
import shutil
import re
from glob import glob1

path="G:\Python"
results="G:\Studia\Przejsciowka\Results\logs"
#Pattern for getting data from outputs
pattern_nodes=re.compile(r'(pd{4})/b', re.IGNORECASE)
pattern_model=re.compile(r'model\: (\w+)', re.I)
pattern_size=re.compile(r'Global lattice size:(\d+)x(\d+)x(\d+)', re.I)
pattern_devices=re.compile(r'Selecting device', re.I)

with open("Result.txt", "w") as plik:
    plik.writelines("Model"+"\t"+"devices"+"\t"+"nodes"+"\t"+"Global Lattice size:")
    for txtFile in glob1(results, "*.out"):
        dane=os.path.join(results, txtFile)
        with open(dane,"r") as f:
            content=f.read()
            matches_nodes=pattern_nodes.finditer(content)
            matches_model=pattern_model.finditer(content)
            matches_size=pattern_size.finditer(content)
            matches_devices=pattern_devices.findall(content)
        #plik.writelines(matches_model.group(1)+"\t"+matches_nodes+"\t"+matches_size.group(1)+"x"+matches_size.group(2)+"x"+matches_size.group(3))
        for s in matches_model:
            plik.writelines("\n"+s.group(1)+"\t"+str(len(matches_devices)))
        print(matches_nodes)
