import os
import numpy as np
import re
from glob import glob1
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

def DataframeCreator():
    os.chdir('./')
    wd = os.getcwd()
    results = os.path.join(wd, 'logs')
    # Pattern for getting data from outputs
    pattern_nodes = re.compile(r'(p\d{4})\b', re.IGNORECASE)
    pattern_model = re.compile(r'model\: (\w+)', re.I)
    pattern_size = re.compile(r'Global lattice size: (\d+)x(\d+)x(\d+)', re.I)
    pattern_devices = re.compile(r'Selecting device', re.I)
    pattern_time = re.compile(r'Total duration: (\d+\.\d+)', re.I)
    pattern_speed = re.compile(r'(\d+\.\d+) MLBUps', re.I)

    data_frame = pd.DataFrame(columns=['Name', 'Model', 'Nodes', 'Devices', 'Speed', 'Time', 'X', 'Y', 'Z'])
    for txtFile in glob1(results, "*.out"):
        dane = os.path.join(results, txtFile)
        with open(dane, "r") as f:
            content = f.read()

        #find data that fits to patterns
        matches_nodes = pattern_nodes.finditer(content)
        matches_model = pattern_model.finditer(content)
        matches_size = pattern_size.finditer(content)
        matches_devices = pattern_devices.findall(content)
        matches_time = pattern_time.finditer(content)
        matches_speed = pattern_speed.finditer(content)

        #need to capture data to a list
        Name = txtFile
        Speed = np.mean(np.array([float(match.group(1)) for match in matches_speed]))
        for match in matches_model:
            Model = match.group(1)
        if pattern_time.search(content) == None:
            Time = None
        else:
            for match in matches_time:
                Time = match.group(1)
        Node = []
        for match in matches_nodes:
            temp = match.group(1)
            Node.append(temp)
        Devices = len(matches_devices)
        for match in matches_size:
            SizeX = match.group(1)
            SizeY = match.group(2)
            SizeZ = match.group(3)
        #creating a list and pandas row to append to DataFrame
        to_append = [Name, Model, Node, Devices, Speed, Time, SizeX, SizeY, SizeZ]
        a_series = pd.Series(to_append, index=data_frame.columns)
        data_frame = data_frame.append(a_series, ignore_index=True)

    data_frame.to_csv(r'export_dataframe2.csv', header=True, index=False)


DataframeCreator()