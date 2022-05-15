# python3 test_compiler/draw_chart.py draw_info/compiler_hh_qcnn_8.txt c      
import os
import matplotlib as mpl
from sympy import true
if os.environ.get('DISPLAY','') == '':
    print('no display found. Using non-interactive Agg backend')
    mpl.use('Agg')
import matplotlib.pyplot as plt
import argparse
import numpy as np
import csv
import ast

plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
plt.rcParams.update({'font.size': 50})
gMarks1 = ['o','X','D','s','^','p']
gMarks2 = ['.','*','s','2','p','1','d','h']
gColors = ['lightcoral','orange','limegreen','cornflowerblue','gray','peru','teal','darkkhaki','slategray']
width = 23
height = 12
linewidth = 8 #default 1.5
markersize = 20

file_type='.pdf'

def draw_normal(title:str, fileName:str, data_list, label, average = False, percentage = False):
    plt.figure(figsize=(width,height))
    # plt.title(title, y=1.03)
    x_value = np.arange(len(data_list[0]))
    plt.xticks(x_value)
    for data, c, m, l in zip(data_list, gColors, gMarks1, label):
        if len(data) != len(x_value):
            x_value = np.arange(len(data))
        plt.plot(x_value, data, linestyle='--', marker=m, color=c, label=l,linewidth= linewidth, markersize=markersize)
    if average:
        np_data = np.array(data_list)
        avg = np.mean(np_data, axis=0)
        plt.plot(x_value, avg, linestyle='--', marker='d', color='violet', label='average', linewidth= linewidth, markersize=markersize)
        current_values = plt.gca().get_yticks()
        plt.gca().set_yticklabels(['{:,.0%}'.format(x) for x in current_values])
    if percentage:
        current_values = plt.gca().get_yticks()
        plt.gca().set_yticklabels(['{:,.0%}'.format(x) for x in current_values])
    # plt.legend(bbox_to_anchor=(1.0, 1.0), loc='lower center')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.13), ncol = 4, frameon=False, columnspacing = 0.75, handletextpad = 0.2)
    plt.xlabel(r'#$e_{extra}$')
    plt.grid(axis='y')
    # plt.margins(0.5)
    plt.savefig(fileName, dpi=300, bbox_inches='tight')

def draw_normal_mix(fileName:str, data_list, data_list2, label, h_line = False):
    plt.figure(figsize=(width,height))
    # plt.title(title, y=1.03)
    x_value = np.arange(len(data_list[0]))
    plt.xticks(x_value)
    for data, data2, c, m, l in zip(data_list, data_list2, gColors, gMarks1, label):
        if len(data) != len(x_value):
            x_value = np.arange(len(data))
        plt.plot(x_value, data, linestyle='--', marker=m, color=c, label=l,linewidth= linewidth, markersize=markersize)
        plt.plot(x_value, data2, linestyle='--', alpha = 0.7, marker=m, color=c, linewidth= 0.65*linewidth, markersize=0.88*markersize)
        if h_line:
            plt.axhline(y=max(data), linestyle=':', linewidth= 0.65*linewidth)
            # x_ticks = np.append(plt.get_xticks(), max(data))
    # plt.legend(bbox_to_anchor=(1.0, 1.0), loc='lower center')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.13), ncol = 5, frameon=False, labelspacing = 0.025, handletextpad = 0.2)
    plt.xlabel(r'#$e_{extra}$')
    plt.grid(axis='y')
    # plt.margins(0.5)
    plt.savefig(fileName, dpi=300, bbox_inches='tight')

def draw_cross_test(ori_filename, data_list):
    filename = 'fig/' + ori_filename + '_fidelity_improvement' + file_type
    
    plt.figure(figsize=(width,height))
    # plt.title(title, y=1.03)
    x_value = np.arange(len(data_list["0"]["Fidelity improvement"]))
    plt.xticks(x_value)
    
    data = []
    for key, c, m in zip(data_list, gColors, gMarks1):
        data.append(data_list[key]["Fidelity improvement"])
        if len(data_list[key]["Fidelity improvement"]) != len(x_value):
            x_value = np.arange(len(data_list[key]["Fidelity improvement"]))
        plt.plot(x_value, data_list[key]["Fidelity improvement"], linestyle='--', marker=m, color=c, label=key,linewidth= linewidth, markersize=markersize)
    
    np_data = np.array(data)
    avg = np.mean(np_data, axis=0)
    plt.plot(x_value, avg, linestyle='--', marker='d', color='violet', label='average', linewidth= linewidth, markersize=markersize)
    current_values = plt.gca().get_yticks()
    plt.gca().set_yticklabels(['{:,.0%}'.format(x) for x in current_values])
    # plt.legend(bbox_to_anchor=(1.0, 1.0), loc='lower center')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.13), ncol = 8, frameon=False, columnspacing = 0.75, handletextpad = 0.2)
    plt.xlabel(r'#$e_{extra}$')
    plt.grid(axis='y')
    # plt.margins(0.5)
    plt.savefig(filename, dpi=300, bbox_inches='tight')

    filename = 'fig/' + ori_filename + '_fidelity_' + file_type
    
    plt.figure(figsize=(width,height))
    # plt.title(title, y=1.03)
    x_value = np.arange(len(data_list["0"]["Fidelity improvement"]))
    plt.xticks(x_value)
    
    data = []
    for key, c, m in zip(data_list, gColors, gMarks1):
        data.append(data_list[key]["Fidelity"])
        if len(data_list[key]["Fidelity"]) != len(x_value):
            x_value = np.arange(len(data_list[key]["Fidelity"]))
        plt.plot(x_value, data_list[key]["Fidelity"], linestyle='--', marker=m, color=c, label=key,linewidth= linewidth, markersize=markersize)
    # plt.legend(bbox_to_anchor=(1.0, 1.0), loc='lower center')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.13), ncol = 8, frameon=False, columnspacing = 0.75, handletextpad = 0.2)
    plt.xlabel(r'#$e_{extra}$')
    plt.grid(axis='y')
    # plt.margins(0.5)
    plt.savefig(filename, dpi=300, bbox_inches='tight')

def draw_copmiler(filename, data):
    line_name = ["OLSQ", "TB-OLSQ", r't$|$ket$\rangle$', "SABRE"]
    # for target in ["Fidelity", "Fidelity w/o Crosstalk", "Average Two-Qubit Gate Fidelity"]:
    for target in ["Average Two-Qubit Gate Fidelity"]:
        Fidelity_list = [data["OLSQ"][target], data["TB-OLSQ"][target], data["tket"][target], data["SABRE"][target]]
        title = target
        new_fileName = 'fig/' + filename + '_' + target.replace(" ", "_").replace("/", "") + file_type
        draw_normal(title, new_fileName, Fidelity_list, line_name)

    line_name = ["OLSQ", "TB-OLSQ", r't$|$ket$\rangle$']
    for target in ["Fidelity improvement", "Fidelity Improvement w/o Crosstalk"]:
        Fidelity_list = [data["OLSQ"][target], data["TB-OLSQ"][target], data["tket"][target]]
        title = target
        new_fileName = 'fig/' + filename + '_' + target.replace(" ", "_").replace("/", "") + file_type
        draw_normal(title, new_fileName, Fidelity_list, line_name, True)
    
    line_name = ["OLSQ", "TB-OLSQ", r't$|$ket$\rangle$', "SABRE"]
    Fidelity_list = [data["OLSQ"]["Fidelity"], data["TB-OLSQ"]["Fidelity"], data["tket"]["Fidelity"], data["SABRE"]["Fidelity"]]
    Fidelity_list2 = [data["OLSQ"]["Fidelity w/o Crosstalk"], data["TB-OLSQ"]["Fidelity w/o Crosstalk"], data["tket"]["Fidelity w/o Crosstalk"], data["SABRE"]["Fidelity w/o Crosstalk"]]
    new_fileName = 'fig/' + filename + '_mix_fidelity' + file_type
    draw_normal_mix(new_fileName, Fidelity_list, Fidelity_list2, line_name)


def draw_architecture(filename, data):
    line_name = ["Heavy-hexagon", "Grid"]
    # for target in ["Fidelity", "Fidelity w/o Crosstalk", "Average Two-Qubit Gate Fidelity"]:
    #     Fidelity_list = [data["hh"][target], data["grid"][target]]
    #     title = target
    #     new_fileName = 'fig/' + filename + '_' + target.replace(" ", "_").replace("/", "") + file_type
    #     draw_normal(title, new_fileName, Fidelity_list, line_name)
    
    # for target in ["Fidelity improvement", "Fidelity Improvement w/o Crosstalk"]:
    #     Fidelity_list = [data["hh"][target], data["grid"][target]]
    #     title = target
    #     new_fileName = 'fig/' + filename + '_' + target.replace(" ", "_").replace("/", "") + file_type
    #     draw_normal(title, new_fileName, Fidelity_list, line_name, False, True)

    Fidelity_list = [data["hh"]["Fidelity"], data["grid"]["Fidelity"]]
    Fidelity_list2 = [data["hh"]["Fidelity w/o Crosstalk"], data["grid"]["Fidelity w/o Crosstalk"]]
    new_fileName = 'fig/' + filename + '_mix_fidelity' + file_type
    draw_normal_mix(new_fileName, Fidelity_list, Fidelity_list2, line_name, True)

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
        else:
            for row in csvreader:
                # print("hi")
                if row[1] == "normal":
                    # print(row[0])
                    # print(row[1])
                    # print(row[3])
                    e = ast.literal_eval(row[0])
                    data["Fidelity w/o Crosstalk"][e] = ast.literal_eval(row[2])
                    data["Fidelity"][e] = ast.literal_eval(row[3])
                    data["D"][e] = ast.literal_eval(row[6])
                    data["Average Two-Qubit Gate Fidelity"][e] = ast.literal_eval(row[10])
    baseline = data["Fidelity"][0]
    # print(data["Fidelity"][0])
    for i, fid in enumerate(data["Fidelity"]):
        data["Fidelity improvement"][i] = (fid - baseline)/baseline
    
    baseline = data["Fidelity w/o Crosstalk"][0]
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
    if args.type == 'c' or args.type == 't' :
        for info in file_info[1:]:
            info_list = info.split(",")
            data[info_list[0]] = get_info(info_list[0], info_list[1].strip(), int(split_info[1])+1)
        # print(info_list)    
    elif args.type == 'a':
        info_list = file_info[1].split(",")
        data[info_list[0]] = get_info("OLSQ", info_list[1].strip(), int(split_info[1])+1)
        info_list = file_info[2].split(",")
        data[info_list[0]] = get_info("OLSQ", info_list[1].strip(), int(split_info[2])+1)
    else:
        raise ValueError("Invalid type")
    
    # print(data)
    if args.type == 'c':
        draw_copmiler(split_info[0], data)
    elif args.type == 'a':
        draw_architecture(split_info[0], data)
    elif args.type == 't':
        draw_cross_test(split_info[0], data)
    else:
        raise ValueError("Invalid type")    

    

    # line_name = ["OLSQ", "TB-OLSQ", r't$|$ket$\rangle$']
    # for target in ["Fidelity improvement"]:
    #     Fidelity_list = [data["OLSQ"][target], data["TB-OLSQ"][target], data["tket"][target]]
    #     title = target
    #     np_data = np.array(Fidelity_list)
    #     avg = np.mean(np_data, axis=0)
        # print(avg)