import os
import numpy as np
import re
from glob import glob1
import pandas as pd
import timeit

start=timeit.default_timer()
os.chdir('./')
wd = os.getcwd()
print(wd)
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

    name.append(txtFile)
    speed.append(np.mean(np.array([float(match.group(1)) for match in matches_speed])))
    for match in matches_model:
        Model = match.group(1)
        model.append(Model)
    if pattern_time.search(content) == None:
        Time = None
        time.append(Time)
    else:
        for match in matches_time:
            Time = match.group(1)
        time.append(Time)
    temp = []
    Node = []
    for match in matches_nodes:
        temp = match.group(1)
        Node.append(temp)
    nodes.append(Node)
    Devices = len(matches_devices)
    device_num.append(Devices)
    for match in matches_size:
        SizeX = match.group(1)
        size1.append(SizeX)
        SizeY = match.group(2)
        size2.append(SizeY)
        SizeZ = match.group(3)
        size3.append(SizeZ)

data_temp = list(zip(name, model, nodes, device_num, speed, time, size1, size2, size3))
data1 = pd.DataFrame(data_temp, columns=['Name', 'Model', 'Nodes', 'Devices', 'Speed', 'Time', 'X', 'Y', 'Z'])

data1.to_csv(r'export_dataframe.csv', header=True, index=False)

t1 = float(timeit.default_timer()-start)
print ("Czas :", str(t1))