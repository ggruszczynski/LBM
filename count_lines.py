import os
import numpy as np
import shutil
import re
from glob import glob1
import pandas as pd

# path="G:\Python"
# results="G:\Studia\Przejsciowka\Results\logs"

wd = os.getcwd()
results = os.path.join(wd, 'logs')

# Pattern for getting data from outputs
pattern_nodes = re.compile(r'(p\d{4})\b', re.IGNORECASE)
pattern_model = re.compile(r'model\: (\w+)', re.I)
pattern_size = re.compile(r'Global lattice size: (\d+)x(\d+)x(\d+)', re.I)
pattern_devices = re.compile(r'Selecting device', re.I)
pattern_time = re.compile(r'Total duration: (\d+\.\d+)', re.I)
pattern_speed = re.compile(r'(\d+\.\d+) MLBUps', re.I)

# Lists for collecting data
nodes = []
model = []
size = []
device_num = []
time = []
size1 = []
size2 = []
size3 = []
speed = []
name = []
'''
device_num=np.array([])
size1=np.array([])
size2=np.array([])
size3=np.array([])
speed=np.array([])'''

for txtFile in glob1(results, "*.out"):
    dane = os.path.join(results, txtFile)
    with open(dane, "r") as f:
        content = f.read()
    matches_nodes = pattern_nodes.finditer(content)
    matches_model = pattern_model.finditer(content)
    matches_size = pattern_size.finditer(content)
    matches_devices = pattern_devices.findall(content)
    matches_time = pattern_time.finditer(content)
    matches_speed = pattern_speed.finditer(content)
    # print(type(matches_nodes))

    name.append(txtFile)
    speed.append(np.mean(np.array([float(match.group(1)) for match in matches_speed])))
    for match in matches_model:
        temp = match.group(1)
        model.append(temp)  # why you cannot make .append(match.group(1)) in oneline?
    if pattern_time.search(content) == None:
        time.append(None)
    else:
        for match in matches_time:
            temp = match.group(1)
        time.append(temp)
    temp = []
    for match in matches_nodes:
        t1 = match.group(1)
        temp.append(t1)
    # print(matches_nodes)
    nodes.append(temp)
    device_num.append(len(matches_devices))
    for match in matches_size:
        x = match.group(1)
        size1.append(x)
        y = match.group(2)
        size2.append(y)
        z = match.group(3)
        size3.append(z)

    # plik.writelines(matches_model.group(1)+"\t"+matches_nodes+"\t"+matches_size.group(1)+"x"+matches_size.group(2)+"x"+matches_size.group(3))
    '''for s in matches_model:
        plik.writelines("\n"+s.group(1)+"\t"+str(len(matches_devices)))
    #print(matches_nodes)'''

data_temp = list(zip(name, model, nodes, device_num, speed, time, size1, size2, size3))
data1 = pd.DataFrame(data_temp, columns=['Name', 'Model', 'Nodes', 'Devices', 'Speed', 'Time', 'X', 'Y', 'Z'])

# for later-try to make multindex
'''data_temp = list(zip(size1, size2, size3))
    columns=pd.MultiIndex.from_product([['Size'],['X','Y','Z']])
    data2=pd.DataFrame([size1,size2,size3], columns=columns)'''

data1.to_csv(r'export_dataframe.csv', header=True, index=False)
