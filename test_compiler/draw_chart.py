import os
import matplotlib as mpl
from sympy import true
if os.environ.get('DISPLAY','') == '':
    print('no display found. Using non-interactive Agg backend')
    mpl.use('Agg')
import matplotlib.pyplot as plt
import argparse
import numpy as np
import matplotlib.ticker as mticker
import csv
import ast

plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
plt.rcParams.update({'font.size': 56})
gMarks1 = ['o','X','D','s','^','p']
gMarks2 = ['.','*','s','2','p','1','d','h']
gColors = ['lightcoral','orange','limegreen','cornflowerblue','gray','peru','teal','darkkhaki','slategray']
width = 35
height = 23
linewidth = 11 #default 1.5
markersize = 40

file_type='.png'

def draw_normal(title:str, fileName:str, data_list, label, average = False):
    plt.figure(figsize=(width,height))
    plt.title(title, y=1.03)
    x_value = np.arange(len(data_list[0]))
    plt.xticks(x_value)
    for data, c, m, l in zip(data_list, gColors, gMarks1, label):
        plt.plot(x_value, data, linestyle='--', marker=m, color=c, label=l,linewidth= linewidth, markersize=markersize)
    if average:
        np_data = np.array(data_list)
        avg = np.mean(np_data, axis=0)
        plt.plot(x_value, avg, linestyle='--', marker='d', color='violet', label='average', linewidth= linewidth, markersize=markersize)
        current_values = plt.gca().get_yticks()
        plt.gca().set_yticklabels(['{:,.0%}'.format(x) for x in current_values])
    # plt.legend(bbox_to_anchor=(1.0, 1.0), loc='lower center')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.08), ncol = 4)
    plt.xlabel(r'#$e_{extra}$')
    plt.grid(axis='y')
    # plt.margins(0.5)
    plt.savefig(fileName, dpi=300, bbox_inches='tight')


def draw_copmiler(filename, data):
    line_name = ["SABRE", r't$|$ket$\rangle$', "OLSQ", "TB-OLSQ"]
    for target in ["Fidelity", "Fidelity w/o Crosstalk", "Average Two-Qubit Gate Fidelity"]:
        Fidelity_list = [data["SABRE"][target], data["tket"][target], data["OLSQ"][target], data["TB-OLSQ"][target]]
        title = target
        new_fileName = 'fig/' + filename + '_' + target.replace(" ", "_").replace("/", "") + file_type
        draw_normal(title, new_fileName, Fidelity_list, line_name)

    for target in ["Fidelity improvement", "Fidelity Improvement w/o Crosstalk"]:
        Fidelity_list = [data["SABRE"][target], data["tket"][target], data["OLSQ"][target], data["TB-OLSQ"][target]]
        title = target
        new_fileName = 'fig/' + filename + '_' + target.replace(" ", "_").replace("/", "") + file_type
        draw_normal(title, new_fileName, Fidelity_list, line_name, True)



def get_info(title, csv_name, edge_num):
    data = {"D": [0] * edge_num, "Average Two-Qubit Gate Fidelity": [0] * edge_num, "Fidelity": [0] * edge_num, "Fidelity w/o Crosstalk": [0] * edge_num, "Fidelity improvement": [0] * edge_num, "Fidelity Improvement w/o Crosstalk": [0] * edge_num}
    with open(csv_name, 'r') as r:
        print(f"Processing {csv_name}")
        csvreader = csv.reader(r)
        header = []
        header = next(csvreader)
        if title == "SABRE":
            for row in csvreader:
                if row[1] == "sabre_lookahead":
                    e = ast.literal_eval(row[0])
                    data["Fidelity w/o Crosstalk"][e] = ast.literal_eval(row[2])
                    data["Fidelity"][e] = ast.literal_eval(row[3])
                    data["D"][e] = ast.literal_eval(row[6])
                    data["Average Two-Qubit Gate Fidelity"][e] = ast.literal_eval(row[10])
        elif title == "tket":
            for row in csvreader:
                e = ast.literal_eval(row[0])
                data["Fidelity w/o Crosstalk"][e] = ast.literal_eval(row[2])
                data["Fidelity"][e] = ast.literal_eval(row[3])
                data["D"][e] = ast.literal_eval(row[6])
                data["Average Two-Qubit Gate Fidelity"][e] = ast.literal_eval(row[10])
        elif title == "OLSQ":
            for row in csvreader:
                if row[1] == "normal":
                    e = ast.literal_eval(row[0])
                    data["Fidelity w/o Crosstalk"][e] = ast.literal_eval(row[2])
                    data["Fidelity"][e] = ast.literal_eval(row[3])
                    data["D"][e] = ast.literal_eval(row[6])
                    data["Average Two-Qubit Gate Fidelity"][e] = ast.literal_eval(row[10])
        elif title == "TB-OLSQ":
            for row in csvreader:
                if row[1] == "transition":
                    e = ast.literal_eval(row[0])
                    data["Fidelity w/o Crosstalk"][e] = ast.literal_eval(row[2])
                    data["Fidelity"][e] = ast.literal_eval(row[3])
                    data["D"][e] = ast.literal_eval(row[6])
                    data["Average Two-Qubit Gate Fidelity"][e] = ast.literal_eval(row[10])
    baseline = data["Fidelity"][0]
    for i, fid in enumerate(data["Fidelity"]):
        data["Fidelity improvement"][i] = (fid - baseline)/baseline
    
    for i, fid in enumerate(data["Fidelity w/o Crosstalk"]):
        data["Fidelity Improvement w/o Crosstalk"][i] = (fid - baseline)/baseline

    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Adding optional argument
    parser.add_argument("f", metavar='csv', type=str,
        help="list of csv file")
    parser.add_argument("type", metavar='type', type=str,
        help="compiler or architecture comparison")
    args = parser.parse_args()

    file_info = []
    with open(args.f, 'r') as f:
        file_info = f.readlines()
    
    split_info = file_info[0].split(',')
    # print(split_info)
    data = dict()
    for info in file_info[1:]:
        info_list = info.split(",")
        # print(info_list)
        if args.type == 'c':
            data[info_list[0]] = get_info(info_list[0], info_list[1].strip(), int(split_info[1])+1)
        elif args.type == 'a':
            raise ValueError("Invalid type")
        else:
            raise ValueError("Invalid type")
    
    # print(data)
    draw_copmiler(split_info[0], data)

    

