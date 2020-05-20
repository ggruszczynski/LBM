import os
import numpy as np
import re
from glob import glob1
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import timeit


def FileDataCreator():
    os.chdir('./')
    wd = os.getcwd()
    results = os.path.join(wd, 'logs')
    # Pattern for getting data from outputs
    pattern_nodes = re.compile(r'(p\d{4})\n', re.IGNORECASE)
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

        # find data that fits to patterns
        matches_nodes = pattern_nodes.finditer(content)
        matches_model = pattern_model.finditer(content)
        matches_size = pattern_size.finditer(content)
        matches_devices = pattern_devices.findall(content)
        matches_time = pattern_time.finditer(content)
        matches_speed = pattern_speed.finditer(content)

        # need to capture data to a list
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
        temp = None;
        for match in matches_nodes:
            temp = match.group(1)
            Node.append(temp)
        Devices = len(matches_devices)
        for match in matches_size:
            SizeX = match.group(1)
            SizeY = match.group(2)
            SizeZ = match.group(3)
        # creating a list and pandas row to append to DataFrame
        to_append = [Name, Model, Node, Devices, Speed, Time, SizeX, SizeY, SizeZ]
        a_series = pd.Series(to_append, index=data_frame.columns)
        data_frame = data_frame.append(a_series, ignore_index=True)

    data_frame.to_csv(r'export_dataframe.csv', header=True, index=False)


def PlotCreator():
    fig_size = plt.rcParams["figure.figsize"]
    fig_size[0] = 16
    fig_size[1] = 8
    plt.rcParams["figure.figsize"] = fig_size
    df1 = pd.read_csv('export_dataframe.csv')
    F1 = df1['Model'].unique().tolist()
    Filt = [(df1['Model'] == a) for a in F1]
    filt = Filt[0]
    filt2 = Filt[1]
    x1 = df1.loc[filt]['Devices']
    x2 = df1.loc[filt2]['Devices']
    y1 = df1.loc[filt]['Speed']
    y2 = df1.loc[filt2]['Speed']
    m1, b1 = np.polyfit(x1, y1, 1)
    m2, b2 = np.polyfit(x2, y2, 1)
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, constrained_layout=True)
    # fig.figsize=(4,12)
    # plt.figure(figsize=(200,500))
    fig.suptitle('Weak Scaling', fontsize=25)

    ax1.plot(df1.loc[filt]['Devices'], df1.loc[filt]['Speed'], 'gx')
    ax2.plot(df1.loc[filt2]['Devices'], df1.loc[filt2]['Speed'], 'gx')
    x = np.linspace(1, 13, 100)
    ax1.plot(x, m1 * x + b1, 'r--', linewidth=2, label='Best fit line')
    ax2.plot(x, m2 * x + b2, 'r--', linewidth=2, label='Best fit line')
    # fig.tight_layout(pad=2.0)
    # plt.setp(ax2, xlabel='Number of GPU')
    ax1.legend(shadow=True, fancybox=True)
    ax2.legend(shadow=True, fancybox=True)
    ax1.set_title('d3q27q27', fontsize=20)
    ax2.set_title('d3q27q7', fontsize=20)
    ax1.set_xlabel('Number of GPU', fontsize=18)
    ax1.set_ylabel('MLBUps', fontsize=18)
    ax2.set_xlabel('Number of GPU', fontsize=18)
    ax2.set_ylabel('MLBUps', fontsize=18)
    ax1.set_ylim(ymin=0)
    ax2.set_ylim(ymin=0, ymax=None)

    # ax1.set_title('Title', fontsize=14)
    ax1.set_xticks(np.arange(0, 13, 1))
    ax2.set_xticks(np.arange(0, 13, 1))
    ax1.grid(True)
    ax2.grid(True)
    fig.savefig('weak_scaling.png', dpi=600)


start = timeit.default_timer()
wd = os.getcwd()
path = os.path.join(wd, 'export_dataframe.csv')

if os.path.isfile(path):
    PlotCreator()
else:
    FileDataCreator()

t1 = float(timeit.default_timer() - start)
print("Czas :", str(t1))
