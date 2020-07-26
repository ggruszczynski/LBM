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
    pattern_local_size = re.compile(r'Local lattice size: (\d+)x(\d+)x(\d+)', re.I)
    # pattern_devices = re.compile(r'Selecting device', re.I)
    pattern_devices = re.compile(r'icm.edu.pl', re.I)
    pattern_time = re.compile(r'Total duration: (\d+\.\d+)', re.I)
    pattern_speed = re.compile(r'(\d+\.\d+) MLBUps', re.I)

    data_frame = pd.DataFrame(
        columns=['Name', 'Model', 'Nodes', 'Devices', 'Speed', 'Time', 'X', 'Y', 'Z', 'Total size', 'Local size'])
    for txtFile in glob1(results, "*.out"):
        dane = os.path.join(results, txtFile)
        with open(dane, "r") as f:
            content = f.read()

        # find data that fits to patterns
        matches_nodes = pattern_nodes.finditer(content)
        matches_model = pattern_model.finditer(content)
        matches_size = pattern_size.finditer(content)
        matches_local_size = pattern_local_size.finditer(content)
        matches_devices = pattern_devices.findall(content)
        matches_time = pattern_time.finditer(content)
        matches_speed = pattern_speed.finditer(content)

        # need to capture data to a list
        Name = txtFile
        Speed = np.mean(np.array([float(match.group(1)) for match in matches_speed])[-100:])
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

        Total_size = int(SizeX) * int(SizeY) * int(SizeZ)
        #Global_size = SizeX + "x" + SizeY + "x" + SizeZ

        for match in matches_local_size:
            LocalX = match.group(1)
            LocalY = match.group(2)
            LocalZ = match.group(3)

        Local_size = LocalX + "x" + LocalY + "x" + LocalZ

        # creating a list and pandas row to append to DataFrame
        to_append = [Name, Model, Node, Devices, Speed, Time, SizeX, SizeY, SizeZ, Total_size, Local_size]
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
    Filt_model = [(df1['Model'] == a) for a in F1]
    # For strong scaling
    x_uniq = df1['X'].unique().tolist()
    y_uniq = df1['Y'].unique().tolist()
    z_uniq = df1['Z'].unique().tolist()
    Filt_size_x = [(df1['X'] == i_x) for i_x in x_uniq]
    Filt_size_y = [(df1['Y'] == i_y) for i_y in y_uniq]
    Filt_size_z = [(df1['Z'] == i_z) for i_z in z_uniq]
    # For weak scaling
    size_uniq = df1['Local size'].unique().tolist()
    weak_filt = [df1['Local size'] == size for size in size_uniq]
    # for plot speedup(A/V)
    total_uniq = df1['Total size'].unique().tolist()
    Filt_total_size= [(df1['Total size'] == totalSize)  for totalSize in total_uniq]


    # Making Weak Scaling Plot
    a = 0
    for i in range(len(Filt_model)):
        for iter in range(len(weak_filt)):
            temp_df = df1.loc[Filt_model[i]].loc[weak_filt[iter]]
            if not temp_df.empty and len(temp_df['Devices']) > 2:
                a += 1
                x = temp_df['Devices']
                y = temp_df['Speed']
                name = temp_df['Model'].unique()
                local_size=str(temp_df['Local size'].unique().tolist()[0])
                make_plot_weak(x, y, name[0] + str(a), local_size)

    # Making Strong Scaling Plot
    a = 0
    for i in range(len(Filt_model)):
        for i_x in range(len(Filt_size_x)):
            for i_y in range(len(Filt_size_y)):
                for i_z in range(len(Filt_size_z)):
                    temp_df = df1.loc[Filt_model[i]].loc[Filt_size_x[i_x]].loc[Filt_size_y[i_y]].loc[Filt_size_z[i_z]]
                    if not temp_df.empty and len(temp_df['Devices']) > 2:
                        x = temp_df['Devices']
                        y = temp_df['Speed']
                        name = temp_df['Model'].unique()
                        global_size = str(temp_df['X'].unique().tolist()[0]) + 'x' + str(temp_df['Y'].unique().tolist()[0]) + 'x' + str(temp_df['Z'].unique().tolist()[0])
                        make_plot_strong(x, y, name[0] + str(a), global_size)
                        a += 1

    # Plot ghost layers
    for i in range(len(Filt_model)):
        for iter in range(len( Filt_total_size)):
            temp_df = df1.loc[Filt_model[i]].loc[weak_filt[iter]]
            if not temp_df.empty and len(temp_df['Devices']) > 2:
                x = temp_df['Devices']
                y = temp_df['Speed']
                name = temp_df['Model'].unique()
                total_size = str(temp_df['Total size'].unique().tolist()[0])
                make_plot_weak(x, y, name[0] , total_size)




def make_plot_weak(x, y, name, size):
    fig = plt.plot(x, y, 'gx')
    plt.title('Weak scaling ' + size, fontsize=32)
    plt.xlabel('Number of GPU', fontsize=24)
    plt.ylabel('MLBUps', fontsize=24)
    plt.ylim(ymin=0)
    plt.xticks(np.arange(0, max(x) + 1, 1.0))
    plt.grid(True)
    plt.savefig("Weak_scaling_" + name, dpi=600)
    plt.clf()


def make_plot_strong(x, y, name, size):
    fig = plt.plot(x, y, 'gx')
    plt.title('Strong scaling '+size, fontsize=32)
    plt.xlabel('Number of GPU', fontsize=24)
    plt.ylabel('MLBUps', fontsize=24)
    plt.ylim(ymin=0)
    plt.xticks(np.arange(0, max(x) + 1, 1.0))
    plt.grid(True)
    plt.savefig("Strong_scaling_" + name, dpi=600)
    plt.clf()

def make_plot_ghost(x, y, name, size):
    fig = plt.plot(x, y, 'gx')
    plt.title('Speedup in function of A/V'+size, fontsize=32)
    plt.xlabel('A/V', fontsize=24)
    plt.ylabel('MLBUps', fontsize=24)
    plt.ylim(ymin=0)
    plt.xticks(np.arange(0, max(x) + 1, 1.0))
    plt.grid(True)
    plt.savefig("Strong_scaling_" + name, dpi=600)
    plt.clf()

def __main__():
    start = timeit.default_timer()
    wd = os.getcwd()
    path = os.path.join(wd, 'export_dataframe.csv')
    if os.path.isfile(path):
        PlotCreator()
    else:
        FileDataCreator()

    t1 = float(timeit.default_timer() - start)
    print("Czas :", str(t1))


__main__()
